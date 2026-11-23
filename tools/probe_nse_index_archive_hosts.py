#!/usr/bin/env python3
"""Compare official NSE archive hostnames for the daily all-indices CSV."""
import json
from datetime import datetime, timezone
from pathlib import Path
import requests

dmy = "19112026"
urls = [
    f"https://archives.nseindia.com/content/indices/ind_close_all_{dmy}.csv",
    f"https://nsearchives.nseindia.com/content/indices/ind_close_all_{dmy}.csv",
]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36",
    "Accept": "text/csv,application/csv,application/octet-stream,*/*",
    "Referer": "https://www.nseindia.com/all-reports",
}
results=[]
for url in urls:
    item={"url":url}
    try:
        r=requests.get(url,headers=headers,timeout=(8,20))
        item.update(status=r.status_code,final_url=r.url,content_type=r.headers.get("Content-Type"),bytes=len(r.content),
                    prefix=r.content[:160].decode("utf-8-sig","replace"))
    except Exception as exc:
        item["error"]=f"{type(exc).__name__}: {exc}"
    results.append(item)
    print(item)
out=Path("artifacts"); out.mkdir(exist_ok=True)
(out/"nse-index-archive-host-probe.json").write_text(json.dumps({"generated_at_utc":datetime.now(timezone.utc).isoformat(),"results":results},indent=2),encoding="utf-8")
