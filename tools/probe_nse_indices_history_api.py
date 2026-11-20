#!/usr/bin/env python3
"""Validate the official NSE India historical-index API route used by the website."""
import json
from datetime import datetime, timezone
from pathlib import Path
import requests

BASE = "https://www.nseindia.com"
PAGE = BASE + "/reports-indices-historical-index-data"
API = BASE + "/api/historical/indicesHistory"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": PAGE,
    "Origin": BASE,
    "Connection": "keep-alive",
}
s = requests.Session()
page = s.get(PAGE, headers=headers, timeout=(15, 40))
page.raise_for_status()
params = {"indexType": "NIFTY 50", "from": "21-10-2026", "to": "19-11-2026"}
r = s.get(API, params=params, headers=headers, timeout=(15, 60))
result = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "page_url": page.url, "page_status": page.status_code,
    "api_url": r.url, "api_status": r.status_code,
    "content_type": r.headers.get("Content-Type"),
    "response_prefix": r.text[:5000],
}
try:
    data = r.json()
    result["json_type"] = type(data).__name__
    if isinstance(data, dict):
        result["keys"] = list(data.keys())
        rows = data.get("data", [])
    else:
        rows = data
    result["row_count"] = len(rows) if isinstance(rows, list) else None
    result["sample_rows"] = rows[:5] if isinstance(rows, list) else rows
except Exception as exc:
    result["json_error"] = f"{type(exc).__name__}: {exc}"
out = Path("artifacts")
out.mkdir(exist_ok=True)
path = out / "nse-indices-history-api-probe.json"
path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"NSE indices page HTTP {page.status_code}; API HTTP {r.status_code}; rows={result.get('row_count')}; content={result['content_type']}")
print(result.get("sample_rows", result.get("json_error", result["response_prefix"][:1000])))
print(f"Saved {path}")
