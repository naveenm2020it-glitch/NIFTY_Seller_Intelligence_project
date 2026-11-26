#!/usr/bin/env python3
"""Download and audit official NSE F&O EOD archives for 22 NIFTY sessions.

No authentication bypass or third-party data. Original archive bytes are preserved.
The workflow is intentionally manual and uploads results as a GitHub Actions artifact.
"""
from __future__ import annotations
import csv, gzip, hashlib, io, json, os, time, zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import requests

ROOT = Path("artifacts/nse-phase1")
RAW = ROOT / "raw"
RAW.mkdir(parents=True, exist_ok=True)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "text/html,application/zip,application/gzip,text/csv,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}
S = requests.Session()
S.headers.update(HEADERS)
DATES = [
 "2026-10-21","2026-10-22","2026-10-23","2026-10-26","2026-10-27",
 "2026-10-28","2026-10-29","2026-10-30","2026-11-02","2026-11-03",
 "2026-11-04","2026-11-05","2026-11-06","2026-11-09","2026-11-11",
 "2026-11-12","2026-11-13","2026-11-16","2026-11-17","2026-11-18","2026-11-19"
]
if os.getenv("INCLUDE_MUHURAT", "auto").lower() in {"auto","true","1","yes"}:
    DATES.insert(0, "2026-11-08")
if os.getenv("INCLUDE_FALLBACK_20261019","false").lower() in {"true","1","yes"}:
    DATES = [d for d in DATES if d != "2026-11-08"]
    DATES.insert(0,"2026-10-19")

def sha(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def fetch(url: str, out: Path) -> dict:
    last = None
    for attempt in range(1, 4):
        try:
            with S.get(url, timeout=(20, 90), stream=True) as r:
                r.raise_for_status()
                content = b"".join(r.iter_content(1024*1024))
                if not content or content[:20].lower().startswith((b"<!doctype", b"<html")):
                    raise ValueError("Response was empty or HTML, not an archive")
                out.write_bytes(content)
                return {"url":url,"status":"downloaded","http_status":r.status_code,
                        "bytes":len(content),"sha256":sha(content),"attempts":attempt}
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(attempt * 2)
    return {"url":url,"status":"failed","error":last,"attempts":3}

def candidate_urls(day: str):
    d = date.fromisoformat(day)
    ymd, dmy = d.strftime("%Y%m%d"), d.strftime("%d%m%Y")
    bhav_names = [
        f"https://archives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv.zip",
        f"https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv.zip",
        f"https://www.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv.zip",
    ]
    mii_names = [
        f"https://archives.nseindia.com/content/fo/NSE_FO_contract_{dmy}.csv.gz",
        f"https://nsearchives.nseindia.com/content/fo/NSE_FO_contract_{dmy}.csv.gz",
        f"https://www.nseindia.com/content/fo/NSE_FO_contract_{dmy}.csv.gz",
    ]
    return bhav_names, mii_names

def inspect_zip(path: Path):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names) != 1: raise ValueError(f"Expected one CSV in zip, found {names}")
        data = z.read(names[0])
    text = data.decode("utf-8-sig", errors="replace")
    return names[0], text

def inspect_gz(path: Path):
    data = gzip.decompress(path.read_bytes())
    return data.decode("utf-8-sig", errors="replace")

manifest, audit = [], []
for day in DATES:
    burls, murls = candidate_urls(day)
    bpath, mpath = RAW / f"bhavcopy_{day}.zip", RAW / f"mii_contract_{day}.csv.gz"
    brec = next((x for x in (fetch(u,bpath) for u in burls) if x["status"]=="downloaded"), None)
    if brec is None: brec = {"status":"failed","error":"All official Bhavcopy URL candidates failed"}
    mrec = next((x for x in (fetch(u,mpath) for u in murls) if x["status"]=="downloaded"), None)
    if mrec is None: mrec = {"status":"failed","error":"All official MII URL candidates failed"}
    row = {"session_date":day,"bhavcopy":brec,"mii_contract":mrec}
    manifest.append(row)
    checks = {"session_date":day,"bhavcopy_downloaded":brec["status"]=="downloaded",
              "mii_downloaded":mrec["status"]=="downloaded","bhavcopy_rows":None,
              "nifty_option_rows":None,"nifty_ce_rows":None,"nifty_pe_rows":None,
              "zero_volume_nifty_rows":None,"mii_rows":None,"audit_status":"not_audited"}
    if brec["status"]=="downloaded" and mrec["status"]=="downloaded":
        try:
            name, text = inspect_zip(bpath)
            reader = csv.DictReader(io.StringIO(text))
            rows = list(reader)
            cols = reader.fieldnames or []
            symcol = next((c for c in cols if c.upper() in {"TCKRSYMB","SYMBOL","UNDERLYING"}), None)
            instcol = next((c for c in cols if c.upper() in {"FININSTRMTP","INSTRUMENT","INSTRUMENT_TYPE"}), None)
            typcol = next((c for c in cols if c.upper() in {"OPTNTYPE","OPTION_TYPE"}), None)
            volcol = next((c for c in cols if c.upper() in {"TtlTradgVol","TOTTRDQTY","TOTAL_TRADED_QUANTITY","VOLUME"}), None)
            nifty = [x for x in rows if symcol and x.get(symcol,"").strip().upper()=="NIFTY" and
                     ((instcol and "OPT" in x.get(instcol,"").upper()) or typcol)]
            ce = sum(1 for x in nifty if typcol and x.get(typcol,"").strip().upper()=="CE")
            pe = sum(1 for x in nifty if typcol and x.get(typcol,"").strip().upper()=="PE")
            zero = sum(1 for x in nifty if volcol and (x.get(volcol,"").strip() in {"","0","0.0"}))
            mtext = inspect_gz(mpath)
            mrows = list(csv.DictReader(io.StringIO(mtext)))
            checks.update({"bhavcopy_rows":len(rows),"nifty_option_rows":len(nifty),
                           "nifty_ce_rows":ce,"nifty_pe_rows":pe,
                           "zero_volume_nifty_rows":zero,"mii_rows":len(mrows),
                           "bhavcopy_csv_member":name,"bhavcopy_columns":cols,
                           "audit_status":"parsed_schema_review_required"})
        except Exception as e:
            checks["audit_status"]="parse_error"
            checks["parse_error"]=f"{type(e).__name__}: {e}"
    audit.append(checks)
    print(f"{day}: bhavcopy={brec['status']} mii={mrec['status']} audit={checks['audit_status']}")

(ROOT/"manifest.json").write_text(json.dumps({"generated_at_utc":datetime.now(timezone.utc).isoformat(),
    "source_policy":"Official NSE archive host candidates only; no access-control bypass",
    "target_sessions":DATES,"results":manifest},indent=2),encoding="utf-8")
(ROOT/"audit.json").write_text(json.dumps({"generated_at_utc":datetime.now(timezone.utc).isoformat(),
    "sessions":audit,"downloaded_bhavcopy":sum(x["bhavcopy_downloaded"] for x in audit),
    "downloaded_mii":sum(x["mii_downloaded"] for x in audit),
    "parsed_sessions":sum(x["audit_status"]=="parsed_schema_review_required" for x in audit),
    "note":"Row parsing is preliminary. Review reported column schemas before treating counts as validated."},indent=2),encoding="utf-8")
with (ROOT/"audit.csv").open("w",newline="",encoding="utf-8") as f:
    fields=list(audit[0].keys()) if audit else []
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(audit)
print(f"SUMMARY downloaded_bhavcopy={sum(x['bhavcopy_downloaded'] for x in audit)}/{len(audit)} downloaded_mii={sum(x['mii_downloaded'] for x in audit)}/{len(audit)}")
