#!/usr/bin/env python3
"""Download official NSE All Indices daily-close CSVs and extract NIFTY 50 OHLC."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

DATES = [
    "20261021","20261022","20261023","20261026","20261027","20261028","20261029","20261030",
    "20261102","20261103","20261104","20261105","20261106","20261108","20261109","20261111",
    "20261112","20261113","20261116","20261117","20261118","20261119",
]
ROOT = Path("artifacts/raw/nse/nifty50_ohlc")
HOSTS = ["https://archives.nseindia.com", "https://nsearchives.nseindia.com"]
PATH = "/content/indices/ind_close_all_{ddmmyyyy}.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36",
    "Accept": "text/csv,application/csv,application/octet-stream,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/all-reports",
    "Origin": "https://www.nseindia.com",
}
s = requests.Session()
s.headers.update(HEADERS)

def norm(value):
    return "".join(ch.lower() for ch in (value or "") if ch.isalnum())

results = []
for ymd in DATES:
    dt = datetime.strptime(ymd, "%Y%m%d")
    dmy = dt.strftime("%d%m%Y")
    name = f"ind_close_all_{dmy}.csv"
    item = {"date": dt.strftime("%Y-%m-%d"), "filename": name}
    attempts = []
    for host in HOSTS:
        url = host + PATH.format(ddmmyyyy=dmy)
        try:
            r = s.get(url, timeout=(8, 25))
            data = r.content
            attempt = {"url": url, "http_status": r.status_code, "final_url": r.url,
                       "content_type": r.headers.get("Content-Type"), "bytes": len(data)}
            if r.status_code == 200:
                try:
                    text = data.decode("utf-8-sig")
                    reader = csv.DictReader(io.StringIO(text))
                    rows = list(reader)
                    columns = reader.fieldnames or []
                    index_col = next((c for c in columns if norm(c) in {"indexname", "index"}), None)
                    date_col = next((c for c in columns if norm(c) in {"indexdate", "date"}), None)
                    row = next((x for x in rows if "nifty 50" == (x.get(index_col, "").strip().lower() if index_col else "")), None)
                    attempt["columns"] = columns
                    attempt["row_count"] = len(rows)
                    if row is not None:
                        required = ["openindexvalue", "highindexvalue", "lowindexvalue", "closingindexvalue"]
                        if all(any(norm(c) == target for c in columns) for target in required):
                            path = ROOT / name
                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.write_bytes(data)
                            item.update(status="DOWNLOADED", url=url, final_url=r.url,
                                        content_type=r.headers.get("Content-Type"), bytes=len(data),
                                        sha256=hashlib.sha256(data).hexdigest(), path=str(path),
                                        columns=columns, row_count=len(rows), nifty50_row=row,
                                        index_date_column=date_col,
                                        date_matches=(row.get(date_col, "").strip().lower() in {
                                            dt.strftime("%d-%b-%Y").lower(),
                                            dt.strftime("%d-%m-%Y").lower(),
                                            dt.strftime("%Y-%m-%d")
                                        } if date_col else False))
                            attempts.append(attempt)
                            break
                        attempt["error"] = "NIFTY 50 row found but required OHLC columns missing"
                    else:
                        attempt["error"] = "NIFTY 50 row not found"
                except Exception as exc:
                    attempt["error"] = f"CSV parse: {type(exc).__name__}: {exc}"
            else:
                attempt["error"] = data[:120].decode("utf-8", "replace")
            attempts.append(attempt)
        except Exception as exc:
            attempts.append({"url": url, "error": f"{type(exc).__name__}: {exc}"})
        if item.get("status") == "DOWNLOADED":
            break
    if item.get("status") != "DOWNLOADED":
        item.update(status="MISSING_OR_INVALID")
    item["attempts"] = attempts
    results.append(item)
    print(f"{item['date']}: {item['status']} source={item.get('url')} row_count={item.get('row_count')}")
    time.sleep(0.5)

out = Path("artifacts/manifests")
out.mkdir(parents=True, exist_ok=True)
manifest = {"generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source": "NSE official All Indices daily-close archive",
            "url_pattern": [host + PATH for host in HOSTS], "results": results}
(out / "nifty50-download-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
count = sum(x.get("status") == "DOWNLOADED" for x in results)
print(f"Downloaded {count}/{len(results)} NIFTY 50 index CSVs")
