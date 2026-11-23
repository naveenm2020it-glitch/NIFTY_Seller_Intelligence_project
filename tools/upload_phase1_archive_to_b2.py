#!/usr/bin/env python3
"""Verify and preserve the Phase 1 NSE audit artifact in private Backblaze B2.

Uploads the complete extracted GitHub Actions artifact (raw source files,
manifests, audit outputs and diagnostics) without modifying or deleting source
objects. Every uploaded object is verified with HeadObject after upload.
"""
from __future__ import annotations

import hashlib
import json
import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path

import boto3

ARTIFACT_DIR = Path(os.environ.get("PHASE1_ARTIFACT_DIR", "phase1-artifact"))
EXPECTED_RAW_FILES = 68
EXPECTED_ARTIFACT_FILES = 78
EXPECTED_AUDIT_CHECKS = 15


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def manifest_path(value: str) -> str:
    prefix = "artifacts/"
    if not value.startswith(prefix):
        raise ValueError(f"Unexpected manifest path: {value}")
    return value[len(prefix):]


def verify_source_artifact() -> list[Path]:
    fo_manifest = load_json(ARTIFACT_DIR / "manifests/fo-download-manifest.json")
    index_manifest = load_json(ARTIFACT_DIR / "manifests/nifty50-download-manifest.json")
    audit = load_json(ARTIFACT_DIR / "audit/phase1-fo-audit-summary.json")

    checks = audit.get("checks", {})
    if audit.get("passed_checks") != EXPECTED_AUDIT_CHECKS or audit.get("total_checks") != EXPECTED_AUDIT_CHECKS:
        raise ValueError("Phase 1 audit summary does not report 15/15 passed checks")
    if len(checks) != EXPECTED_AUDIT_CHECKS or not all(value is True for value in checks.values()):
        raise ValueError("One or more Phase 1 audit assertions are not true")

    expected: dict[str, tuple[str, int]] = {}
    for result in fo_manifest.get("results", []):
        for field in ("bhavcopy", "mii_contract"):
            entry = result.get(field) or {}
            if entry.get("status") != "DOWNLOADED":
                raise ValueError(f"F&O source was not downloaded: {result.get('date')} {field}")
            expected[manifest_path(entry["path"])] = (entry["sha256"], int(entry["bytes"]))

    for entry in index_manifest.get("results", []):
        if entry.get("status") != "DOWNLOADED" or entry.get("date_matches") is not True:
            raise ValueError(f"NIFTY 50 index source is missing or date-mismatched: {entry.get('date')}")
        expected[manifest_path(entry["path"])] = (entry["sha256"], int(entry["bytes"]))

    raw_files = {p.relative_to(ARTIFACT_DIR).as_posix(): p for p in (ARTIFACT_DIR / "raw").rglob("*") if p.is_file()}
    if len(raw_files) != EXPECTED_RAW_FILES:
        raise ValueError(f"Expected {EXPECTED_RAW_FILES} raw source files; found {len(raw_files)}")
    if set(raw_files) != set(expected):
        missing = sorted(set(expected) - set(raw_files))
        extra = sorted(set(raw_files) - set(expected))
        raise ValueError(f"Manifest/raw-file inventory mismatch; missing={missing}; extra={extra}")

    for rel, (expected_hash, expected_size) in expected.items():
        path = raw_files[rel]
        actual_size = path.stat().st_size
        actual_hash = sha256_file(path)
        if actual_size != expected_size or actual_hash != expected_hash:
            raise ValueError(f"Source manifest verification failed: {rel}")

    files = sorted(p for p in ARTIFACT_DIR.rglob("*") if p.is_file())
    if len(files) != EXPECTED_ARTIFACT_FILES:
        raise ValueError(f"Expected {EXPECTED_ARTIFACT_FILES} artifact files; found {len(files)}")
    print(f"Verified {len(raw_files)} raw source files against manifests; Phase 1 audit is 15/15.")
    print(f"Preserving all {len(files)} artifact files, including audit reports and diagnostics.")
    return files


def main() -> None:
    required = [
        "B2_ENDPOINT_URL", "B2_REGION", "B2_BUCKET_NAME",
        "B2_APPLICATION_KEY_ID", "B2_APPLICATION_KEY",
    ]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise RuntimeError("Missing required GitHub Actions secrets: " + ", ".join(missing))

    source_artifact_id = os.environ.get("SOURCE_ARTIFACT_ID", "14688805993")
    source_artifact_sha256 = os.environ.get("SOURCE_ARTIFACT_SHA256", "")
    if not source_artifact_sha256:
        raise RuntimeError("SOURCE_ARTIFACT_SHA256 is required")

    files = verify_source_artifact()
    bucket = os.environ["B2_BUCKET_NAME"]
    prefix = os.environ.get("B2_PREFIX", "nifty-seller-intelligence/phase1/2026-11-23").strip("/")
    client = boto3.client(
        "s3",
        endpoint_url=os.environ["B2_ENDPOINT_URL"],
        region_name=os.environ["B2_REGION"],
        aws_access_key_id=os.environ["B2_APPLICATION_KEY_ID"],
        aws_secret_access_key=os.environ["B2_APPLICATION_KEY"],
    )

    # Read-only preflight. Uploads are additive/overwrite-identical at a stable prefix;
    # this script never deletes objects or changes bucket policy/ACLs.
    client.head_bucket(Bucket=bucket)
    uploaded = []
    for path in files:
        relative = path.relative_to(ARTIFACT_DIR).as_posix()
        key = f"{prefix}/phase1-nse-fo-index-download-and-diagnostics/{relative}"
        digest = sha256_file(path)
        size = path.stat().st_size
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        client.upload_file(
            str(path),
            bucket,
            key,
            ExtraArgs={"Metadata": {"sha256": digest}, "ContentType": content_type},
        )
        head = client.head_object(Bucket=bucket, Key=key)
        metadata_hash = head.get("Metadata", {}).get("sha256")
        if int(head.get("ContentLength", -1)) != size or metadata_hash != digest:
            raise RuntimeError(f"B2 post-upload verification failed: {key}")
        uploaded.append({
            "key": key,
            "bytes": size,
            "sha256": digest,
            "verified": True,
        })
        print(f"Verified B2 object: {key} ({size} bytes)")

    transfer_manifest = {
        "purpose": "Immutable preservation copy of the completed Phase 1 NSE EOD audit artifact",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "repository": "naveenm2020it-glitch/NIFTY_Seller_Intelligence_project",
            "workflow_run_id": 44858251380,
            "artifact_id": int(source_artifact_id),
            "artifact_name": "phase1-nse-fo-index-download-and-diagnostics",
            "artifact_zip_sha256": source_artifact_sha256,
        },
        "destination": {"provider": "Backblaze B2 S3-compatible API", "bucket": bucket, "prefix": prefix},
        "raw_source_files_verified": EXPECTED_RAW_FILES,
        "audit_checks_passed": EXPECTED_AUDIT_CHECKS,
        "audit_checks_total": EXPECTED_AUDIT_CHECKS,
        "uploaded_files": len(uploaded),
        "uploaded_bytes": sum(item["bytes"] for item in uploaded),
        "objects": uploaded,
    }
    manifest_bytes = json.dumps(transfer_manifest, indent=2).encode("utf-8")
    manifest_key = f"{prefix}/phase1-nse-fo-index-download-and-diagnostics/b2-upload-manifest.json"
    import tempfile
    with tempfile.NamedTemporaryFile(prefix="b2-upload-manifest-", suffix=".json", delete=False) as tmp:
        tmp.write(manifest_bytes)
        temp_path = Path(tmp.name)
    try:
        manifest_hash = sha256_file(temp_path)
        client.upload_file(
            str(temp_path), bucket, manifest_key,
            ExtraArgs={"Metadata": {"sha256": manifest_hash}, "ContentType": "application/json"},
        )
    finally:
        temp_path.unlink(missing_ok=True)
    head = client.head_object(Bucket=bucket, Key=manifest_key)
    if int(head.get("ContentLength", -1)) != len(manifest_bytes) or head.get("Metadata", {}).get("sha256") != manifest_hash:
        raise RuntimeError("B2 transfer manifest post-upload verification failed")

    print("B2_ARCHIVE_UPLOAD_SUCCESS")
    print(f"Bucket: {bucket}")
    print(f"Prefix: {prefix}/phase1-nse-fo-index-download-and-diagnostics/")
    print(f"Verified objects: {len(uploaded)} data/report files + 1 transfer manifest")
    print(f"Verified bytes: {sum(item['bytes'] for item in uploaded)}")


if __name__ == "__main__":
    main()
