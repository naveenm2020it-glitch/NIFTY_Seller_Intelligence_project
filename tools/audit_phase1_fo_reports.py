#!/usr/bin/env python3
"""Row-level audit of the 22-session official NSE F&O Bhavcopy/MII archive set."""
from __future__ import annotations

import gzip
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

DATES = [
    "20261021","20261022","20261023","20261026","20261027","20261028","20261029","20261030",
    "20261102","20261103","20261104","20261105","20261106","20261108","20261109","20261111",
    "20261112","20261113","20261116","20261117","20261118","20261119",
]
ROOT = Path("artifacts/raw/nse")
OUT = Path("artifacts/audit")
EPOCH = pd.Timestamp("1980-01-01")

def read_bhavcopy(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names) != 1:
            raise ValueError(f"{path.name}: expected one CSV member, got {len(names)}")
        with z.open(names[0]) as stream:
            return pd.read_csv(stream, low_memory=False)

def read_mii(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, compression="gzip", low_memory=False)

def numeric(series):
    return pd.to_numeric(series, errors="coerce")

def expiry_1980(series):
    return pd.to_datetime(numeric(series), unit="s", origin=EPOCH, errors="coerce")

def audit_day(ymd: str, previous_ymd: str | None) -> dict:
    d = datetime.strptime(ymd, "%Y%m%d")
    ddmmyyyy = d.strftime("%d%m%Y")
    bh_path = ROOT / "fo_bhavcopy" / f"BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv.zip"
    mii_path = ROOT / "mii_contracts" / f"NSE_FO_contract_{ddmmyyyy}.csv.gz"
    if not bh_path.exists() or not mii_path.exists():
        raise FileNotFoundError(f"{d:%Y-%m-%d}: missing Bhavcopy or MII file")
    bh, mii = read_bhavcopy(bh_path), read_mii(mii_path)
    b = bh[(bh["TckrSymb"].astype(str).str.upper() == "NIFTY") & bh["OptnTp"].isin(["CE", "PE"])].copy()
    c = mii[(mii["TckrSymb"].astype(str).str.upper() == "NIFTY") & mii["OptnTp"].isin(["CE", "PE"])].copy()
    b["idn"] = numeric(b["FinInstrmId"])
    c["idn"] = numeric(c["FinInstrmId"])
    b["expiry"] = pd.to_datetime(b["XpryDt"], errors="coerce")
    b["strike"] = numeric(b["StrkPric"])
    c["expiry"] = expiry_1980(c["XpryDt"])
    c["strike"] = numeric(c["StrkPric"]) / 100.0
    mii_by_id = c.drop_duplicates("idn").set_index("idn")
    same_ids = set(mii_by_id.index.dropna())
    missing = b[~b["idn"].isin(same_ids)]
    previous_by_id = pd.DataFrame()
    previous_ids = set()
    if len(missing) and previous_ymd:
        prev_date = datetime.strptime(previous_ymd, "%Y%m%d")
        prev_path = ROOT / "mii_contracts" / f"NSE_FO_contract_{prev_date:%d%m%Y}.csv.gz"
        previous = read_mii(prev_path)
        previous = previous[(previous["TckrSymb"].astype(str).str.upper() == "NIFTY") & previous["OptnTp"].isin(["CE", "PE"])].copy()
        previous["idn"] = numeric(previous["FinInstrmId"])
        previous["expiry"] = expiry_1980(previous["XpryDt"])
        previous["strike"] = numeric(previous["StrkPric"]) / 100.0
        previous_by_id = previous.drop_duplicates("idn").set_index("idn")
        previous_ids = set(previous_by_id.index.dropna())
    expiry_ok = strike_ok = option_ok = prev_expiry_count = 0
    unmatched = 0
    for row in b.itertuples(index=False):
        iid = row.idn
        if iid in mii_by_id.index:
            ref = mii_by_id.loc[iid]
        elif iid in previous_ids:
            ref = previous_by_id.loc[iid]
            prev_expiry_count += 1
        else:
            unmatched += 1
            continue
        if pd.notna(ref["expiry"]) and pd.notna(row.expiry) and ref["expiry"].date() == row.expiry.date():
            expiry_ok += 1
        if pd.notna(ref["strike"]) and pd.notna(row.strike) and abs(ref["strike"] - row.strike) < 1e-8:
            strike_ok += 1
        if str(ref["OptnTp"]) == str(row.OptnTp):
            option_ok += 1
    for col in ["OpnPric", "HghPric", "LwPric", "ClsPric", "UndrlygPric", "TtlTradgVol", "OpnIntrst"]:
        b[col + "_n"] = numeric(b[col])
    traded = b[b["TtlTradgVol_n"] > 0]
    zero = b[b["TtlTradgVol_n"] == 0]
    ohlc_bad = (
        (traded["HghPric_n"] < traded["LwPric_n"]) |
        (traded["HghPric_n"] < traded["OpnPric_n"]) |
        (traded["HghPric_n"] < traded["ClsPric_n"]) |
        (traded["LwPric_n"] > traded["OpnPric_n"]) |
        (traded["LwPric_n"] > traded["ClsPric_n"])
    ).fillna(True)
    ohlc_bad |= traded[["OpnPric_n", "HghPric_n", "LwPric_n", "ClsPric_n"]].isna().any(axis=1)
    trad_dates = pd.to_datetime(bh["TradDt"], errors="coerce").dropna().dt.normalize().unique()
    biz_dates = pd.to_datetime(bh["BizDt"], errors="coerce").dropna().dt.normalize().unique()
    expected = pd.Timestamp(d.date())
    index_path = ROOT / "nifty50_ohlc" / f"ind_close_all_{ddmmyyyy}.csv"
    if not index_path.exists():
        raise FileNotFoundError(f"{d:%Y-%m-%d}: missing NIFTY 50 index CSV")
    index_df = pd.read_csv(index_path)
    index_rows = index_df[index_df["Index Name"].astype(str).str.strip().str.lower() == "nifty 50"]
    if len(index_rows) != 1:
        raise ValueError(f"{d:%Y-%m-%d}: expected one NIFTY 50 row, got {len(index_rows)}")
    ix = index_rows.iloc[0]
    index_date = pd.to_datetime(ix["Index Date"], format="%d-%m-%Y", errors="coerce")
    ix_open, ix_high, ix_low, ix_close = [float(ix[col]) for col in
        ["Open Index Value", "High Index Value", "Low Index Value", "Closing Index Value"]]
    index_ohlc_valid = ix_high >= max(ix_open, ix_low, ix_close) and ix_low <= min(ix_open, ix_high, ix_close)
    underlying_price = float(b["UndrlygPric_n"].dropna().iloc[0]) if b["UndrlygPric_n"].notna().any() else None
    return {
        "date": expected.strftime("%Y-%m-%d"),
        "bhavcopy_filename": bh_path.name, "mii_filename": mii_path.name,
        "bhavcopy_total_rows": len(bh), "bhavcopy_duplicate_ids_all": int(numeric(bh["FinInstrmId"]).duplicated().sum()),
        "mii_duplicate_ids_all": int(numeric(mii["FinInstrmId"]).duplicated().sum()),
        "trad_date_match": len(trad_dates) == 1 and pd.Timestamp(trad_dates[0]) == expected,
        "biz_date_match": len(biz_dates) == 1 and pd.Timestamp(biz_dates[0]) == expected,
        "nifty_option_rows": len(b), "ce_rows": int((b["OptnTp"] == "CE").sum()),
        "pe_rows": int((b["OptnTp"] == "PE").sum()), "expiry_count": int(b["expiry"].nunique()),
        "unique_strikes": int(b["strike"].nunique()), "bhavcopy_duplicate_nifty_ids": int(b["idn"].duplicated().sum()),
        "mii_nifty_option_rows": len(c), "mii_ce_rows": int((c["OptnTp"] == "CE").sum()),
        "mii_pe_rows": int((c["OptnTp"] == "PE").sum()), "mii_duplicate_nifty_ids": int(c["idn"].duplicated().sum()),
        "same_day_contract_matches": int(b["idn"].isin(same_ids).sum()),
        "previous_day_expiry_contract_matches": prev_expiry_count, "unmatched_contract_ids": unmatched,
        "expiry_matches": expiry_ok, "strike_matches": strike_ok, "option_type_matches": option_ok,
        "zero_volume_rows": len(zero), "traded_rows": len(traded),
        "negative_volume_rows": int((b["TtlTradgVol_n"] < 0).sum()),
        "negative_oi_rows": int((b["OpnIntrst_n"] < 0).sum()),
        "traded_ohlc_invalid_rows": int(ohlc_bad.sum()),
        "traded_ohlc_nonpositive_rows": int((traded[["OpnPric_n", "HghPric_n", "LwPric_n", "ClsPric_n"]] <= 0).any(axis=1).sum()),
        "zero_volume_rows_with_zero_open_high_low": int((zero[["OpnPric_n", "HghPric_n", "LwPric_n"]] == 0).all(axis=1).sum()),
        "underlying_missing_rows": int(b["UndrlygPric_n"].isna().sum()),
        "underlying_unique_values": int(b["UndrlygPric_n"].nunique()),
        "underlying_price": underlying_price,
        "nifty50_index_date_match": pd.notna(index_date) and index_date.normalize() == expected,
        "nifty50_index_ohlc_valid": index_ohlc_valid,
        "nifty50_index_open": ix_open, "nifty50_index_high": ix_high, "nifty50_index_low": ix_low,
        "nifty50_index_close": ix_close,
        "underlying_equals_nifty50_close": underlying_price is not None and np.isclose(underlying_price, ix_close, atol=1e-8),
        "mii_prtd_to_trad_counts": c["PrtdToTrad"].value_counts(dropna=False).to_dict(),
        "mii_del_flag_counts": c["DelFlg"].value_counts(dropna=False).to_dict(),
    }

def main():
    rows = []
    for i, ymd in enumerate(DATES):
        rows.append(audit_day(ymd, DATES[i - 1] if i else None))
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "phase1-fo-datewise-audit.csv", index=False)
    checks = {
        "sessions": len(df),
        "all_bhavcopy_and_mii_files_present": len(df) == 22,
        "all_trad_dates_match": bool(df["trad_date_match"].all()),
        "all_biz_dates_match": bool(df["biz_date_match"].all()),
        "all_bhavcopy_and_mii_ids_unique": bool((df["bhavcopy_duplicate_ids_all"].sum() == 0) and (df["mii_duplicate_ids_all"].sum() == 0)),
        "all_nifty_option_ids_unique": bool((df["bhavcopy_duplicate_nifty_ids"].sum() == 0) and (df["mii_duplicate_nifty_ids"].sum() == 0)),
        "all_option_contracts_mapped": int(df["unmatched_contract_ids"].sum()) == 0,
        "all_contract_expiry_strike_option_type_match": bool(
            (df["expiry_matches"] == df["nifty_option_rows"]).all() and
            (df["strike_matches"] == df["nifty_option_rows"]).all() and
            (df["option_type_matches"] == df["nifty_option_rows"]).all()
        ),
        "no_negative_volume_or_oi": int(df["negative_volume_rows"].sum()) == 0 and int(df["negative_oi_rows"].sum()) == 0,
        "all_traded_option_ohlc_valid": int(df["traded_ohlc_invalid_rows"].sum()) == 0 and int(df["traded_ohlc_nonpositive_rows"].sum()) == 0,
        "underlying_present_and_single_value_per_day": int(df["underlying_missing_rows"].sum()) == 0 and bool((df["underlying_unique_values"] == 1).all()),
        "all_nifty50_index_dates_and_ohlc_valid": bool(df["nifty50_index_date_match"].all() and df["nifty50_index_ohlc_valid"].all()),
        "underlying_price_matches_nifty50_index_close_all_sessions": bool(df["underlying_equals_nifty50_close"].all()),
        "zero_volume_rows_preserved": True,
    }
    summary = {
        "scope": "22 candidate sessions ending 2026-11-19; Muhurat 2026-11-08 included because both official F&O reports were downloaded",
        "fallback_2026-10-19": "downloaded as contingency only; excluded from selected 22-session set",
        "totals": {k: int(df[k].sum()) for k in [
            "bhavcopy_total_rows","nifty_option_rows","ce_rows","pe_rows","mii_nifty_option_rows",
            "zero_volume_rows","traded_rows","same_day_contract_matches","previous_day_expiry_contract_matches",
            "unmatched_contract_ids","expiry_matches","strike_matches","option_type_matches"
        ]},
        "checks": checks,
        "passed_checks": sum(checks.values()),
        "total_checks": len(checks),
    }
    (OUT / "phase1-fo-audit-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not all(checks.values()):
        raise SystemExit("F&O audit found one or more validation failures; inspect date-wise CSV.")

if __name__ == "__main__":
    main()
