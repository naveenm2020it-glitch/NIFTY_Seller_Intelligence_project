#!/usr/bin/env python3
"""Probe NSE's report-page archive API for one historical F&O session.

This is a diagnostic fallback to the public report page's own download route.
It retains every successful original response and records all attempted
parameter combinations. No third-party data source is used.
"""
from __future__ import annotations
import hashlib, json, os, re, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
import requests

DATE=os.getenv("TRADE_DATE","2026-10-30")
dt=datetime.strptime(DATE,"%Y-%m-%d")
DATE_LABEL=dt.strftime("%d-%b-%Y")
DDMMYYYY=dt.strftime("%d%m%Y")
ROOT=Path("artifacts/nse-api-route-probe")
RAW=ROOT/"raw"; RAW.mkdir(parents=True,exist_ok=True)
S=requests.Session()
S.headers.update({
 "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36",
 "Accept":"text/html,application/xhtml+xml,application/json,application/octet-stream,*/*",
 "Accept-Language":"en-US,en;q=0.9",
 "Referer":"https://www.nseindia.com/all-reports-derivatives",
})
# Prime the public NSE website session as its own browser download flow does.
for page in ("https://www.nseindia.com/","https://www.nseindia.com/all-reports-derivatives"):
 try: S.get(page,timeout=(15,45))
 except requests.RequestException: pass

REPORTS=[
 ("participant_open_interest","F&O - Participant wise Open Interest(csv)",f"fao_participant_oi_{DDMMYYYY}.csv"),
 ("participant_trading_volume","F&O - Participant wise Trading Volumes(csv)",f"fao_participant_vol_{DDMMYYYY}.csv"),
 ("market_activity","F&O - Market Activity Report",f"fo{DDMMYYYY}.zip"),
 ("daily_settlement_prices","F&O - Daily Settlement Prices(csv)",f"FOSett_prce_{DDMMYYYY}.csv"),
]
# NSE report catalogue places F&O reports under derivatives / equity-derivatives.
CATEGORIES=["derivatives"]
SECTIONS=["equity-derivatives"]
results=[]
for key,name,filename in REPORTS:
 attempts=[]; saved=None
 for category in CATEGORIES:
  for section in SECTIONS:
   archive=[{"name":name,"type":"daily-reports","category":category,"section":section}]
   params={"archives":json.dumps(archive,separators=(",",":")),"date":DATE_LABEL,"type":"derivatives","mode":"single"}
   url="https://www.nseindia.com/api/reports?"+urlencode(params)
   try:
    r=S.get(url,timeout=(20,75))
    b=r.content
    valid=(r.status_code==200 and len(b)>128 and
           not b.lstrip().lower().startswith((b"<!doctype html",b"<html")) and
           not (b.lstrip().startswith(b"{") and b'"error"' in b[:1000].lower()))
    # ZIP report should be ZIP; CSV reports should look like text with delimiters.
    if filename.endswith(".zip"):
     import zipfile,io
     import_ok=zipfile.is_zipfile(io.BytesIO(b))
    else:
     import_ok=(b"," in b[:8192] or b";" in b[:8192] or b"|" in b[:8192])
    attempts.append({"category":category,"section":section,"http_status":r.status_code,
                     "bytes":len(b),"content_type":r.headers.get("Content-Type"),
                     "final_url":r.url,"valid_payload":bool(valid and import_ok)})
    if valid and import_ok:
     path=RAW/filename; path.write_bytes(b)
     saved={"path":str(path),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),
            "category":category,"section":section,"download_url":r.url}
     break
   except Exception as e:
    attempts.append({"category":category,"section":section,"error":f"{type(e).__name__}: {e}"})
   time.sleep(.2)
  if saved: break
 results.append({"key":key,"report_name":name,"expected_filename":filename,
                 "status":"DOWNLOADED" if saved else "NOT_RESOLVED",
                 "saved":saved,"attempts":attempts})
 report={"trade_date":DATE,"generated_at_utc":datetime.now(timezone.utc).isoformat(),
         "endpoint":"https://www.nseindia.com/api/reports",
         "method":"NSE public report-page archive API; session primed from official report page",
         "results":results,
         "warning":"A successful HTTP response is not accepted unless payload format is plausible. Inspect downloaded schemas before ingestion."}
 (ROOT/"api-route-probe.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
 lines=[f"# NSE report API route probe — {DATE}","","| Report | Status | Bytes | Category | Section | SHA-256 |","|---|---|---:|---|---|---|"]
 for x in results:
  z=x["saved"] or {}
  lines.append(f"| {x['key']} | {x['status']} | {z.get('bytes','')} | {z.get('category','')} | {z.get('section','')} | {z.get('sha256','')} |")
 lines += ["","## Attempts",""]
 for x in results:
  lines += [f"### {x['key']}",""]
  for a in x["attempts"]:
   lines.append(f"- category={a.get('category')} section={a.get('section')} HTTP={a.get('http_status')} bytes={a.get('bytes')} valid={a.get('valid_payload')} error={a.get('error','')}")
  lines.append("")
 (ROOT/"api-route-probe.md").write_text("\n".join(lines),encoding="utf-8")
 print(json.dumps({"trade_date":DATE,"results":[{"key":x["key"],"status":x["status"],"saved":x["saved"]} for x in results]},indent=2))
if not any(x["status"]=="DOWNLOADED" for x in results):
 raise SystemExit("NSE report API route probe did not resolve any supplementary reports.")
