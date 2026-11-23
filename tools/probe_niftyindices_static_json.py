#!/usr/bin/env python3
"""Probe the official NSE Indices historical JSON asset referenced by its page JavaScript."""
import json
from datetime import datetime, timezone
from pathlib import Path
import requests

URL = "https://liveindexsa.niftyindices.com/assets/json/HistoricalData.json"
headers = {
    "User-Agent": "Mozilla/5.0 (compatible; NIFTY-Seller-Intelligence-Audit/1.0)",
    "Accept": "application/json,*/*",
    "Referer": "https://www.niftyindices.com/reports/historical-data",
}
r = requests.get(URL, headers=headers, timeout=60)
result = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "url": URL,
    "http_status": r.status_code,
    "content_type": r.headers.get("Content-Type"),
    "content_length": len(r.content),
    "prefix": r.text[:4000],
}
try:
    data = r.json()
    result["json_type"] = type(data).__name__
    result["row_count"] = len(data) if hasattr(data, "__len__") else None
    if isinstance(data, list):
        result["sample_rows"] = data[:5]
        result["nifty50_rows"] = [x for x in data if "NIFTY 50" in json.dumps(x).upper()][:5]
except Exception as exc:
    result["json_error"] = f"{type(exc).__name__}: {exc}"
out = Path("artifacts")
out.mkdir(exist_ok=True)
path = out / "niftyindices-static-json-probe.json"
path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"Static historical JSON HTTP {r.status_code}, type={result.get('json_type')}, rows={result.get('row_count')}, bytes={len(r.content)}")
print(f"NIFTY 50 matches={len(result.get('nifty50_rows', []))}; saved {path}")
