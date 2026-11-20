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
URL = "https://nsearchives.nseindia.com/content/indices/ind_close_all_{ddmmyyyy}.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36",
    "Accept": "text/csv,application/csv,application/octet-stream,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/all-reports",
    "Origin": "https://www.nseindia.com",
}
s = requests.Session()
s.headers.update(HEADERS)
results = []
for ymd in DATES:
    dt = datetime.strptime(ymd, "%Y%m%d")
    dmy = dt.strftime("%d%m%Y")
    name = f"ind_close_all_{dmy}.csv"
    url = URL.format(ddmmyyyy=dmy)
    item = {"date": dt.strftime("%Y-%m-%d"), "url": url, "filename": name}
    try:
        r = s.get(url, timeout=(15, 60))
        data = r.content
        item.update(http_status=r.status_code, final_url=r.url, content_type=r.headers.get("Content-Type"),
                    bytes=len(data))
        if r.status_code != 200:
            item.update(status="MISSING_OR_HTTP_ERROR", response_prefix=data[:120].decode("utf-8","replace"))
        else:
            text = data.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
            rows = list(reader)
            item["columns"] = reader.fieldnames
            # Normalize header spacing/case but retain source CSV unchanged.
            def norm(x): return "".join(ch.lower() for ch in (x or "") if ch.isalnum())
            index_col = next((c for c in reader.fieldnames or [] if norm(c) in {"indexname","index"}), None)
            date_col = next((c for c in reader.fieldnames or [] if norm(c) in {"indexdate","date"}), None)
            row = next((x for x in rows if "nifty 50" == (x.get(index_col,"").strip().lower() if index_col else "")), None)
            item["row_count"] = len(rows)
            if row is None:
                item.update(status="NO_NIFTY50_ROW", index_column=index_col)
            else:
                item["nifty50_row"] = row
                item["index_column"] = index_col
                item["index_date_column"] = date_col
                expected = dt.strftime("%d-%b-%Y").lower()
                actual = (row.get(date_col,"").strip().lower() if date_col else "")
                item["date_matches"] = actual in {expected, dt.strftime("%d-%m-%Y").lower(), dt.strftime("%Y-%m-%d")}
                if not all(any(norm(c) == target for c in reader.fieldnames or []) for target in
                           ["openindexvalue","highindexvalue","lowindexvalue","closingindexvalue"]):
                    item["status"] = "MISSING_REQUIRED_OHLC_COLUMNS"
                else:
                    path = ROOT / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                    item.update(status="DOWNLOADED", sha256=hashlib.sha256(data).hexdigest(), path=str(path))
        print(f"{item['date']}: {item.get('status')} HTTP={item.get('http_status')} rows={item.get('row_count')}")
    except Exception as exc:
        item.update(status="DOWNLOAD_ERROR", error=f"{type(exc).__name__}: {exc}")
        print(f"{item['date']}: DOWNLOAD_ERROR {item['error']}")
    results.append(item)
    time.sleep(1.0)

out = Path("artifacts/manifests")
out.mkdir(parents=True, exist_ok=True)
manifest = {"generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source": "NSE official All Indices daily-close archive",
            "url_pattern": URL, "results": results}
(out / "nifty50-download-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(f"Downloaded {sum(x.get('status') == 'DOWNLOADED' for x in results)}/{len(results)} NIFTY 50 index CSVs")
