"""Read-only resolver for the approved Phase 1 local archive layout."""
from __future__ import annotations
import gzip, hashlib, json, math, os, zipfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
import pandas as pd

class ArchiveError(Exception): pass
class ArchiveUnavailable(ArchiveError): pass
class ArchiveValidationError(ArchiveError): pass

@dataclass(frozen=True)
class SourceFile:
    kind: str
    trade_date: date
    path: Path
    manifest_entry: dict[str, Any]

@dataclass(frozen=True)
class ResolvedConfiguration:
    analysis_date: date
    available_expiries: tuple[date, ...]
    nearest_expiry: date
    selected_expiry: date
    expiry_selection_mode: str
    automatic_fallback: bool
    fallback_reason: str | None
    sources: tuple[SourceFile, ...]

def archive_root() -> Path:
    return Path(os.getenv("DATA_STORAGE_PATH", "../local_data")).expanduser().resolve()

def _load_manifest(path: Path) -> dict:
    if not path.is_file():
        raise ArchiveUnavailable(f"Historical archive manifest not found: {path}. Set DATA_STORAGE_PATH to the extracted Phase 1 archive root.")
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: raise ArchiveValidationError(f"Cannot read archive manifest {path.name}: {exc}") from exc

def _entry_map(manifest: dict) -> dict[str, dict]:
    entries = manifest.get("results")
    if not isinstance(entries, list): raise ArchiveValidationError("Archive manifest is missing its results list.")
    return {str(item.get("date")): item for item in entries if isinstance(item, dict) and item.get("date")}

def _safe_path(root: Path, entry: dict, fallback: str) -> Path:
    candidate = (root / (entry.get("path") or fallback)).resolve()
    if candidate != root and root not in candidate.parents: raise ArchiveValidationError("Manifest path escapes the configured archive root.")
    return candidate

def _verify(path: Path, entry: dict, label: str) -> None:
    if entry.get("status") != "DOWNLOADED": raise ArchiveUnavailable(f"{label} is not marked DOWNLOADED in its manifest.")
    if not path.is_file(): raise ArchiveUnavailable(f"Required {label} file is missing: {path}")
    if entry.get("bytes") is None or not entry.get("sha256"): raise ArchiveValidationError(f"{label} manifest entry lacks byte-size or SHA-256 provenance.")
    digest, size = hashlib.sha256(), 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk); digest.update(chunk)
    if size != int(entry["bytes"]): raise ArchiveValidationError(f"{label} file size mismatch for {path.name}.")
    if digest.hexdigest().lower() != str(entry["sha256"]).lower(): raise ArchiveValidationError(f"{label} SHA-256 mismatch for {path.name}.")

def _sources(day: date) -> tuple[SourceFile, SourceFile, SourceFile]:
    root = archive_root()
    fo = _entry_map(_load_manifest(root / "artifacts/manifests/fo-download-manifest.json")).get(day.isoformat())
    ix = _entry_map(_load_manifest(root / "artifacts/manifests/nifty50-download-manifest.json")).get(day.isoformat())
    if not fo or not ix: raise ArchiveUnavailable(f"No complete Phase 1 manifest coverage for {day.isoformat()}.")
    ymd, dmy = day.strftime("%Y%m%d"), day.strftime("%d%m%Y")
    bh, cm = fo.get("bhavcopy") or {}, fo.get("mii_contract") or {}
    bhp = _safe_path(root, bh, f"artifacts/raw/nse/fo_bhavcopy/BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv.zip")
    cmp = _safe_path(root, cm, f"artifacts/raw/nse/mii_contracts/NSE_FO_contract_{dmy}.csv.gz")
    ixp = _safe_path(root, ix, f"artifacts/raw/nse/nifty50_ohlc/ind_close_all_{dmy}.csv")
    _verify(bhp, bh, "F&O Bhavcopy"); _verify(cmp, cm, "MII Contract Master"); _verify(ixp, ix, "NIFTY 50 OHLC")
    return (SourceFile("fo_bhavcopy", day, bhp, bh), SourceFile("mii_contract", day, cmp, cm), SourceFile("nifty50_ohlc", day, ixp, ix))

def available_analysis_dates() -> list[date]:
    root = archive_root()
    fo = _entry_map(_load_manifest(root / "artifacts/manifests/fo-download-manifest.json"))
    ix = _entry_map(_load_manifest(root / "artifacts/manifests/nifty50-download-manifest.json"))
    dates = []
    for raw in sorted(set(fo) & set(ix)):
        try:
            day = date.fromisoformat(raw)
            _sources(day)
            dates.append(day)
        except (ValueError, ArchiveError): continue
    return dates

def _read_bhavcopy(path: Path) -> pd.DataFrame:
    try:
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if n.lower().endswith(".csv")]
            if len(names) != 1: raise ArchiveValidationError("Bhavcopy ZIP must contain exactly one CSV.")
            with z.open(names[0]) as stream: return pd.read_csv(stream, low_memory=False)
    except (OSError, zipfile.BadZipFile, pd.errors.ParserError) as exc: raise ArchiveValidationError(f"Cannot parse Bhavcopy {path.name}: {exc}") from exc

def _read_mii(path: Path) -> pd.DataFrame:
    try:
        with gzip.open(path, "rb") as stream: return pd.read_csv(stream, low_memory=False)
    except (OSError, EOFError, pd.errors.ParserError) as exc: raise ArchiveValidationError(f"Cannot parse MII contract master {path.name}: {exc}") from exc

def _id(value: Any) -> str | None:
    try: return str(int(float(value)))
    except (TypeError, ValueError, OverflowError): return None

def _mii_expiry(value: Any) -> date | None:
    try: return (datetime(1980, 1, 1) + timedelta(seconds=int(float(value)))).date()
    except (TypeError, ValueError, OverflowError): return None

def _bh_expiry(value: Any) -> date | None:
    parsed = pd.to_datetime(value, errors="coerce")
    return None if pd.isna(parsed) else parsed.date()

def _resolve_expiries(day: date, sources: tuple[SourceFile, ...]) -> tuple[list[date], date, SourceFile | None]:
    bh, mii = _read_bhavcopy(sources[0].path), _read_mii(sources[1].path)
    req_bh = {"TradDt", "FinInstrmId", "TckrSymb", "OptnTp", "XpryDt", "StrkPric"}
    req_mii = {"FinInstrmId", "TckrSymb", "OptnTp", "XpryDt", "StrkPric"}
    if req_bh - set(bh.columns) or req_mii - set(mii.columns):
        raise ArchiveValidationError("Contract metadata schema is missing required Bhavcopy/MII fields.")
    trade_dates = pd.to_datetime(bh["TradDt"], errors="coerce").dropna().dt.date.unique()
    if len(trade_dates) != 1 or trade_dates[0] != day:
        raise ArchiveValidationError("Bhavcopy trade date does not match requested analysis date.")
    b = bh[(bh.TckrSymb.astype(str).str.upper() == "NIFTY") & bh.OptnTp.astype(str).str.upper().isin(["CE", "PE"])]
    m = mii[(mii.TckrSymb.astype(str).str.upper() == "NIFTY") & mii.OptnTp.astype(str).str.upper().isin(["CE", "PE"])]
    if b["FinInstrmId"].map(_id).duplicated().any() or m["FinInstrmId"].map(_id).duplicated().any():
        raise ArchiveValidationError("Duplicate NIFTY option instrument IDs found in Bhavcopy or MII.")
    mapped: dict[str, tuple[date, float, str]] = {}
    master_expiries: set[date] = set()
    for row in m.to_dict("records"):
        cid, exp = _id(row.get("FinInstrmId")), _mii_expiry(row.get("XpryDt"))
        try: strike = float(row.get("StrkPric")) / 100.0
        except (TypeError, ValueError): strike = None
        if strike is not None and not math.isfinite(strike): strike = None
        option_type = str(row.get("OptnTp", "")).upper()
        if exp and exp >= day: master_expiries.add(exp)
        if cid and exp and strike is not None: mapped[cid] = (exp, strike, option_type)
    bh_rows = b[["FinInstrmId", "XpryDt"]].to_dict("records")
    bh_ids = {_id(row["FinInstrmId"]) for row in bh_rows}
    if None in bh_ids:
        raise ArchiveValidationError("Bhavcopy contains a NIFTY option row without a valid instrument ID.")
    missing_ids = {cid for cid in bh_ids if cid not in mapped}
    previous_source = None
    if missing_ids:
        root = archive_root()
        manifest = _load_manifest(root / "artifacts/manifests/fo-download-manifest.json")
        manifest_entries = _entry_map(manifest)
        earlier = sorted((raw for raw in manifest_entries if raw < day.isoformat()), reverse=True)
        for raw_day in earlier:
            entry = manifest_entries[raw_day].get("mii_contract") or {}
            try:
                prior_day = date.fromisoformat(raw_day)
                prior_path = _safe_path(root, entry, f"artifacts/raw/nse/mii_contracts/NSE_FO_contract_{prior_day:%d%m%Y}.csv.gz")
                _verify(prior_path, entry, "Previous-session MII Contract Master")
                prior = _read_mii(prior_path)
                prior = prior[(prior.TckrSymb.astype(str).str.upper() == "NIFTY") & prior.OptnTp.astype(str).str.upper().isin(["CE", "PE"])]
                for row in prior.to_dict("records"):
                    cid, exp = _id(row.get("FinInstrmId")), _mii_expiry(row.get("XpryDt"))
                    try: strike = float(row.get("StrkPric")) / 100.0
                    except (TypeError, ValueError): strike = None
                    if strike is not None and not math.isfinite(strike): strike = None
                    option_type = str(row.get("OptnTp", "")).upper()
                    if cid in missing_ids and exp and strike is not None:
                        mapped[cid] = (exp, strike, option_type)
                        if exp >= day: master_expiries.add(exp)
                previous_source = SourceFile("previous_session_mii_contract", prior_day, prior_path, entry)
                if not (missing_ids - set(mapped)): break
            except ArchiveError:
                continue
    unresolved = {cid for cid in bh_ids if cid and cid not in mapped}
    if unresolved:
        raise ArchiveValidationError(f"{len(unresolved)} NIFTY option contract IDs could not be reconciled to same-day or previous-session MII.")
    bh_expiries = {_bh_expiry(value) for value in b.XpryDt if _bh_expiry(value)}
    matched_expiries = set()
    for row in b[["FinInstrmId", "XpryDt", "StrkPric", "OptnTp"]].to_dict("records"):
        cid, bh_exp = _id(row["FinInstrmId"]), _bh_expiry(row["XpryDt"])
        mii_exp, mii_strike, mii_type = mapped[cid]
        try: bh_strike = float(row["StrkPric"])
        except (TypeError, ValueError): bh_strike = None
        if bh_strike is not None and not math.isfinite(bh_strike): bh_strike = None
        if bh_exp != mii_exp:
            raise ArchiveValidationError(f"Contract expiry mismatch for instrument ID {cid}.")
        if bh_strike is None or abs(bh_strike - mii_strike) > 1e-8:
            raise ArchiveValidationError(f"Contract strike mismatch for instrument ID {cid}.")
        if str(row["OptnTp"]).upper() != mii_type:
            raise ArchiveValidationError(f"Contract option-type mismatch for instrument ID {cid}.")
        if mii_exp >= day and mii_exp in bh_expiries:
            matched_expiries.add(mii_exp)
    available = sorted(matched_expiries)
    if not available:
        raise ArchiveUnavailable("No NIFTY CE/PE expiry is both present in Bhavcopy and reconciled to an MII contract snapshot.")
    nearest_master = min(master_expiries) if master_expiries else available[0]
    return available, nearest_master, previous_source

def resolve_configuration(day: date, expiry: date | None = None) -> ResolvedConfiguration:
    if day > date.today():
        raise ArchiveValidationError("Analysis date must be a completed historical trading session.")
    sources = _sources(day)
    expiries, nearest_master, previous_source = _resolve_expiries(day, sources)
    if expiry is not None and expiry not in expiries:
        raise ArchiveValidationError(f"Expiry {expiry.isoformat()} is unavailable for {day.isoformat()}. Available expiries: {', '.join(x.isoformat() for x in expiries)}.")
    selected = expiry or (nearest_master if nearest_master in expiries else expiries[0])
    fallback = expiry is None and selected != nearest_master
    reason = (f"Nearest MII expiry {nearest_master.isoformat()} has no matching NIFTY CE/PE Bhavcopy contracts; selected next available expiry {selected.isoformat()}."
              if fallback else None)
    resolved_sources = sources + ((previous_source,) if previous_source else ())
    return ResolvedConfiguration(day, tuple(expiries), nearest_master, selected, "MANUAL" if expiry else "AUTO", fallback, reason, resolved_sources)

def validate_source_content(sources: tuple[SourceFile, SourceFile, SourceFile]) -> dict:
    bh, mii, ix = _read_bhavcopy(sources[0].path), _read_mii(sources[1].path), pd.read_csv(sources[2].path)
    required_ix = {"Index Name", "Index Date", "Open Index Value", "High Index Value", "Low Index Value", "Closing Index Value"}
    if required_ix - set(ix.columns): raise ArchiveValidationError(f"NIFTY 50 CSV missing columns: {sorted(required_ix - set(ix.columns))}.")
    rows = ix[ix["Index Name"].astype(str).str.strip().str.lower() == "nifty 50"]
    if len(rows) != 1: raise ArchiveValidationError(f"Expected exactly one NIFTY 50 index row; found {len(rows)}.")
    row = rows.iloc[0]; idx_date = pd.to_datetime(row["Index Date"], dayfirst=True, errors="coerce")
    if pd.isna(idx_date) or idx_date.date() != sources[2].trade_date: raise ArchiveValidationError("NIFTY 50 index date does not match analysis date.")
    o, h, l, c = [float(row[k]) for k in ("Open Index Value", "High Index Value", "Low Index Value", "Closing Index Value")]
    if not (l <= min(o, h, c) and h >= max(o, l, c)): raise ArchiveValidationError("NIFTY 50 OHLC relationship is invalid.")
    req_bh = {"FinInstrmId", "TckrSymb", "OptnTp", "XpryDt", "StrkPric", "ClsPric", "TtlTradgVol", "OpnIntrst", "UndrlygPric"}
    req_mii = {"FinInstrmId", "TckrSymb", "OptnTp", "XpryDt", "StrkPric"}
    if req_bh - set(bh.columns) or req_mii - set(mii.columns): raise ArchiveValidationError("F&O source schema is missing required Phase 1 fields.")
    nifty_options = bh[(bh.TckrSymb.astype(str).str.upper() == "NIFTY") & bh.OptnTp.astype(str).str.upper().isin(["CE", "PE"])]
    underlying = pd.to_numeric(nifty_options["UndrlygPric"], errors="coerce").dropna().unique()
    if len(underlying) != 1 or abs(float(underlying[0]) - c) > 1e-8:
        raise ArchiveValidationError("NIFTY option underlying price does not reconcile to the NIFTY 50 daily close.")
    return {"nifty50_index_date": idx_date.date().isoformat(), "nifty50_ohlc": {"open": o, "high": h, "low": l, "close": c}, "bhavcopy_rows": int(len(bh)), "mii_contract_rows": int(len(mii)), "nifty_option_rows": int(len(nifty_options)), "underlying_close_reconciled": True}
