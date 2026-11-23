"""Manifest-backed Phase 3 processing pipeline; source files are never modified."""
from __future__ import annotations
from datetime import date
import gzip
import zipfile
import pandas as pd
from app.modules.user_config import archive as archive_reader
from app.modules.data_processing.normalization import normalize_index, normalize_options
from app.modules.data_validation.validators import validate_normalized_payload

def _read_zip_csv(path):
    with zipfile.ZipFile(path) as archive:
        members=[name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(members)!=1: raise archive_reader.ArchiveValidationError("Bhavcopy ZIP must contain exactly one CSV.")
        with archive.open(members[0]) as stream: return pd.read_csv(stream,low_memory=False)

def _read_gzip_csv(path):
    with gzip.open(path,"rb") as stream: return pd.read_csv(stream,low_memory=False)

def _read_csv(path):
    return pd.read_csv(path,low_memory=False)

def build_session_payload(trading_date: date, selected_expiry: date):
    sources=archive_reader._sources(trading_date)
    bh,mii,index=_read_zip_csv(sources[0].path),_read_gzip_csv(sources[1].path),_read_csv(sources[2].path)
    resolved=archive_reader.resolve_configuration(trading_date,selected_expiry)
    index_bar=normalize_index(index,trading_date)
    index_bar["source_sha256"]=sources[2].manifest_entry["sha256"]
    index_bar["source_filename"]=sources[2].path.name
    prior=pd.DataFrame()
    previous_sources=[s for s in resolved.sources if s.kind=="previous_session_mii_contract"]
    if previous_sources: prior=_read_gzip_csv(previous_sources[0].path)
    option_bars=normalize_options(bh,mii,prior,trading_date,selected_expiry,index_bar["close"])
    for record in option_bars:
        record["source_sha256"]=sources[0].manifest_entry["sha256"]
        record["source_filename"]=sources[0].path.name
    summary=validate_normalized_payload(index_bar,option_bars,trading_date,selected_expiry)
    return {"index_bar":index_bar,"option_bars":option_bars,"validation_summary":summary,
        "sources":[{"kind":s.kind,"trade_date":s.trade_date.isoformat(),"filename":s.path.name,"sha256":s.manifest_entry.get("sha256"),"bytes":s.manifest_entry.get("bytes"),"source_url":s.manifest_entry.get("url")} for s in resolved.sources]}
