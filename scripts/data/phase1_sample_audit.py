#!/usr/bin/env python3
"""Read-only one-session audit for NSE NIFTY FO Bhavcopy and MII contract master."""
import argparse
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

NSE_MII_EPOCH = datetime(1980, 1, 1)


def nse_mii_timestamp(value):
    """Convert legacy NSE MII seconds from 1980-01-01 to a timestamp."""
    if pd.isna(value):
        return pd.NaT
    return NSE_MII_EPOCH + timedelta(seconds=float(value))


def read_bhavcopy(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise ValueError(f"Expected exactly one CSV in {path.name}; found {len(csv_names)}")
        with archive.open(csv_names[0]) as stream:
            return pd.read_csv(stream, low_memory=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bhavcopy", required=True, type=Path)
    parser.add_argument("--contract-master", required=True, type=Path)
    args = parser.parse_args()

    bh = read_bhavcopy(args.bhavcopy)
    cm = pd.read_csv(args.contract_master, compression="gzip", low_memory=False)

    required_bh = {"FinInstrmId", "TckrSymb", "XpryDt", "StrkPric", "OptnTp", "TtlTradgVol"}
    required_cm = {"FinInstrmId", "TckrSymb", "XpryDt", "StrkPric", "OptnTp", "PrtdToTrad", "DelFlg"}
    if missing := required_bh - set(bh.columns):
        raise ValueError(f"Bhavcopy missing columns: {sorted(missing)}")
    if missing := required_cm - set(cm.columns):
        raise ValueError(f"Contract master missing columns: {sorted(missing)}")

    bh["FinInstrmId"] = pd.to_numeric(bh["FinInstrmId"], errors="coerce")
    cm["FinInstrmId"] = pd.to_numeric(cm["FinInstrmId"], errors="coerce")
    bh_nifty = bh[(bh["TckrSymb"] == "NIFTY") & bh["OptnTp"].isin(["CE", "PE"])].copy()
    cm_nifty = cm[(cm["TckrSymb"] == "NIFTY") & cm["OptnTp"].isin(["CE", "PE"])].copy()

    bh_nifty["XpryDt"] = pd.to_datetime(bh_nifty["XpryDt"], errors="coerce")
    bh_nifty["StrkPric"] = pd.to_numeric(bh_nifty["StrkPric"], errors="coerce")
    cm_nifty["XpryDt_epoch"] = pd.to_numeric(cm_nifty["XpryDt"], errors="coerce")
    cm_nifty["XpryDt_1980"] = cm_nifty["XpryDt_epoch"].map(nse_mii_timestamp)
    cm_nifty["StrkPric"] = pd.to_numeric(cm_nifty["StrkPric"], errors="coerce")

    matched = cm_nifty.merge(
        bh_nifty[["FinInstrmId", "XpryDt", "StrkPric", "OptnTp"]],
        on="FinInstrmId", how="inner", suffixes=("_mii", "_bhav")
    )
    matched["mii_strike_rupees"] = matched["StrkPric_mii"] / 100
    matched["expiry_matches"] = matched["XpryDt_1980"].dt.date == matched["XpryDt_bhav"].dt.date
    matched["strike_matches"] = (matched["mii_strike_rupees"] - matched["StrkPric_bhav"]).abs() < 1e-8
    matched["option_type_matches"] = matched["OptnTp_mii"] == matched["OptnTp_bhav"]

    print(f"Bhavcopy NIFTY CE/PE rows: {len(bh_nifty)}")
    print(f"  CE: {(bh_nifty['OptnTp'] == 'CE').sum()}; PE: {(bh_nifty['OptnTp'] == 'PE').sum()}")
    print(f"  Distinct expiries: {bh_nifty['XpryDt'].nunique()}")
    print(f"  Distinct instrument IDs: {bh_nifty['FinInstrmId'].nunique()}")
    print(f"  Duplicate instrument ID rows: {bh_nifty['FinInstrmId'].duplicated().sum()}")
    print(f"  Zero-volume rows: {(pd.to_numeric(bh_nifty['TtlTradgVol'], errors='coerce').fillna(0) == 0).sum()}")
    print(f"MII NIFTY CE/PE rows: {len(cm_nifty)}")
    print(f"  CE: {(cm_nifty['OptnTp'] == 'CE').sum()}; PE: {(cm_nifty['OptnTp'] == 'PE').sum()}")
    print(f"  Distinct instrument IDs: {cm_nifty['FinInstrmId'].nunique()}")
    print(f"  Duplicate instrument ID rows: {cm_nifty['FinInstrmId'].duplicated().sum()}")
    print(f"  PrtdToTrad counts: {cm_nifty['PrtdToTrad'].value_counts(dropna=False).to_dict()}")
    print(f"Matched instrument IDs: {len(matched)}")
    print(f"  Expiry matches using NSE 1980 epoch: {matched['expiry_matches'].sum()}/{len(matched)}")
    print(f"  Strike matches after FO paise-to-rupee conversion (/100): {matched['strike_matches'].sum()}/{len(matched)}")
    print(f"  Option-type matches: {matched['option_type_matches'].sum()}/{len(matched)}")


if __name__ == "__main__":
    main()
