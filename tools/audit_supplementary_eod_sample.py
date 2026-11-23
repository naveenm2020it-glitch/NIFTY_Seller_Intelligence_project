#!/usr/bin/env python3
"""One-session NSE supplementary EOD report sample download and usefulness audit."""
from __future__ import annotations
import hashlib, io, json, os, time, zipfile
from datetime import datetime, timezone
from pathlib import Path
import requests
import pandas as pd

TRADE_DATE = os.getenv("TRADE_DATE", "2026-10-30")
dt = datetime.strptime(TRADE_DATE, "%Y-%m-%d")
ddmmyyyy, yyyymmdd = dt.strftime("%d%m%Y"), dt.strftime("%Y%m%d")
ROOT = Path("artifacts/supplementary-sample")
RAW = ROOT / "raw"
RAW.mkdir(parents=True, exist_ok=True)
S = requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128 Safari/537.36",
                  "Accept":"text/csv,application/zip,application/octet-stream,*/*",
                  "Referer":"https://www.nseindia.com/"})
REPORTS = {
 "participant_open_interest":[f"https://archives.nseindia.com/content/nsccl/fao_participant_oi_{ddmmyyyy}.csv",f"https://archives.nseindia.com/content/nsccl/fao_participant_oi_{ddmmyyyy}.csv",f"https://archives.nseindia.com/content/nsccl/fao_participant_oi_{ddmmyyyy}.csv",f"https://archives.nseindia.com/content/nsccl/fao_participant_oi_{ddmmyyyy}.csv",f"https://archives.nseindia.com/archives/nsccl/fao/fao_participant_oi_{ddmmyyyy}.csv"],
 "participant_trading_volume":[f"https://archives.nseindia.com/content/nsccl/fao_participant_vol_{ddmmyyyy}.csv",f"https://archives.nseindia.com/content/nsccl/fao_participant_vol_{ddmmyyyy}.csv",f"https://archives.nseindia.com/content/nsccl/fao_participant_vol_{ddmmyyyy}.csv",f"https://archives.nseindia.com/content/nsccl/fao_participant_vol_{ddmmyyyy}.csv",f"https://archives.nseindia.com/archives/nsccl/fao/fao_participant_vol_{ddmmyyyy}.csv"],
 "market_activity":[f"https://archives.nseindia.com/content/nsccl/fo{ddmmyyyy}.zip",f"https://archives.nseindia.com/content/nsccl/fo/fo{ddmmyyyy}.zip",f"https://archives.nseindia.com/archives/nsccl/fao/fo{ddmmyyyy}.zip"],
 "daily_settlement_prices":[f"https://archives.nseindia.com/content/nsccl/FOSett_prce_{ddmmyyyy}.csv",f"https://archives.nseindia.com/content/nsccl/FOSett_prce_{ddmmyyyy}.csv",f"https://archives.nseindia.com/content/nsccl/FOSett_prce_{ddmmyyyy}.csv",f"https://archives.nseindia.com/content/nsccl/FOSett_prce_{ddmmyyyy}.csv",f"https://archives.nseindia.com/archives/nsccl/fao/FOSett_prce_{ddmmyyyy}.csv"]}
BASE=[f"https://archives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{yyyymmdd}_F_0000.csv.zip",f"https://nsearchives.nseindia.com/archives/nsccl/fao/BhavCopy_NSE_FO_0_0_0_{yyyymmdd}_F_0000.csv.zip"]

def digest(b): return hashlib.sha256(b).hexdigest()
def html(b): return b.lstrip().lower().startswith((b"<!doctype html",b"<html",b"<head"))
def download(name, urls, suffix):
 attempts=[]
 for url in urls:
  try:
   r=S.get(url,timeout=(20,90)); b=r.content
   a={"url":url,"http_status":r.status_code,"content_type":r.headers.get("Content-Type"),"bytes":len(b),"final_url":r.url}
   if r.status_code!=200 or not b or html(b): a["result"]="HTTP_ERROR_OR_HTML"; attempts.append(a); continue
   if suffix==".zip" and not zipfile.is_zipfile(io.BytesIO(b)): a["result"]="INVALID_ZIP"; attempts.append(a); continue
   if suffix==".csv" and b"," not in b[:4096] and b";" not in b[:4096]: a["result"]="NOT_RECOGNIZED_AS_CSV"; attempts.append(a); continue
   p=RAW/f"{name}{suffix}"; p.write_bytes(b)
   return {"name":name,"status":"DOWNLOADED","path":str(p),"sha256":digest(b),"bytes":len(b),"source_url":url,"attempts":attempts}
  except Exception as e: attempts.append({"url":url,"result":"EXCEPTION","error":f"{type(e).__name__}: {e}"})
  time.sleep(.4)
 return {"name":name,"status":"UNAVAILABLE_OR_INVALID","attempts":attempts}

def csv_audit(b, source):
 frame=None; errors=[]
 for kw in ({},{"encoding":"latin1"},{"encoding":"latin1","on_bad_lines":"skip"}):
  try: frame=pd.read_csv(io.BytesIO(b),low_memory=False,**kw); break
  except Exception as e: errors.append(str(e))
 if frame is None: return {"source":source,"parse_status":"FAILED","errors":errors}
 cols=[str(c).strip() for c in frame.columns]; low=[c.lower() for c in cols]
 sym=[c for c in cols if any(k in c.lower() for k in ("symbol","underlying","ticker"))]
 nifty={c:int((frame[c].astype(str).str.strip().str.upper()=="NIFTY").sum()) for c in sym}
 participant=any(k in " ".join(low) for k in ("participant","client","pro","fii","dii"))
 relevance=("AGGREGATE_PARTICIPANT_DATA_NOT_NIFTY_CONTRACT_SPECIFIC" if participant and not any(nifty.values()) else
            "NIFTY_ROWS_PRESENT_REQUIRES_FIELD_LEVEL_REVIEW" if any(nifty.values()) else "GENERAL_OR_CONTRACT_REPORT_REQUIRES_FIELD_LEVEL_REVIEW")
 return {"source":source,"parse_status":"OK","rows":int(len(frame)),"columns":cols,
         "null_count_by_column":{str(k):int(v) for k,v in frame.isna().sum().items()},
         "date_columns":[c for c in cols if "date" in c.lower() or c.lower() in {"trad_dt","biz_dt"}],
         "symbol_columns":sym,"nifty_row_counts_by_symbol_column":nifty,"nifty_relevance":relevance,
         "sample_rows":frame.head(5).fillna("").astype(str).to_dict(orient="records")}

def audit(item):
 if item["status"]!="DOWNLOADED": return {"report":item["name"],"status":item["status"],"attempts":item["attempts"]}
 p=Path(item["path"])
 if p.suffix==".csv": return {"report":item["name"],**csv_audit(p.read_bytes(),p.name)}
 out={"report":item["name"],"archive":p.name,"members":[]}
 with zipfile.ZipFile(p) as z:
  for n in z.namelist():
   if n.endswith("/"): continue
   m={"name":n,"bytes":z.getinfo(n).file_size}
   if n.lower().endswith(".csv"): m.update(csv_audit(z.read(n),n))
   out["members"].append(m)
 return out

def main():
 results=[]
 for n,u in REPORTS.items():
  x=download(n,u,".zip" if n=="market_activity" else ".csv"); results.append(x); print(n,x["status"],x.get("bytes"))
 results.append(download("baseline_bhavcopy",BASE,".zip"))
 audits=[audit(x) for x in results]
 data={"trade_date":TRADE_DATE,"generated_at_utc":datetime.now(timezone.utc).isoformat(),
       "source_policy":"Official NSE archive hosts only; original downloaded bytes retained unchanged",
       "downloads":results,"audits":audits,
       "limitations":["One session is a schema/usefulness smoke test, not statistical validation.",
        "Participant-wise aggregate index options data must not be labelled NIFTY-specific.",
        "Market Activity ZIP members are inventoried individually.",
        "No report is promoted into production signal inputs by this audit."]}
 (ROOT/"sample-audit.json").write_text(json.dumps(data,indent=2,default=str),encoding="utf-8")
 lines=[f"# NSE Supplementary EOD Sample Audit — {TRADE_DATE}","","Original files are retained under raw/; one-session diagnostic only.","",
        "| Report | Status | Bytes | SHA-256 |","|---|---|---:|---|"]
 for x in results: lines.append(f"| {x['name']} | {x['status']} | {x.get('bytes','')} | {x.get('sha256','')} |")
 lines += ["","## Schema and usefulness observations",""]
 for a in audits:
  lines += [f"### {a['report']}",""]
  if a.get("parse_status")=="OK": lines += [f"- Rows: {a['rows']}",f"- Columns: {', '.join(a['columns'])}",f"- NIFTY relevance: {a['nifty_relevance']}",""]
  elif "members" in a:
   lines += [f"- ZIP members: {len(a['members'])}",""]
   for m in a["members"]: lines.append(f"  - {m['name']} ({m['bytes']} bytes; {m.get('rows','?')} rows)")
   lines.append("")
  else: lines += [f"- Status: {a.get('status',a.get('parse_status','unknown'))}",""]
 lines += ["## Limitations",""]+[f"- {x}" for x in data["limitations"]]
 (ROOT/"sample-audit.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
 print(json.dumps({"date":TRADE_DATE,"download_status":{x["name"]:x["status"] for x in results},"audit_file":str(ROOT/"sample-audit.json")},indent=2))
 if not any(x["status"]=="DOWNLOADED" for x in results if x["name"]!="baseline_bhavcopy"): raise SystemExit("No supplementary NSE reports downloaded; baseline Bhavcopy alone does not count as a successful supplementary audit.")
if __name__=="__main__": main()
