#!/usr/bin/env python3
"""Download one-day NSE F&O supplementary EOD samples via archive URLs."""
from __future__ import annotations
import hashlib, json, os, time, zipfile, io
from datetime import datetime, timezone
from pathlib import Path
import requests

DATE=os.getenv("TRADE_DATE","2026-10-30")
dt=datetime.strptime(DATE,"%Y-%m-%d")
ddmmyyyy=dt.strftime("%d%m%Y")
ddmonyyyy=dt.strftime("%d%b%Y").upper()
root=Path("artifacts/nse-api-route-probe")
raw=root/"raw"; raw.mkdir(parents=True,exist_ok=True)
session=requests.Session()
session.headers.update({
 "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36",
 "Accept":"text/csv,application/zip,application/octet-stream,*/*",
 "Accept-Language":"en-US,en;q=0.9",
 "Referer":"https://www.nseindia.in/all-reports-derivatives",
})
# Prime NSE cookies from the official report catalogue.
for page in ("https://www.nseindia.in/","https://www.nseindia.in/all-reports-derivatives"):
 try: session.get(page,timeout=(15,45))
 except requests.RequestException: pass

reports=[
 {"key":"participant_open_interest","filename":f"fao_participant_oi_{ddmmyyyy}.csv",
  "url":f"https://nsearchives.nseindia.com/content/nsccl/fao_participant_oi_{ddmmyyyy}.csv","kind":"csv"},
 {"key":"participant_trading_volume","filename":f"fao_participant_vol_{ddmmyyyy}.csv",
  "url":f"https://nsearchives.nseindia.com/content/nsccl/fao_participant_vol_{ddmmyyyy}.csv","kind":"csv"},
 {"key":"market_activity","filename":f"fo{ddmmyyyy}.zip",
  "url":f"https://nsearchives.nseindia.com/archives/fo/mkt/fo{ddmmyyyy}.zip","kind":"zip"},
 {"key":"daily_settlement_prices","filename":f"FOSett_prce_{ddmmyyyy}.csv",
  "url":f"https://nsearchives.nseindia.com/archives/nsccl/sett/FOSett_prce_{ddmmyyyy}.csv","kind":"csv"},
 {"key":"daily_volatility","filename":f"FOVOLT_{ddmmyyyy}.csv",
  "url":f"https://nsearchives.nseindia.com/archives/nsccl/volt/FOVOLT_{ddmmyyyy}.csv","kind":"csv"},
]
results=[]
for report in reports:
 item={**report,"status":"NOT_RESOLVED"}
 try:
  response=session.get(report["url"],timeout=(20,90))
  body=response.content
  valid=response.status_code==200 and len(body)>100
  if report["kind"]=="zip":
   valid=valid and zipfile.is_zipfile(io.BytesIO(body))
   if valid:
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
     members=[{"name":x.filename,"bytes":x.file_size} for x in archive.infolist() if not x.is_dir()]
     valid=bool(members)
  else:
   prefix=body[:8192].lstrip().lower()
   valid=valid and not prefix.startswith((b"<html",b"<!doctype",b"{")) and (b"," in body[:8192] or b";" in body[:8192])
   members=[]
  item.update({"http_status":response.status_code,"bytes":len(body),
    "content_type":response.headers.get("Content-Type"),"final_url":response.url,
    "valid_payload":bool(valid)})
  if valid:
   path=raw/report["filename"]; path.write_bytes(body)
   item.update({"status":"DOWNLOADED","saved_path":str(path),
    "sha256":hashlib.sha256(body).hexdigest(),"zip_members":members})
 except Exception as exc:
  item["error"]=f"{type(exc).__name__}: {exc}"
 results.append(item)
 time.sleep(1.0)

result={"trade_date":DATE,"generated_at_utc":datetime.now(timezone.utc).isoformat(),
 "source":"NSE archive URLs; original response bytes retained unchanged","reports":results}
(root/"api-route-probe.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
lines=[f"# NSE supplementary F&O sample — {DATE}","","| Report | Status | HTTP | Bytes | SHA-256 |","|---|---|---:|---:|---|"]
for x in results:
 lines.append(f"| {x['key']} | {x['status']} | {x.get('http_status','')} | {x.get('bytes','')} | {x.get('sha256','')} |")
for x in results:
 lines += ["",f"## {x['key']}",f"- URL: {x['url']}",f"- Content-Type: {x.get('content_type','')}",f"- Final URL: {x.get('final_url','')}"]
 for m in x.get("zip_members",[]): lines.append(f"- ZIP member: {m['name']} ({m['bytes']} bytes)")
 if x.get("error"): lines.append(f"- Error: {x['error']}")
(root/"api-route-probe.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(json.dumps({"trade_date":DATE,"reports":[{k:x.get(k) for k in ("key","status","http_status","bytes","sha256","zip_members","error")} for x in results]},indent=2))
if not any(x["status"]=="DOWNLOADED" for x in results):
 raise SystemExit("No supplementary NSE archive report downloaded.")
