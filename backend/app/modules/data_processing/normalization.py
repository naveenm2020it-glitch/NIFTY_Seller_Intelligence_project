"""Deterministic normalization for manifest-verified NIFTY EOD source frames."""
from __future__ import annotations
from datetime import date, datetime, timedelta
import math
from typing import Any
import pandas as pd

class ProcessingValidationError(ValueError):
    """Raised when source records cannot be represented without data loss."""

def _required(frame: pd.DataFrame, fields: set[str], label: str) -> None:
    missing=sorted(fields-set(frame.columns))
    if missing: raise ProcessingValidationError(f"{label} is missing required fields: {', '.join(missing)}.")

def _number(value: Any, field: str, *, allow_zero: bool=True) -> float:
    try: result=float(value)
    except (TypeError, ValueError, OverflowError): raise ProcessingValidationError(f"Invalid numeric value in {field}.") from None
    if not math.isfinite(result) or (not allow_zero and result<=0) or (allow_zero and result<0):
        raise ProcessingValidationError(f"Out-of-range numeric value in {field}.")
    return result

def _instrument_id(value: Any) -> str:
    number=_number(value,"FinInstrmId",allow_zero=False)
    if not number.is_integer(): raise ProcessingValidationError("FinInstrmId must be an integer.")
    return str(int(number))

def _bh_date(value: Any) -> date:
    parsed=pd.to_datetime(value,errors="coerce")
    if pd.isna(parsed): raise ProcessingValidationError("Bhavcopy contains an invalid date.")
    return parsed.date()

def _mii_expiry(value: Any) -> date:
    seconds=_number(value,"MII XpryDt")
    try: return (datetime(1980,1,1)+timedelta(seconds=int(seconds))).date()
    except (OverflowError,ValueError): raise ProcessingValidationError("MII contains an invalid expiry.") from None

def _bh_strike(value: Any) -> float:
    return _number(value,"Bhavcopy StrkPric")

def _mii_strike(value: Any) -> float:
    return _number(value,"MII StrkPric")/100.0

def _option_type(value: Any) -> str:
    result=str(value).strip().upper()
    if result not in {"CE","PE"}: raise ProcessingValidationError("Option type must be CE or PE.")
    return result

def normalize_index(frame: pd.DataFrame, trading_date: date) -> dict:
    required={"Index Name","Index Date","Open Index Value","High Index Value","Low Index Value","Closing Index Value"}
    _required(frame,required,"NIFTY 50 index CSV")
    matches=frame[frame["Index Name"].astype(str).str.strip().str.casefold()=="nifty 50"]
    if len(matches)!=1: raise ProcessingValidationError("Expected exactly one NIFTY 50 index row.")
    row=matches.iloc[0]
    parsed=pd.to_datetime(row["Index Date"],dayfirst=True,errors="coerce")
    if pd.isna(parsed) or parsed.date()!=trading_date: raise ProcessingValidationError("NIFTY 50 index date does not match analysis date.")
    values={name:_number(row[column],f"NIFTY 50 {name}",allow_zero=False) for name,column in {
        "open":"Open Index Value","high":"High Index Value","low":"Low Index Value","close":"Closing Index Value"}.items()}
    if values["high"]<max(values["open"],values["low"],values["close"]) or values["low"]>min(values["open"],values["high"],values["close"]):
        raise ProcessingValidationError("NIFTY 50 OHLC relationship is invalid.")
    return {"trade_date":trading_date,"symbol":"NIFTY 50",**values}

def normalize_options(bhavcopy: pd.DataFrame, same_day_mii: pd.DataFrame, prior_mii: pd.DataFrame|None, trading_date: date, selected_expiry: date, index_close: float) -> list[dict]:
    required_bh={"TradDt","FinInstrmId","TckrSymb","OptnTp","XpryDt","StrkPric","OpnPric","HghPric","LwPric","ClsPric","TtlTradgVol","OpnIntrst","UndrlygPric"}
    required_mii={"FinInstrmId","TckrSymb","OptnTp","XpryDt","StrkPric"}
    _required(bhavcopy,required_bh,"F&O Bhavcopy")
    _required(same_day_mii,required_mii,"MII contract master")
    options=bhavcopy[(bhavcopy["TckrSymb"].astype(str).str.strip().str.upper()=="NIFTY") & bhavcopy["OptnTp"].astype(str).str.strip().str.upper().isin(["CE","PE"])].copy()
    if options.empty: raise ProcessingValidationError("No NIFTY CE/PE option records found.")
    mapped={}
    def add_master(frame: pd.DataFrame, source_kind: str):
        _required(frame,required_mii,source_kind)
        subset=frame[(frame["TckrSymb"].astype(str).str.strip().str.upper()=="NIFTY") & frame["OptnTp"].astype(str).str.strip().str.upper().isin(["CE","PE"])]
        seen=set()
        for _,row in subset.iterrows():
            cid=_instrument_id(row["FinInstrmId"])
            if cid in seen: raise ProcessingValidationError(f"Duplicate NIFTY instrument ID {cid} in {source_kind}.")
            seen.add(cid)
            mapped[cid]={"expiry":_mii_expiry(row["XpryDt"]),"strike":_mii_strike(row["StrkPric"]),"option_type":_option_type(row["OptnTp"]),"source_kind":source_kind}
    add_master(same_day_mii,"mii_contract")
    if prior_mii is not None and not prior_mii.empty:
        # Same-day IDs have precedence. The prior snapshot is used only for IDs absent on the selected date.
        prior_required=required_mii
        _required(prior_mii,prior_required,"Previous-session MII contract master")
        subset=prior_mii[(prior_mii["TckrSymb"].astype(str).str.strip().str.upper()=="NIFTY") & prior_mii["OptnTp"].astype(str).str.strip().str.upper().isin(["CE","PE"])]
        prior_seen=set()
        for _,row in subset.iterrows():
            cid=_instrument_id(row["FinInstrmId"])
            if cid in prior_seen: raise ProcessingValidationError(f"Duplicate NIFTY instrument ID {cid} in previous-session MII.")
            prior_seen.add(cid)
            if cid not in mapped: mapped[cid]={"expiry":_mii_expiry(row["XpryDt"]),"strike":_mii_strike(row["StrkPric"]),"option_type":_option_type(row["OptnTp"]),"source_kind":"previous_session_mii_contract"}
    records=[]; seen=set()
    for _,row in options.iterrows():
        if _bh_date(row["TradDt"])!=trading_date: raise ProcessingValidationError("Bhavcopy contains a record for a different trading date.")
        cid=_instrument_id(row["FinInstrmId"])
        if cid in seen: raise ProcessingValidationError(f"Duplicate NIFTY option instrument ID {cid} in Bhavcopy.")
        seen.add(cid)
        contract=mapped.get(cid)
        if contract is None: raise ProcessingValidationError(f"Unmatched NIFTY option instrument ID {cid}.")
        expiry=_bh_date(row["XpryDt"]); strike=_bh_strike(row["StrkPric"]); kind=_option_type(row["OptnTp"])
        if (expiry,strike,kind)!=(contract["expiry"],contract["strike"],contract["option_type"]):
            raise ProcessingValidationError(f"Contract metadata mismatch for instrument ID {cid}.")
        if expiry!=selected_expiry: continue
        volume=_number(row["TtlTradgVol"],"TtlTradgVol"); oi=_number(row["OpnIntrst"],"OpnIntrst")
        underlying=_number(row["UndrlygPric"],"UndrlygPric",allow_zero=False)
        if not math.isclose(underlying,index_close,rel_tol=0,abs_tol=1e-8): raise ProcessingValidationError(f"Underlying close does not match NIFTY 50 close for instrument ID {cid}.")
        prices={name:_number(row[column],column) for name,column in {"open":"OpnPric","high":"HghPric","low":"LwPric","close":"ClsPric"}.items()}
        if volume>0:
            if min(prices.values())<=0: raise ProcessingValidationError(f"Traded option {cid} has non-positive OHLC.")
            if prices["high"]<max(prices.values()) or prices["low"]>min(prices.values()): raise ProcessingValidationError(f"Invalid traded-option OHLC for instrument ID {cid}.")
        elif any(prices[k]!=0 for k in ("open","high","low")):
            raise ProcessingValidationError(f"Zero-volume option {cid} must have zero open/high/low, consistent with Phase 1 audit.")
        records.append({"trade_date":trading_date,"symbol":"NIFTY","instrument_id":cid,"expiry":expiry,"strike":strike,"option_type":kind,**prices,"volume":int(volume) if volume.is_integer() else volume,"open_interest":int(oi) if oi.is_integer() else oi,"underlying_close":underlying,"contract_source":contract["source_kind"]})
    if not records: raise ProcessingValidationError(f"No NIFTY CE/PE records found for selected expiry {selected_expiry.isoformat()}.")
    return records
