#!/usr/bin/env python3
"""Download and verify the preserved Phase 1 archive from private Backblaze B2."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath

import boto3

ARCHIVE_PREFIX = "nifty-seller-intelligence/phase1/2026-11-23/phase1-nse-fo-index-download-and-diagnostics"
TRANSFER_MANIFEST_KEY = f"{ARCHIVE_PREFIX}/b2-upload-manifest.json"
EXPECTED_ARTIFACT_ID = 14688805993
EXPECTED_WORKFLOW_RUN_ID = 44858251380
EXPECTED_ARTIFACT_SHA256 = "f1f8ca45a0e122846d9e0c73d8dacb97d53e3fc21c50d74de14e531865cf8a4"
EXPECTED_OBJECTS = 78
EXPECTED_RAW_FILES = 68


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    required = (
        "B2_ENDPOINT_URL", "B2_REGION", "B2_BUCKET_NAME",
        "B2_APPLICATION_KEY_ID", "B2_APPLICATION_KEY",
    )
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise RuntimeError("Missing required B2 environment settings: " + ", ".join(missing))

    root = Path(os.environ.get("PHASE1_ARTIFACT_DIR", "local_data")).resolve()
    root.mkdir(parents=True, exist_ok=True)
    client = boto3.client(
        "s3",
        endpoint_url=os.environ["B2_ENDPOINT_URL"],
        region_name=os.environ["B2_REGION"],
        aws_access_key_id=os.environ["B2_APPLICATION_KEY_ID"],
        aws_secret_access_key=os.environ["B2_APPLICATION_KEY"],
    )
    bucket = os.environ["B2_BUCKET_NAME"]
    client.head_bucket(Bucket=bucket)

    response = client.get_object(Bucket=bucket, Key=TRANSFER_MANIFEST_KEY)
    manifest_bytes = response["Body"].read()
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    if response.get("Metadata", {}).get("sha256") != manifest_hash:
        raise RuntimeError("B2 transfer-manifest SHA-256 metadata does not match its content.")
    transfer = json.loads(manifest_bytes)

    source = transfer.get("source", {})
    if (
        source.get("artifact_id") != EXPECTED_ARTIFACT_ID
        or source.get("workflow_run_id") != EXPECTED_WORKFLOW_RUN_ID
        or source.get("artifact_zip_sha256") != EXPECTED_ARTIFACT_SHA256
    ):
        raise RuntimeError("B2 transfer manifest does not identify the approved Phase 1 artifact.")
    objects = transfer.get("objects")
    if transfer.get("uploaded_files") != EXPECTED_OBJECTS or not isinstance(objects, list) or len(objects) != EXPECTED_OBJECTS:
        raise RuntimeError("B2 transfer manifest does not contain the expected 78 preserved objects.")
    if transfer.get("raw_source_files_verified") != EXPECTED_RAW_FILES:
        raise RuntimeError("B2 transfer manifest does not confirm 68 verified raw source files.")
    if transfer.get("audit_checks_passed") != 15 or transfer.get("audit_checks_total") != 15:
        raise RuntimeError("B2 transfer manifest does not confirm the Phase 1 15/15 audit.")

    seen: set[str] = set()
    total_bytes = 0
    raw_count = 0
    for item in objects:
        key = item.get("key", "")
        if not item.get("verified") or not key.startswith(ARCHIVE_PREFIX + "/"):
            raise RuntimeError(f"Unverified or out-of-prefix B2 object in transfer manifest: {key}")
        relative = key[len(ARCHIVE_PREFIX) + 1:]
        rel_path = PurePosixPath(relative)
        if rel_path.is_absolute() or not rel_path.parts or any(part in ("", ".", "..") for part in rel_path.parts):
            raise RuntimeError(f"Unsafe relative path in B2 transfer manifest: {relative}")
        if relative in seen:
            raise RuntimeError(f"Duplicate B2 object path in transfer manifest: {relative}")
        seen.add(relative)

        destination = (root / Path(*rel_path.parts)).resolve()
        if destination != root and root not in destination.parents:
            raise RuntimeError(f"Resolved B2 object path escapes archive root: {relative}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        client.download_file(bucket, key, str(destination))

        expected_size = int(item["bytes"])
        expected_hash = str(item["sha256"]).lower()
        actual_size = destination.stat().st_size
        actual_hash = sha256_file(destination)
        if actual_size != expected_size or actual_hash != expected_hash:
            raise RuntimeError(f"Downloaded B2 object failed size/SHA-256 verification: {relative}")
        total_bytes += actual_size
        raw_count += int(relative.startswith("raw/"))

    if len(seen) != EXPECTED_OBJECTS or raw_count != EXPECTED_RAW_FILES:
        raise RuntimeError(f"Unexpected downloaded inventory: objects={len(seen)}, raw={raw_count}")
    print(f"Verified {len(seen)} B2 objects ({raw_count} raw source files), {total_bytes} bytes.")
    print("Approved Phase 1 artifact identity, source hashes and 15/15 audit provenance confirmed.")


if __name__ == "__main__":
    main()
