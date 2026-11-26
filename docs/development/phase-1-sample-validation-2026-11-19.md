# Phase 1 — 19-Nov-2026 Sample Validation

## Status

**Partial sample validation — two of the three core source types have been audited.** This is not a completed three-source end-to-end run and is not the 22-session audit.

Sample audit record: `Phase1_Sample_Audit_2026-11-19.md` (audit date 20-Nov-2026).

## Core source checklist

| Core source | Sample file / source | Status |
|---|---|---|
| F&O UDiFF Common Bhavcopy Final | `BhavCopy_NSE_FO_0_0_0_20261119_F_0000.csv.zip` | Audited in the existing one-session sample |
| F&O-MII NSE Exclusive Contract File | `NSE_FO_contract_19112026.csv.gz` | Audited in the existing one-session sample |
| NIFTY 50 Historical Index OHLC | Official NIFTY Indices historical-data CSV for 2026-11-19 | Not present in the inspected sample; pending |

The spread-contract file `NSE_FO_spdcontract_19112026.csv.gz` is not a substitute for the standard MII contract master and is excluded from the core source list. A narrow CE-only option report is not a substitute for the full NIFTY CE/PE coverage in the UDiFF Bhavcopy.

## Existing Bhavcopy sample results

| Check | Result |
|---|---:|
| Total Bhavcopy rows | 44,543 |
| NIFTY CE/PE rows | 2,106 |
| CE rows | 1,045 |
| PE rows | 1,061 |
| Distinct NIFTY option expiries | 18 |
| Distinct NIFTY option instrument IDs | 2,106 |
| Zero-volume NIFTY option rows | 613 |

Zero-volume rows must be retained and classified as no-trade, not missing data.

## Existing MII contract-master cross-check

| Check | Result |
|---|---:|
| NIFTY CE/PE rows in MII master | 4,315 |
| CE / PE rows | 2,150 / 2,165 |
| `PrtdToTrad=1` / `PrtdToTrad=0` | 2,205 / 2,110 |
| Bhavcopy NIFTY option IDs found in MII | 2,106 / 2,106 |
| Option type match | 2,106 / 2,106 |
| Strike match after legacy MII paise-to-rupee conversion | 2,106 / 2,106 |
| Expiry match using legacy MII epoch | 2,106 / 2,106 |
| Duplicate NIFTY option IDs in Bhavcopy and MII | 0 reported in each |

### Format-specific parsing rules established by this sample

- For the identified legacy MII contract-master format, interpret `XpryDt` as seconds from midnight 01-Jan-1980.
- For the identified legacy MII FO price/strike field, convert paise to rupees by dividing by 100.
- These conversions must only be applied after positively identifying the legacy MII format. Do not apply them blindly to UDiFF or another contract-master format.
- Preserve source values and normalized values side by side, with parser version and validation status.
- Keep contract-master universe separate from daily traded Bhavcopy observations. Do not assume the Bhavcopy contains every listed contract.

## Remaining work for the 19-Nov sample

1. Manually obtain the official NIFTY 50 historical OHLC CSV row/file for 19-Nov-2026, subject to applicable data-use terms.
2. Verify the CSV date and NIFTY 50 identity; validate Open, High, Low, Close are numeric and satisfy basic OHLC consistency (High >= max(Open, Close), Low <= min(Open, Close), High >= Low).
3. Record original filename, source page/URL, byte size, SHA-256 and acquisition timestamp for all three core inputs.
4. Run the three-source date-alignment check.
5. Produce one consolidated sample manifest and audit report. Do not claim the sample is end-to-end complete until the index OHLC input is verified.

## Gate before 22-session expansion

Proceed to the remaining sessions only after:
- the NIFTY 50 OHLC input for this sample is verified;
- all three core sources align to 2026-11-19;
- the parser rules pass the sample checks;
- the applicable terms permit the intended manual acquisition, storage, processing, and retention.

## Limitations

- This report records existing sample-audit results; it does not represent a new download performed in this step.
- No 19-Nov NIFTY 50 OHLC CSV was present in the inspected sample audit.
- No 22-session download or audit is claimed.
- No raw market-data archive is stored in this document or committed to the repository.
