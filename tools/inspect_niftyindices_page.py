#!/usr/bin/env python3
"""Inspect the official NSE Indices historical-data page for its published UI download route."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests

BASE = "https://www.niftyindices.com/reports/historical-data"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NIFTY-Seller-Intelligence-Audit/1.0)",
    "Accept": "text/html,application/javascript,*/*",
    "Referer": "https://www.niftyindices.com/",
}
session = requests.Session()
page = session.get(BASE, headers=HEADERS, timeout=45)
page.raise_for_status()
html = page.text
scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html, re.I)
forms = re.findall(r'<form\b[^>]*>', html, re.I)
inputs = re.findall(r'<input\b[^>]*>', html, re.I)
selects = re.findall(r'<select\b[^>]*>', html, re.I)
terms = re.compile(r'historical|download|csv|excel|indexName|fromDate|toDate|datatable|\.ashx|\.aspx|api/', re.I)
js_results = []
for src in scripts:
    url = urljoin(BASE, src)
    try:
        response = session.get(url, headers=HEADERS, timeout=45)
        response.raise_for_status()
        body = response.text
        matches = []
        for match in terms.finditer(body):
            start, end = max(0, match.start()-180), min(len(body), match.end()+260)
            snippet = re.sub(r'\s+', ' ', body[start:end])
            if snippet not in matches:
                matches.append(snippet)
            if len(matches) >= 25:
                break
        if matches:
            js_results.append({"script_url": url, "status": response.status_code, "matches": matches})
    except Exception as exc:
        js_results.append({"script_url": url, "error": f"{type(exc).__name__}: {exc}"})
report = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "page_url": page.url,
    "page_status": page.status_code,
    "page_title": re.findall(r'<title[^>]*>(.*?)</title>', html, re.I|re.S)[:1],
    "forms": forms,
    "inputs": inputs[:100],
    "selects": selects[:100],
    "script_count": len(scripts),
    "script_results": js_results,
}
out = Path("artifacts")
out.mkdir(exist_ok=True)
path = out / "niftyindices-endpoint-discovery.json"
path.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(f"Page HTTP {page.status_code}; scripts {len(scripts)}; form tags {len(forms)}; input tags {len(inputs)}; select tags {len(selects)}")
for item in js_results:
    print(item["script_url"], "matches", len(item.get("matches", [])), "error", item.get("error"))
print(f"Saved {path}")
