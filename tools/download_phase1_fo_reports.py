#!/usr/bin/env python3
"""Download official NSE F&O reports for the Phase 1 candidate sessions.

Only the published NSE archives are requested. Original response bytes are saved
unchanged, with SHA-256, response metadata and explicit missing/error states.
No market data is committed to Git or uploaded to production storage.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path("artifacts/raw/nse")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NIFTY-Seller-Intelligence-Phase1/1.0)",
    "Accept": "application/zip,application/gzip,application/octet-stream,*/*",
    "Referer": "https://www.nseindia.com/",
}
# 22-session candidate list ending 19-Nov-2026, including special Muhurat date.
SESSION_DATES = [
    "20261021","20261022","20261023","20261026","20261027","20261028","20261029","20261030",
    "20261102","20261103","20261104","20261105","20261106","20261108","20261109","20261111",
    "20261112","20261113","20261116","20261117","20261118","20261119",
]
# Only used if 08-Nov does not have actual F&O reports; it may complete 22 regular sessions.
FALLBACK_DATE = "20261019"
BASE = "https://archives.nseindia.com/content/fo"
session = requests.Session()
session.headers.update(HEADERS)

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def fetch(url: str, path: Path, kind: str) -> dict:
    item = {"url": url, "path": str(path), "kind": kind, "status": "NOT_ATTEMPTED"}
    try:
        response = session.get(url, timeout=(20, 90), stream=True)
        data = response.content
        item.update(http_status=response.status_code, content_type=response.headers.get("Content-Type"),
                    bytes=len(data), final_url=response.url)
        if response.status_code != 200:
            item["status"] = "MISSING_OR_HTTP_ERROR"
            item["response_prefix"] = data[:160].decode("utf-8", "replace")
            return item
        if kind == "fo_bhavcopy":
            if not data.startswith(b"PK"):
                item["status"] = "INVALID_NOT_ZIP"
                item["response_prefix"] = data[:160].decode("utf-8", "replace")
                return item
            import io
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                csvs = [n for n in zf.namelist() if n.lower().endswith(".csv")]
                if len(csvs) != 1:
                    item["status"] = "INVALID_ZIP_CONTENTS"
                    item["csv_members"] = csvs
                    return item
                item["csv_member"] = csvs[0]
                with zf.open(csvs[0]) as f:
                    item["columns"] = next(csv.reader([f.readline().decode("utf-8-sig", "replace")]))
        else:
            if not data.startswith(b"\x1f\x8b"):
                item["status"] = "INVALID_NOT_GZIP"
                item["response_prefix"] = data[:160].decode("utf-8", "replace")
                return item
            import io
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as f:
                first = f.readline().decode("utf-8-sig", "replace")
                item["columns"] = next(csv.reader([first]))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        item.update(status="DOWNLOADED", sha256=digest(data))
        return item
    except Exception as exc:
        item.update(status="DOWNLOAD_ERROR", error=f"{type(exc).__name__}: {exc}")
        return item

results = []
dates = SESSION_DATES + [FALLBACK_DATE]
for ymd in dates:
    dt = datetime.strptime(ymd, "%Y%m%d")
    dmy = dt.strftime("%d%m%Y")
    stamp = dt.strftime("%d%m%Y")
    bh_name = f"BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv.zip"
    cm_name = f"NSE_FO_contract_{stamp}.csv.gz"
    bh_url = f"{BASE}/{bh_name}"
    cm_url = f"{BASE}/{cm_name}"
    bh = fetch(bh_url, ROOT / "fo_bhavcopy" / bh_name, "fo_bhavcopy")
    cm = fetch(cm_url, ROOT / "mii_contracts" / cm_name, "mii_contract")
    results.append({"date": dt.strftime("%Y-%m-%d"), "is_fallback": ymd == FALLBACK_DATE,
                    "bhavcopy": bh, "mii_contract": cm})
    print(f"{dt:%Y-%m-%d}: bhavcopy={bh['status']} ({bh.get('http_status')}) "
          f"mii={cm['status']} ({cm.get('http_status')})")
    time.sleep(0.25)

report = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "source": "https://archives.nseindia.com/content/fo/",
    "candidate_sessions": SESSION_DATES,
    "fallback_date_if_muhurat_unavailable": FALLBACK_DATE,
    "results": results,
}
out = Path("artifacts/manifests")
out.mkdir(parents=True, exist_ok=True)
(out / "fo-download-manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(f"Manifest written: {out / 'fo-download-manifest.json'}")
