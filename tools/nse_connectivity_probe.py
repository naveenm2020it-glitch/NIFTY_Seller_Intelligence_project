#!/usr/bin/env python3
"""Read-only connectivity probe for official NSE/NSE Indices historical data sources.

This probe does not bypass access controls, mutate remote systems, or persist market data.
It records DNS and HTTP reachability for the official report pages and dated NSE archive
URL patterns so the acquisition method can be selected from observed responses.
"""
from __future__ import annotations

import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

OUT = Path("artifacts")
OUT.mkdir(exist_ok=True)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NIFTY-Seller-Intelligence-Audit/1.0)",
    "Accept": "text/html,application/zip,application/gzip,text/csv,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}
SOURCES = [
    {
        "name": "NSE All Reports",
        "url": "https://www.nseindia.com/all-reports",
        "kind": "official_landing_page",
    },
    {
        "name": "NSE F&O UDiFF Bhavcopy sample (2026-10-22)",
        "url": "https://archives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_20261022_F_0000.csv.zip",
        "kind": "official_archive_candidate",
    },
    {
        "name": "NSE F&O MII Contract sample (2026-10-22)",
        "url": "https://archives.nseindia.com/content/fo/NSE_FO_contract_22102026.csv.gz",
        "kind": "official_archive_candidate",
    },
    {
        "name": "NSE Indices Historical Data",
        "url": "https://www.niftyindices.com/reports/historical-data",
        "kind": "official_landing_page",
    },
]

def probe(item: dict) -> dict:
    url = item["url"]
    host = urlparse(url).hostname
    result = {**item, "host": host, "dns": [], "http_status": None,
              "final_url": None, "content_type": None, "content_length": None,
              "error": None}
    try:
        result["dns"] = sorted({entry[4][0] for entry in socket.getaddrinfo(host, 443)})
    except Exception as exc:
        result["dns_error"] = f"{type(exc).__name__}: {exc}"
    try:
        with requests.get(url, headers=HEADERS, timeout=(15, 45), stream=True,
                          allow_redirects=True) as response:
            result["http_status"] = response.status_code
            result["final_url"] = response.url
            result["content_type"] = response.headers.get("Content-Type")
            result["content_length"] = response.headers.get("Content-Length")
            result["response_sample"] = next(response.iter_content(128), b"").hex()
            result["http_ok"] = response.ok
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result

report = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "runner": "GitHub-hosted Actions runner",
    "purpose": "Read-only official-source connectivity diagnostic",
    "results": [probe(item) for item in SOURCES],
}
path = OUT / "connectivity-report.json"
path.write_text(json.dumps(report, indent=2), encoding="utf-8")
for item in report["results"]:
    print(f'{item["name"]}: DNS={bool(item["dns"])} HTTP={item["http_status"]} '
          f'content_type={item["content_type"]} error={item["error"]}')
print(f"Saved {path}")
