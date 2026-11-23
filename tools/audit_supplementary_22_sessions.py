#!/usr/bin/env python3
"""One-off 22-session audit of NSE participant OI and F&O daily volatility."""
from __future__ import annotations
import hashlib, io, json, os, time, zipfile
from datetime import datetime, timezone
from pathlib import Path
import requests
import pandas as pd

DATES = ["2026-10-21","2026-10-22","2026-10-23","2026-10-26","2026-10-27","2026-10-28","2026-10-29","2026-10-30","2026-11-02","2026-11-03","2026-11-04","2026-11-05","2026-11-06","2026-11-08","2026-11-09","2026-11-11","2026-11-12","2026-11-13","2026-11-16","2026-11-17","2026-11-18","2026-11-19"]
ROOT = Path("artifacts/supplementary-22-session-audit")
RAW = ROOT / "raw"
RAW.mkdir(parents=True, exist_ok=True)
S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/csv,application/zip,application/octet-stream,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.in/all-reports-derivatives",
})
for page in ("https://www.nseindia.in/", "https://www.nseindia.in/all-reports-derivatives"):
    try: S.get(page, timeout=(15, 45))
    except requests.RequestException: pass

def sha(b): return hashlib.sha256(b).hexdigest()

def get_bytes(url):
    attempts=[]
    for n in range(3):
        try:
            r=S.get(url,timeout=(20,90))
            b=r.content
            attempts.append({"status":r.status_code,"bytes":len(b),"content_type":r.headers.get("Content-Type")})
            if r.status_code==200 and len(b)>100 and not b.lstrip().lower().startswith((b"<html",b"<!doctype",b"{")):
                return b, attempts
        except Exception as e:
            attempts.append({"error":f"{type(e).__name__}: {e}"})
        time.sleep(1.0*(n+1))
    return None, attempts

def download(date, kind):
    dt=datetime.strptime(date,"%Y-%m-%d")
    dd=dt.strftime("%d%m%Y"); ymd=dt.strftime("%Y%m%d")
    if kind=="participant_oi":
        name=f"fao_participant_oi_{dd}.csv"
        url=f"https://nsearchives.nseindia.com/content/nsccl/{name}"
    elif kind=="daily_volatility":
        name=f"FOVOLT_{dd}.csv"
        url=f"https://nsearchives.nseindia.com/archives/nsccl/volt/{name}"
    else:
        name=f"BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv.zip"
        url=f"https://archives.nseindia.com/content/fo/{name}"
    b, attempts=get_bytes(url)
    item={"date":date,"kind":kind,"filename":name,"url":url,"attempts":attempts}
    if b is None:
        item["status"]="UNAVAILABLE"
        return item, None
    if kind=="bhavcopy" and not zipfile.is_zipfile(io.BytesIO(b)):
        item["status"]="INVALID_ZIP"; return item,None
    if kind!="bhavcopy" and b"," not in b[:8192]:
        item["status"]="INVALID_CSV"; return item,None
    p=RAW/date/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b)
    item.update({"status":"DOWNLOADED","bytes":len(b),"sha256":sha(b),"saved_path":str(p)})
    return item,b

def parse_csv(b, skiprows=0):
    for enc in ("utf-8-sig","latin1"):
        try:
            f=pd.read_csv(io.BytesIO(b),skiprows=skiprows,encoding=enc,low_memory=False)
            f.columns=[str(c).strip() for c in f.columns]
            return f
        except Exception:
            pass
    raise ValueError("CSV parse failed using utf-8-sig and latin1")

def audit_oi(b, date):
    f=parse_csv(b,skiprows=1)
    required=["Client Type","Future Index Long","Future Index Short","Future Stock Long","Future Stock Short",
      "Option Index Call Long","Option Index Put Long","Option Index Call Short","Option Index Put Short",
      "Option Stock Call Long","Option Stock Put Long","Option Stock Call Short","Option Stock Put Short",
      "Total Long Contracts","Total Short Contracts"]
    missing=[c for c in required if c not in f.columns]
    if missing: return {"status":"SCHEMA_MISMATCH","missing_columns":missing,"columns":list(f.columns)}
    f["Client Type"]=f["Client Type"].astype(str).str.strip().str.upper()
    expected={"CLIENT","DII","FII","PRO","TOTAL"}
    categories=set(f["Client Type"])
    total=f[f["Client Type"]=="TOTAL"]
    if len(total)!=1: return {"status":"ROW_LAYOUT_MISMATCH","rows":len(f),"categories":sorted(categories)}
    numeric=required[1:]
    for c in numeric: f[c]=pd.to_numeric(f[c],errors="coerce")
    nulls={c:int(f[c].isna().sum()) for c in numeric if f[c].isna().any()}
    cats=f[f["Client Type"].isin(["CLIENT","DII","FII","PRO"])]
    sums=cats[numeric].sum()
    tv=total.iloc[0][numeric]
    diffs={c:int(sums[c]-tv[c]) for c in numeric if pd.notna(sums[c]) and pd.notna(tv[c]) and sums[c]!=tv[c]}
    return {"status":"OK" if not missing and not nulls and categories==expected else "DATA_QUALITY_WARNING",
      "rows":int(len(f)),"categories":sorted(categories),"expected_categories_present":categories==expected,
      "numeric_nulls":nulls,"total_row_reconciliation_differences":diffs,
      "nifty_specific":False,"scope":"Equity Derivatives participant aggregates; no symbol/expiry/strike identifiers",
      "total_option_index_call_long":int(tv["Option Index Call Long"]),
      "total_option_index_put_long":int(tv["Option Index Put Long"]),
      "total_option_index_call_short":int(tv["Option Index Call Short"]),
      "total_option_index_put_short":int(tv["Option Index Put Short"])}

def audit_vol(b, date):
    f=parse_csv(b)
    required=["Date","Symbol","Underlying Close Price (A)","Underlying Annualised Volatility (F) = E*sqrt(365)",
      "Futures Close Price (G)","Futures Annualised Volatility (L) = K*sqrt(365)",
      "Applicable Annualised Volatility (N) = Max (F or L)"]
    missing=[c for c in required if c not in f.columns]
    if missing: return {"status":"SCHEMA_MISMATCH","missing_columns":missing,"columns":list(f.columns)}
    f["Symbol"]=f["Symbol"].astype(str).str.strip().str.upper()
    n=f[f["Symbol"]=="NIFTY"]
    if len(n)!=1: return {"status":"NIFTY_ROW_MISSING_OR_DUPLICATE","nifty_rows":int(len(n))}
    r=n.iloc[0]
    fields=required[2:]
    vals={c:pd.to_numeric(r[c],errors="coerce") for c in fields}
    if any(pd.isna(v) for v in vals.values()): return {"status":"NIFTY_NUMERIC_PARSE_ERROR"}
    underlying=vals[required[2]]
    underlying_ann=vals[required[3]]
    futures_close=vals[required[4]]
    futures_ann=vals[required[5]]
    applicable=vals[required[6]]
    return {"status":"OK","date_in_file":str(r["Date"]),"nifty_rows":1,
      "nifty_underlying_close":float(underlying),"nifty_underlying_annualised_volatility":float(underlying_ann),
      "nifty_futures_close":float(futures_close),"nifty_futures_annualised_volatility":float(futures_ann),
      "nifty_applicable_annualised_volatility":float(applicable),
      "applicable_equals_max":bool(abs(applicable-max(underlying_ann,futures_ann))<1e-8),
      "volatility_is_option_iv":False}

def audit_bhav(b):
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        names=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names)!=1: raise ValueError(f"Expected one Bhavcopy CSV, got {names}")
        f=parse_csv(z.read(names[0]))
    for c in ["TckrSymb","FinInstrmTp","UndrlygPric","TtlTradgVol"]:
        if c not in f.columns: raise ValueError(f"Bhavcopy missing {c}")
    nifty=f[(f["TckrSymb"].astype(str).str.upper()=="NIFTY") & (f["FinInstrmTp"].astype(str).str.upper()=="IDO")]
    prices=pd.to_numeric(nifty["UndrlygPric"],errors="coerce").dropna().unique()
    if len(prices)!=1: raise ValueError(f"Expected one NIFTY underlying close, got {prices}")
    return {"nifty_option_rows":int(len(nifty)),"nifty_underlying_close":float(prices[0]),
      "zero_volume_rows":int((pd.to_numeric(nifty["TtlTradgVol"],errors="coerce")==0).sum())}

def main():
    downloads=[]; daily=[]
    for date in DATES:
        row={"date":date}
        for kind in ("participant_oi","daily_volatility","bhavcopy"):
            item,b=download(date,kind); downloads.append(item)
            row[kind+"_download_status"]=item["status"]
            if b is not None:
                try:
                    if kind=="participant_oi": row["participant_oi_audit"]=audit_oi(b,date)
                    elif kind=="daily_volatility": row["daily_volatility_audit"]=audit_vol(b,date)
                    else: row["bhavcopy_audit"]=audit_bhav(b)
                except Exception as e:
                    row[kind+"_audit"]={"status":"AUDIT_ERROR","error":f"{type(e).__name__}: {e}"}
            time.sleep(0.35)
        va=row.get("daily_volatility_audit",{})
        ba=row.get("bhavcopy_audit",{})
        if va.get("status")=="OK" and ba.get("nifty_underlying_close") is not None:
            diff=round(va["nifty_underlying_close"]-ba["nifty_underlying_close"],8)
            va["bhavcopy_underlying_close"]=ba["nifty_underlying_close"]
            va["difference_vs_bhavcopy_underlying_close"]=diff
            va["matches_bhavcopy_underlying_close"]=abs(diff)<=0.01
        daily.append(row)
    summary={
      "trade_dates":DATES,"expected_sessions":len(DATES),
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),
      "downloads":downloads,"daily_audits":daily,
      "rollup":{
        "participant_oi_downloaded":sum(x["kind"]=="participant_oi" and x["status"]=="DOWNLOADED" for x in downloads),
        "daily_volatility_downloaded":sum(x["kind"]=="daily_volatility" and x["status"]=="DOWNLOADED" for x in downloads),
        "bhavcopy_downloaded":sum(x["kind"]=="bhavcopy" and x["status"]=="DOWNLOADED" for x in downloads),
        "participant_oi_schema_ok":sum(x.get("participant_oi_audit",{}).get("status")=="OK" for x in daily),
        "daily_volatility_schema_ok":sum(x.get("daily_volatility_audit",{}).get("status")=="OK" for x in daily),
        "volatility_underlying_matches_bhavcopy":sum(x.get("daily_volatility_audit",{}).get("matches_bhavcopy_underlying_close") is True for x in daily),
        "participant_oi_total_reconciliation_warnings":sum(bool(x.get("participant_oi_audit",{}).get("total_row_reconciliation_differences")) for x in daily),
      },
      "interpretation_limits":[
        "Participant OI is aggregate Equity Derivatives positioning, not NIFTY contract/strike-specific positioning.",
        "Daily Volatility is underlying/futures EWMA-style volatility, not option implied volatility.",
        "A 22-session data-quality audit is not predictive validation or evidence of causal signal value.",
        "Bhavcopy is used as the underlying-close cross-check and remains authoritative for contract-level option data.",
        "Missing files are recorded as unavailable; never interpreted as zero."
      ]
    }
    (ROOT/"audit-22-sessions.json").write_text(json.dumps(summary,indent=2,default=str),encoding="utf-8")
    lines=["# NSE Supplementary 22-Session Audit","",
      f"Sessions: {len(DATES)} | Generated: {summary['generated_at_utc']}","",
      "## Download and schema rollup","",
      "| Metric | Result |","|---|---:|"]
    for k,v in summary["rollup"].items(): lines.append(f"| {k} | {v} |")
    lines += ["","## Session results","","| Date | OI download/schema | Volatility download/schema | NIFTY close matches Bhavcopy | OI total reconciliation warning |",
      "|---|---|---|---|---|"]
    for r in daily:
        oi=r.get("participant_oi_audit",{}); vo=r.get("daily_volatility_audit",{})
        lines.append(f"| {r['date']} | {r.get('participant_oi_download_status')} / {oi.get('status','-')} | {r.get('daily_volatility_download_status')} / {vo.get('status','-')} | {vo.get('matches_bhavcopy_underlying_close','-')} | {bool(oi.get('total_row_reconciliation_differences'))} |")
    lines += ["","## Per-session detail",""]
    for r in daily:
        lines += [f"### {r['date']}","",f"- Participant OI: {json.dumps(r.get('participant_oi_audit',{}),sort_keys=True)}",
          f"- Daily volatility: {json.dumps(r.get('daily_volatility_audit',{}),sort_keys=True)}",
          f"- Bhavcopy: {json.dumps(r.get('bhavcopy_audit',{}),sort_keys=True)}",""]
    lines += ["## Interpretation limits",""]+[f"- {x}" for x in summary["interpretation_limits"]]
    (ROOT/"audit-22-sessions.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(summary["rollup"],indent=2))
    if summary["rollup"]["participant_oi_downloaded"]==0 or summary["rollup"]["daily_volatility_downloaded"]==0:
        raise SystemExit("No useful supplementary report samples downloaded.")
if __name__=="__main__": main()
