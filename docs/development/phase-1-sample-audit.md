# Phase 1 — NSE sample data audit (19-Nov-2026)

**Audit run:** 20-Nov-2026  
**Scope:** One complete F&O UDiFF Bhavcopy and same-day legacy FO MII contract-master sample. This is not the full 22-session audit.

## Source files

- `BhavCopy_NSE_FO_0_0_0_20261119_F_0000.csv.zip`
- `NSE_FO_contract_19112026.csv.gz`
- `NSE_FO_spdcontract_19112026.csv.gz` is the spread-contract file, not the standard contract master.
- `OPTIDX_NIFTY_CE_08-Jan-2026_TO_23-Jan-2026.csv` is a narrow CE/one-strike sample and does not establish full CE/PE coverage.

## Verified sample results

| Check | Result |
|---|---:|
| Total Bhavcopy rows | 44,543 |
| NIFTY CE/PE Bhavcopy rows | 2,106 |
| CE / PE rows | 1,045 / 1,061 |
| Distinct expiries | 18 |
| Bhavcopy distinct IDs / duplicate ID rows | 2,106 / 0 |
| Zero-volume option rows | 613 |
| MII NIFTY CE/PE rows | 4,315 |
| MII CE / PE rows | 2,150 / 2,165 |
| MII distinct IDs / duplicate ID rows | 4,315 / 0 |
| Matched IDs | 2,106 |
| Expiry matches | 2,106 / 2,106 |
| Strike matches | 2,106 / 2,106 |
| Option-type matches | 2,106 / 2,106 |

## Resolved parser issues

### 1. Expiry epoch

The initial audit incorrectly interpreted MII `XpryDt` as Unix seconds from 1970. NSE Data & Analytics Master Data Specification v1.5 (01-Jul-2024) says time fields are seconds from midnight 01-Jan-1980 unless otherwise specified; the F&O contract-master expiry field is explicitly seconds elapsed from 01-Jan-1980. Applying that epoch makes all 2,106 matched option expiry dates agree with the Bhavcopy. Example: `1483021800` becomes `2026-12-29 14:30:00`, whose date matches `2026-12-29`.

### 2. Strike scaling

NSE's same master specification says FO price fields are in paise and must be divided by 100 to obtain rupees. The observed MII `StrkPric / 100` therefore matches the Bhavcopy for all 2,106 matched option IDs. Keep raw and normalized values separately. Apply this only to the legacy MII FO format, not blindly to UDiFF or other report formats.

Official specification: https://nsearchives.nseindia.com/web/sites/default/files/inline-files/NSE_MasterData_Technical_Specifications.pdf

## Data handling decisions

- Preserve zero-volume rows; zero traded volume is not missing data.
- Keep daily MII contract-master snapshots separate from Bhavcopy observations. The MII sample has 4,315 option rows while the Bhavcopy has 2,106.
- Use `FinInstrmId` as a candidate cross-file key and validate expiry, symbol, option type and normalized strike.
- Preserve original source files and record report date, source, download timestamp, byte size and SHA-256.
- Do not automate NSE website collection until the permitted acquisition method is confirmed.

## Still open

1. Obtain the remaining 21 sessions of F&O Bhavcopy and matching daily MII contract master for the approved 22-session window.
2. Obtain matching 22-session NIFTY 50 historical index OHLC.
3. Re-run the documented epoch and strike checks across all 22 sessions; quarantine mismatches.
4. Resolve the UI cutoff-time semantics: EOD-only reports cannot reconstruct arbitrary intraday snapshots. Either cutoff must be an EOD-compatible reporting boundary, or the data scope needs an approved intraday source.
5. Reconcile `main` and `phase-0-foundation` before merging Phase 1. They are diverged; the only main-side file difference identified is `.github/workflows/ci.yml`. Do not reset or blindly merge either branch.

## Reproducibility

Run the read-only audit utility:

```bash
python scripts/data/phase1_sample_audit.py --bhavcopy /path/to/BhavCopy_NSE_FO_0_0_0_YYYYMMDD_F_0000.csv.zip --contract-master /path/to/NSE_FO_contract_ddmmyyyy.csv.gz
```

No market-data archives are included in this repository.
