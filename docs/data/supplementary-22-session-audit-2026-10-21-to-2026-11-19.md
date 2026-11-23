# NSE Supplementary 22-Session Historical Audit

**Audit period:** 21-Oct-2026 to 19-Nov-2026  
**Sessions:** 22 (includes 08-Nov-2026 special Muhurat session; excludes 10-Nov holiday)  
**Execution:** 23-Nov-2026  
**Branch:** `phase-2-supplementary-report-sample-audit`  
**Purpose:** Verify retrieval, schema stability, internal consistency and relationship to core NIFTY EOD data for Participant-wise Open Interest and F&O Daily Volatility. This is not predictive validation.

## Executive result

All 22 expected sessions were successfully retrieved for both supplementary reports. The corresponding 22 Bhavcopy files were also downloaded for an independent underlying-close check.

| Check | Result |
|---|---:|
| Participant-wise OI reports downloaded | 22/22 |
| Daily Volatility reports downloaded | 22/22 |
| F&O Bhavcopy files downloaded | 22/22 |
| Participant OI schema checks passed | 22/22 |
| Daily Volatility schema checks passed | 22/22 |
| NIFTY underlying close matched Bhavcopy | 22/22 |
| Participant OI TOTAL-row reconciliation warnings | 18/22 sessions |
| Maximum OI TOTAL-row discrepancy | 1 contract |
| Daily Volatility NIFTY rows | Exactly 1 per session |
| Daily Volatility formula recomputation | 22/22 within published rounding precision |

Original source files are retained unchanged in the workflow artifact. No raw market data was committed to Git.

## 1. Download route and reproducibility

The direct NSE archive-host routes used in the successful one-day test were applied across the 22 sessions:

- Participant OI: `https://nsearchives.nseindia.com/content/nsccl/fao_participant_oi_DDMMYYYY.csv`
- Daily Volatility: `https://nsearchives.nseindia.com/archives/nsccl/volt/FOVOLT_DDMMYYYY.csv`
- Core reconciliation source: `https://archives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_YYYYMMDD_F_0000.csv.zip`

Each response was checked for HTTP success, non-empty payload and expected CSV/ZIP structure. Original bytes, URLs, byte sizes and SHA-256 digests are included in the JSON audit output and the raw files are retained under `raw/<trade-date>/`.

**GitHub Actions evidence**
- Run: [45145254774](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/actions/runs/45145254774)
- Artifact: `14803727787`, `nse-supplementary-22-session-audit`
- Artifact size: 28,608,504 bytes
- Artifact SHA-256: `2c8218a27bcd95178477c2bfb2e953a583a24492276a149b55f5d11b0bc4df16`
- Artifact retention expiry shown by GitHub: 23-Dec-2026
- Artifact contains 68 files: 22 OI CSVs, 22 volatility CSVs, 22 Bhavcopy ZIPs, plus JSON and Markdown audit outputs.

## 2. Participant-wise Open Interest

### 2.1 Schema and coverage

All 22 files use the same 15-column schema and exactly five rows:
- Client
- DII
- FII
- Pro
- TOTAL

The 14 numeric measures cover long/short positions in index futures, stock futures, index calls/puts, stock calls/puts, and total long/short contracts. There were no missing numeric values in the checked fields.

### 2.2 Scope limitation

The report title and structure identify Equity Derivatives participant aggregates. It has no underlying symbol, expiry, strike or contract identifier. Consequently:
- It is not NIFTY-specific.
- It cannot identify the writer or buyer of a particular NIFTY option contract.
- Its long/short index-option totals aggregate across index products.
- It is not a substitute for contract-level Bhavcopy OI.

The participant categories can still describe broad positioning changes across the Equity Derivatives segment, provided the application labels that scope explicitly.

### 2.3 TOTAL-row reconciliation

On 18 of 22 sessions, the sum of Client + DII + FII + Pro differed from the published TOTAL row in one or more numeric columns. Every observed difference was exactly one contract in absolute value; no larger difference occurred.

This is a recurring source-level arithmetic discrepancy. The audit preserves the published values and records the differences. It does not silently adjust the TOTAL row or participant rows. The magnitude is tiny relative to the aggregate values, but its cause is not established.

### 2.4 Descriptive participant changes (not NIFTY signals)

The following start/end comparisons are for aggregate Equity Derivatives index-option fields only. “Net” here means the report's participant long contracts minus participant short contracts for that option side; it is not a NIFTY-only net position or a directional trading recommendation.

| Participant | Index call net, 21-Oct | Index call net, 19-Nov | Index put net, 21-Oct | Index put net, 19-Nov |
|---|---:|---:|---:|---:|
| Client | +389,918 | -30,158 | -826,431 | -329,077 |
| DII | +7,448 | +4,314 | +113,261 | +103,979 |
| FII | -341,527 | -99,941 | +597,220 | +332,376 |
| Pro | -55,839 | +125,784 | +115,949 | -107,279 |

These changes demonstrate that the report contains participant-category variation. They do not establish whether that variation predicts NIFTY direction, option premium decay, seller profitability or future volatility. A longer historical study and explicit out-of-sample testing would be needed.

**Assessment:** Retain as a supplementary research candidate only. If later used, feature names and dashboard labels must say “Equity Derivatives participant aggregate” and must not imply NIFTY-only positioning.

## 3. F&O Daily Volatility

### 3.1 Schema and coverage

All 22 files use the same 16-column schema. Total report row counts vary from 224 to 230, but each file contains exactly one NIFTY row.

The report supplies:
- Underlying close and previous close
- Underlying log return and previous/current daily volatility
- Underlying annualised volatility
- Futures close and previous close
- Futures log return and previous/current daily volatility
- Futures annualised volatility
- Applicable daily and annualised volatility

The NIFTY values were numeric on all 22 sessions.

### 3.2 Reconciliation against Bhavcopy

The NIFTY underlying close in FOVOLT matched the unique NIFTY underlying price carried in the corresponding F&O Bhavcopy on all 22/22 sessions, to the paisa.

The underlying previous-close field also chained to the preceding selected session's underlying close on all 21 transitions.

The futures previous-close field chained to the preceding selected session's futures close on 20/21 transitions. The one mismatch is 27-Oct-2026: the 27-Oct FOVOLT futures previous close is 22,891.40, while the 26-Oct FOVOLT futures close is 22,767.30. The reason is not established in this audit; possible contract-selection/roll methodology must be checked with NSE's field definition before using this futures series as a continuous price series.

### 3.3 Volatility formula check

The published daily volatility fields were recomputed from the supplied previous-day volatility and log-return fields using the report's stated EWMA-style formula:

`CurrentDailyVol = sqrt(0.995 × PreviousDailyVol² + 0.005 × LogReturn²)`

Applicable daily volatility was recomputed as the maximum of underlying and futures daily volatility, and applicable annualised volatility as the maximum of their annualised values. All 22 NIFTY rows matched within the precision of the published rounded fields. Maximum absolute annualised-value difference was approximately 0.0000055.

### 3.4 NIFTY volatility range

The report's applicable annualised NIFTY volatility over the sample:
- Minimum: 16.093063% on 28-Oct-2026
- Maximum: 16.704367% on 06-Nov-2026
- Mean across 22 sessions: approximately 16.370162%
- 21-Oct value: 16.226878%
- 19-Nov value: 16.509766%

This is an underlying/futures volatility reference, not option implied volatility. It is not a strike-wise IV surface, does not provide CE/PE premium-specific IV, and must not be labelled or used as option IV.

**Assessment:** Suitable as an optional exchange-published volatility-regime reference and cross-check against an independently calculated underlying-volatility feature. Before use, resolve or explicitly handle the 27-Oct futures previous-close discontinuity. Underlying volatility fields are better supported by this sample's close-to-close continuity checks than the futures series.

## 4. Recommended project treatment

1. Keep the mandatory Phase 1 source set unchanged: F&O UDiFF Bhavcopy Final, F&O MII Contract File and NIFTY 50 All Indices daily-close CSV.
2. Keep Participant OI as a research-only supplementary candidate for broad Equity Derivatives participant context. Do not use it as NIFTY-specific positioning.
3. Keep F&O Daily Volatility as an optional regime reference. Prefer the underlying-volatility fields for initial experimentation; do not call them option IV.
4. Do not make either report a prerequisite for an analysis run.
5. Do not feed either report into seller-trap labels, eight-scenario decisions, CE/PE premium triggers or ML training until a separate predictive-value study is designed and validated out of sample.
6. Preserve missing reports as unavailable/pending, never as zero.
7. Review applicable NSE terms and confirm a permitted acquisition method before implementing recurring collection. This one-off historical audit does not authorize an automated production downloader.

## 5. Limitations

- The sample is only 22 sessions and is a data-quality/schema audit, not a predictive backtest.
- Participant OI is broad Equity Derivatives aggregate data; it cannot identify NIFTY-specific writers or strikes.
- The one-contract TOTAL-row discrepancies recur and their cause is unknown.
- The 27-Oct futures previous-close discontinuity remains unexplained.
- A stable schema over this sample does not guarantee future schema stability or report publication timing.

## 6. Implementation and source references

- Audit script: `tools/audit_supplementary_22_sessions.py`
- Workflow: `.github/workflows/supplementary-22-session-audit.yml`
- JSON result: `audit-22-sessions.json` in the workflow artifact
- Session detail: `audit-22-sessions.md` in the workflow artifact
- One-day report comparison: `docs/data/supplementary-eod-sample-audit-2026-10-30.md`
- Phase 1 core source and row-level audit: `phase1-nse-fo-index-download-and-diagnostics` archive artifact

**Conclusion:** Both supplementary reports are now proven retrievable and structurally consistent across the selected 22 sessions. Daily Volatility has a clean NIFTY underlying-close reconciliation and internally consistent calculations. Participant OI has stable schema and participant categories but is aggregate-only, with recurring one-contract total-row discrepancies. These reports should remain optional research inputs, not production decision-engine dependencies.
