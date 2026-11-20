#!/usr/bin/env python3
"""Probe the official NSE Indices historical-data POST used by its public page."""
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE = "https://www.niftyindices.com/reports/historical-data"
ENDPOINT = "https://www.niftyindices.com/BackPage/getHistoricaldatatabletoString"
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (compatible; NIFTY-Seller-Intelligence-Audit/1.0)",
    "Accept": "application/json, text/plain, */*",
    "Referer": BASE,
    "Origin": "https://www.niftyindices.com",
}
page = session.get(BASE, headers=headers, timeout=45)
page.raise_for_status()
cinfo = "{'name':'NIFTY 50','startDate':'01-11-2026','endDate':'19-11-2026','indexName':'NIFTY 50'}"
response = session.post(ENDPOINT, headers={**headers, "Content-Type": "application/json; charset=utf-8",
                                           "X-Requested-With": "XMLHttpRequest"},
                        json={"cinfo": cinfo}, timeout=60)
result = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "page_status": page.status_code,
    "endpoint": ENDPOINT,
    "request_cinfo": cinfo,
    "http_status": response.status_code,
    "content_type": response.headers.get("Content-Type"),
    "content_length": response.headers.get("Content-Length"),
    "response_text_prefix": response.text[:5000],
}
out = Path("artifacts")
out.mkdir(exist_ok=True)
path = out / "niftyindices-api-probe.json"
path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"Index history endpoint HTTP {response.status_code}; content-type={result['content_type']}; bytes={len(response.content)}")
print(result["response_text_prefix"][:1200])
print(f"Saved {path}")
