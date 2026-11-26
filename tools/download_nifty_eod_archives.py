#!/usr/bin/env python3
"""Acquire official NSE EOD archives and reconcile NIFTY options to dated MII masters.

All original Bhavcopy ZIP and MII GZ bytes are retained. Cross-session MII matches
are explicitly labelled with their source master date; no synthetic rows are created.
"""
from __future__ import annotations
import csv, gzip, hashlib, io, json, os, time, zipfile
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
import requests

ROOT = Path("artifacts/nse-phase1")
RAW = ROOT / "raw"
ROOT.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "text/html,application/zip,application/gzip,text/csv,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)
REGULAR_DATES = [
 "2026-10-21","2026-10-22","2026-10-23","2026-10-26","2026-10-27",
 "2026-10-28","2026-10-29","2026-10-30","2026-11-02","2026-11-03",
 "2026-11-04","2026-11-05","2026-11-06","2026-11-09","2026-11-11",
 "2026-11-12","2026-11-13","2026-11-16","2026-11-17","2026-11-18","2026-11-19"
]
INCLUDE_MUHURAT = os.getenv("INCLUDE_MUHURAT", "auto").lower() or "auto"
DATES = (["2026-11-08"] + REGULAR_DATES) if INCLUDE_MUHURAT in {"auto","yes","true","1"} else REGULAR_DATES
if len(DATES) != len(set(DATES)):
    raise RuntimeError("Duplicate dates in acquisition plan")

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def download(url: str, target: Path) -> dict:
    error = None
    for attempt in range(1, 4):
        try:
            with SESSION.get(url, timeout=(20, 90), stream=True) as response:
                response.raise_for_status()
                chunks = []
                for chunk in response.iter_content(1024 * 1024):
                    if chunk:
                        chunks.append(chunk)
                body = b"".join(chunks)
                if not body or body.lstrip()[:20].lower().startswith((b"<!doctype", b"<html")):
                    raise ValueError("Response was empty or HTML, not an archive")
                target.write_bytes(body)
                return {"url":url,"status":"downloaded","http_status":response.status_code,
                        "bytes":len(body),"sha256":sha256(body),"attempts":attempt}
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            time.sleep(attempt * 2)
    return {"url":url,"status":"failed","error":error,"attempts":3}

def urls_for(day: str):
    d = date.fromisoformat(day)
    ymd, dmy = d.strftime("%Y%m%d"), d.strftime("%d%m%Y")
    bhav = [f"https://{host}/content/fo/BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv.zip"
            for host in ("archives.nseindia.com","nsearchives.nseindia.com","www.nseindia.com")]
    mii = [f"https://{host}/content/fo/NSE_FO_contract_{dmy}.csv.gz"
           for host in ("archives.nseindia.com","nsearchives.nseindia.com","www.nseindia.com")]
    return bhav, mii

def first_success(urls, target):
    for url in urls:
        result = download(url, target)
        if result["status"] == "downloaded":
            return result
    return {"status":"failed","error":"All official NSE URL candidates failed"}

def csv_from_zip(path: Path):
    with zipfile.ZipFile(path) as archive:
        names = [n for n in archive.namelist() if n.lower().endswith(".csv")]
        if len(names) != 1:
            raise ValueError(f"Expected exactly one CSV in Bhavcopy ZIP, got {names}")
        name = names[0]
        rows = list(csv.DictReader(io.StringIO(archive.read(name).decode("utf-8-sig"))))
        return name, rows

def csv_from_gzip(path: Path):
    raw = gzip.decompress(path.read_bytes()).decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(raw)))

def mii_expiry_date(raw_value: str) -> str:
    # NSE MII expiry is seconds since 1980-01-01 UTC, not Unix epoch.
    seconds = int(Decimal(raw_value))
    return (datetime(1980,1,1,tzinfo=timezone.utc) + timedelta(seconds=seconds)).date().isoformat()

def mii_strike(raw_value: str) -> Decimal:
    # NSE MII strike is stored in 1/100 units.
    return Decimal(raw_value) / Decimal("100")

def identity_checks(bhav_row, master_row):
    return {
        "symbol": bhav_row.get("TckrSymb","").strip().upper() == master_row.get("TckrSymb","").strip().upper(),
        "option_type": bhav_row.get("OptnTp","").strip().upper() == master_row.get("OptnTp","").strip().upper(),
        "expiry": bhav_row.get("XpryDt","").strip() == mii_expiry_date(master_row.get("XpryDt","")),
        "strike": Decimal(bhav_row.get("StrkPric","0")) == mii_strike(master_row.get("StrkPric","0")),
        "contract_name": bhav_row.get("FinInstrmNm","").strip().upper() == master_row.get("StockNm","").strip().upper(),
        "mii_product_type": master_row.get("FinInstrmNm","").strip().upper() == "OPTIDX",
    }

def is_nifty_option(row):
    return (row.get("TckrSymb","").strip().upper() == "NIFTY"
            and row.get("FinInstrmTp","").strip().upper() == "IDO"
            and row.get("OptnTp","").strip().upper() in {"CE","PE"})

# 1. Download and retain every original source file.
manifest = []
for day in DATES:
    bhav_urls, mii_urls = urls_for(day)
    bhav_path = RAW / f"bhavcopy_{day}.zip"
    mii_path = RAW / f"mii_contract_{day}.csv.gz"
    bhav_result = first_success(bhav_urls, bhav_path)
    mii_result = first_success(mii_urls, mii_path)
    manifest.append({"session_date":day,"bhavcopy":bhav_result,"mii_contract":mii_result})
    print(f"{day}: Bhavcopy={bhav_result['status']} MII={mii_result['status']}", flush=True)

failed = [x for x in manifest if x["bhavcopy"]["status"] != "downloaded" or x["mii_contract"]["status"] != "downloaded"]
if failed:
    (ROOT/"manifest.json").write_text(json.dumps({"target_sessions":DATES,"results":manifest},indent=2),encoding="utf-8")
    raise RuntimeError(f"{len(failed)} session(s) missing one or more required official source files; see manifest.json")

# 2. Parse exact NSE UDiFF schema and load dated MII masters.
bhav_rows_by_day = {}
mii_by_day = {}
master_union = defaultdict(list)
session_stats = []
for day in DATES:
    member, all_bhav_rows = csv_from_zip(RAW / f"bhavcopy_{day}.zip")
    mii_rows = csv_from_gzip(RAW / f"mii_contract_{day}.csv.gz")
    nifty_rows = [r for r in all_bhav_rows if is_nifty_option(r)]
    mii_nifty = [r for r in mii_rows
                 if r.get("TckrSymb","").strip().upper()=="NIFTY"
                 and r.get("FinInstrmNm","").strip().upper()=="OPTIDX"
                 and r.get("OptnTp","").strip().upper() in {"CE","PE"}]
    mii_map = {r["FinInstrmId"]:r for r in mii_nifty if r.get("FinInstrmId")}
    if len(mii_map) != len([r for r in mii_nifty if r.get("FinInstrmId")]):
        raise RuntimeError(f"Duplicate FinInstrmId in {day} MII NIFTY option master")
    bhav_rows_by_day[day] = (member, all_bhav_rows, nifty_rows)
    mii_by_day[day] = mii_map
    for instrument_id, row in mii_map.items():
        master_union[instrument_id].append((day,row))
    ids = [r["FinInstrmId"] for r in nifty_rows if r.get("FinInstrmId")]
    duplicate_ids = len(ids) - len(set(ids))
    session_stats.append({
        "session_date":day,"bhavcopy_csv_member":member,"bhavcopy_total_rows":len(all_bhav_rows),
        "nifty_option_rows":len(nifty_rows),
        "nifty_ce_rows":sum(r["OptnTp"].strip().upper()=="CE" for r in nifty_rows),
        "nifty_pe_rows":sum(r["OptnTp"].strip().upper()=="PE" for r in nifty_rows),
        "zero_volume_rows":sum(float(r.get("TtlTradgVol") or 0)==0 for r in nifty_rows),
        "same_day_mii_nifty_option_contracts":len(mii_map),
        "unique_bhavcopy_instrument_ids":len(set(ids)),
        "duplicate_bhavcopy_instrument_ids":duplicate_ids,
        "same_day_id_matches":len(set(ids) & set(mii_map)),
        "missing_same_day_master":len(set(ids) - set(mii_map)),
    })

# 3. Reconcile each Bhavcopy contract by immutable NSE instrument ID.
reconciliation = []
for day in DATES:
    _, _, rows = bhav_rows_by_day[day]
    same_master = mii_by_day[day]
    for row in rows:
        instrument_id = row.get("FinInstrmId","").strip()
        match_type, master_day, master_row = "unmatched_all_22_masters", "", None
        if instrument_id in same_master:
            match_type, master_day, master_row = "same_day_master_match", day, same_master[instrument_id]
        elif instrument_id in master_union:
            # Prefer nearest dated master record; ties resolve to earlier date.
            choices = sorted(master_union[instrument_id],
                             key=lambda item:(abs((date.fromisoformat(item[0])-date.fromisoformat(day)).days),
                                              item[0]))
            master_day, master_row = choices[0]
            match_type = "cross_session_master_match"
        checks = identity_checks(row, master_row) if master_row else {}
        reconciliation.append({
            "session_date":day,"FinInstrmId":instrument_id,"FinInstrmNm":row.get("FinInstrmNm",""),
            "expiry_date":row.get("XpryDt",""),"strike":row.get("StrkPric",""),
            "option_type":row.get("OptnTp",""),"bhavcopy_underlying":row.get("TckrSymb",""),
            "master_match_type":match_type,"master_source_date":master_day,
            "master_symbol":master_row.get("TckrSymb","") if master_row else "",
            "master_contract_name":master_row.get("StockNm","") if master_row else "",
            "master_expiry_date":mii_expiry_date(master_row.get("XpryDt","")) if master_row else "",
            "master_strike_normalized":str(mii_strike(master_row.get("StrkPric","0"))) if master_row else "",
            "master_option_type":master_row.get("OptnTp","") if master_row else "",
            "identity_checks":json.dumps(checks,sort_keys=True),
            "identity_match":bool(checks) and all(checks.values()),
        })

# 4. Enforce invariants before calling this a reconciled audit.
unmatched = [r for r in reconciliation if r["master_match_type"]=="unmatched_all_22_masters"]
identity_mismatches = [r for r in reconciliation if r["master_match_type"]!="unmatched_all_22_masters" and not r["identity_match"]]
duplicate_sessions = [x for x in session_stats if x["duplicate_bhavcopy_instrument_ids"]]
total_options = sum(x["nifty_option_rows"] for x in session_stats)
total_ce = sum(x["nifty_ce_rows"] for x in session_stats)
total_pe = sum(x["nifty_pe_rows"] for x in session_stats)
total_zero = sum(x["zero_volume_rows"] for x in session_stats)
cross = sum(r["master_match_type"]=="cross_session_master_match" for r in reconciliation)
same = sum(r["master_match_type"]=="same_day_master_match" for r in reconciliation)
summary = {
    "generated_at_utc":datetime.now(timezone.utc).isoformat(),
    "source_policy":"Official NSE Bhavcopy and MII archives only; no access-control bypass; no synthetic market rows",
    "target_sessions":DATES,"session_count":len(DATES),
    "downloaded_bhavcopy_files":sum(x["bhavcopy"]["status"]=="downloaded" for x in manifest),
    "downloaded_mii_files":sum(x["mii_contract"]["status"]=="downloaded" for x in manifest),
    "total_nifty_option_rows":total_options,"total_ce_rows":total_ce,"total_pe_rows":total_pe,
    "total_zero_volume_rows":total_zero,"same_day_master_matches":same,
    "cross_session_master_matches":cross,"unmatched_across_all_22_masters":len(unmatched),
    "identity_mismatches":len(identity_mismatches),
    "unique_nifty_instrument_ids_across_master_union":len(master_union),
    "duplicate_bhavcopy_ids_by_session":duplicate_sessions,
    "audit_status":"PASS" if len(DATES)==22 and len(manifest)==22 and not unmatched and not identity_mismatches and not duplicate_sessions and total_ce+total_pe==total_options else "REVIEW_REQUIRED",
    "limitations":[
        "A cross-session MII match validates contract identity only; it does not replace the original session's MII snapshot.",
        "The MII master is a contract reference file, not historical option-chain OI or premium data.",
        "Muhurat date is included only because its Bhavcopy and MII source files were successfully downloaded."
    ]
}
(ROOT/"manifest.json").write_text(json.dumps({"generated_at_utc":summary["generated_at_utc"],
    "source_policy":summary["source_policy"],"target_sessions":DATES,"results":manifest},indent=2),encoding="utf-8")
(ROOT/"audit.json").write_text(json.dumps({"summary":summary,"sessions":session_stats},indent=2),encoding="utf-8")
with (ROOT/"audit.csv").open("w",newline="",encoding="utf-8") as f:
    fields=list(session_stats[0].keys())
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(session_stats)
with (ROOT/"contract-reconciliation.csv").open("w",newline="",encoding="utf-8") as f:
    fields=list(reconciliation[0].keys()) if reconciliation else []
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(reconciliation)
print(json.dumps(summary,indent=2),flush=True)
if summary["audit_status"] != "PASS":
    raise RuntimeError("NIFTY EOD audit invariants failed; inspect audit.json and contract-reconciliation.csv")
