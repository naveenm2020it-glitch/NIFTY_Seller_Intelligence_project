"""Domain checks for normalized EOD payloads."""
from __future__ import annotations
from datetime import date
from typing import Any

class DataQualityError(ValueError): pass

def validate_normalized_payload(index_bar:dict[str,Any],option_bars:list[dict[str,Any]],trading_date:date,selected_expiry:date)->dict:
    if index_bar.get("trade_date")!=trading_date or index_bar.get("symbol")!="NIFTY 50":
        raise DataQualityError("Normalized index record does not match requested NIFTY 50 session.")
    if not option_bars:raise DataQualityError("Normalized option dataset is empty.")
    ids=set();ce=pe=zero=0
    for row in option_bars:
        if row["trade_date"]!=trading_date or row["symbol"]!="NIFTY" or row["expiry"]!=selected_expiry:
            raise DataQualityError("Normalized option record falls outside selected NIFTY session/expiry.")
        if row["instrument_id"] in ids:raise DataQualityError(f"Duplicate normalized instrument ID {row['instrument_id']}.")
        ids.add(row["instrument_id"])
        if row["option_type"]=="CE":ce+=1
        elif row["option_type"]=="PE":pe+=1
        else:raise DataQualityError("Normalized option has invalid option type.")
        if row["volume"]<0 or row["open_interest"]<0:raise DataQualityError("Negative volume or open interest is not permitted.")
        if row["volume"]==0:zero+=1
        if row["underlying_close"]!=index_bar["close"]:raise DataQualityError("Option underlying close does not reconcile to NIFTY 50 close.")
    return {"status":"PASSED","trade_date":trading_date.isoformat(),"selected_expiry":selected_expiry.isoformat(),"option_rows":len(option_bars),"ce_rows":ce,"pe_rows":pe,"zero_volume_rows":zero,"traded_rows":len(option_bars)-zero,"contract_source_counts":{kind:sum(row["contract_source"]==kind for row in option_bars) for kind in ("mii_contract","previous_session_mii_contract")}}
