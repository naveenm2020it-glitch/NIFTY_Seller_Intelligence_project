# NSE F&O EOD Report Inventory — Review Note

**Review date:** 23 November 2026  
**Project:** NIFTY Seller Intelligence  
**Branch:** `phase-2-user-config-orchestration`  
**Purpose:** Identify which official NSE EOD reports should be retained as core inputs, supplementary context, or deferred candidates. This is a research/inventory note, not authorization for automated NSE collection.

## 1. Evidence reviewed

1. Phase 1 closeout and audit on `phase-1-data-audit`: the 22-session archive already contains F&O UDiFF Bhavcopy, daily MII contract master and NIFTY 50 All Indices OHLC. The Phase 1 audit reconciled 43,966 NIFTY CE/PE Bhavcopy rows against contract-master snapshots, including the documented previous-session snapshot fallback.
2. NSE All Reports — Derivatives page: confirms that the F&O report catalogue includes participant-wise OI, participant-wise trading volumes, FII derivatives statistics, daily volatility, daily settlement prices, market activity, NCL OI, combined OI, combined delta-equivalent OI, SPAN and other risk/operational files.
3. NSE Data & Analytics, *Post Trade Data Technical Specification (Futures and Options Market)*, dated 03-Jan-2013, especially pages 6 and 12–15. This is an older specification. Use it as a field/nomenclature reference only; do not assume its publication timings or schema are unchanged without inspecting current sample files.

## 2. Existing core inputs — retain as mandatory

| Report | Current project status | Role |
|---|---|---|
| F&O UDiFF Common Bhavcopy Final (ZIP) | Phase 1 audited | Contract-level option/futures OHLC, settlement, volume, OI and underlying fields available in the UDiFF rows |
| F&O MII Contract File (GZ) | Phase 1 audited | Contract identity and metadata; expiry, strike and option type mapping |
| NSE Indices All Indices daily-close CSV | Phase 1 audited | NIFTY 50 daily OHLC and underlying cross-check |

These three remain the first-version mandatory EOD source set. Preserve raw bytes, source URL, report/trading date, retrieval timestamp, byte size, SHA-256, parser/schema version and audit outcome.

## 3. Supplementary reports — assessment

### 3.1 Participant-wise Open Interest — recommended supplementary input (high priority)

**Official filename pattern in the 2013 technical specification:** `fao_participant_oi_DDMMYYYY.csv`.

The specification lists these fields:
- Client Type
- Future Index Long / Future Index Short
- Future Stock Long / Future Stock Short
- Option Index Call Long / Option Index Put Long
- Option Index Call Short / Option Index Put Short
- Option Stock Call Long / Option Stock Put Long
- Option Stock Call Short / Option Stock Put Short
- Total Long Contracts / Total Short Contracts

**Potential value:** daily participant-category positioning context (e.g. FII, DII, Pro, Client categories if present in the current file) for index futures and index options.

**Critical limitation:** these are segment/category aggregates, not NIFTY-contract-specific positions. Do not attribute the aggregate values to NIFTY alone or infer the exact writer/buyer of a particular NIFTY strike. Long/short columns must be interpreted separately; total long/short sums combine different instruments and option directions.

**Decision:** add to the supplementary-candidate list. Promote to an ingested dataset only after obtaining and validating current-format sample files, confirming category labels, units, totals, report date and actual publication/availability behaviour.

### 3.2 Participant-wise Trading Volumes — recommended supplementary input (medium priority)

**Official filename pattern:** `fao_participant_vol_DDMMYYYY.csv). The 2013 specification lists the same participant and instrument-side breakdown as the OI report, with total long/short contracts.

**Potential value:** compare participant-category trading activity with end-of-day positioning. It may help identify broad participation shifts.

**Critical limitation:** volume measures activity, not closing positions or net option writing. It is not NIFTY-specific and should not be substituted for Bhavcopy contract-level traded volume.

**Decision:** optional supplementary candidate, lower priority than participant OI. Inspect current file and test whether it adds non-duplicative signal before inclusion.

### 3.3 F&O Daily Volatility — useful supplementary candidate (medium priority)

**Official filename pattern:** `FOVOLT_DDMMYYYY.csv`. The 2013 specification describes underlying and futures close prices, previous closes, log returns, previous/current daily volatility and annualised volatility. It describes an EWMA-style update and an applicable volatility as the maximum of underlying/futures daily volatility.

**Potential value:** an exchange-published futures/underlying volatility reference for regime context and cross-checking a separately computed volatility feature.

**Critical limitation:** the specification describes futures/underlying volatility, not NIFTY option implied volatility or a strike-wise volatility surface. Do not use it as option IV.

**Decision:** retain as an optional candidate for volatility-regime cross-checking. Do not make it mandatory because the core price series can support independently computed volatility; first compare current report values and methodology.

### 3.4 F&O Daily Settlement Prices — likely redundant for core analysis (low/medium priority)

**Official filename pattern:** `FOSett_prce_DDMMYYYY.csv`. The 2013 specification lists DATE, INSTRUMENT, UNDERLYING, EXPIRY DATE and MTM SETTLEMENT PRICE.

**Potential value:** independent settlement reference and reconciliation check.

**Critical limitation:** the Phase 1 UDiFF Bhavcopy already contains a settlement-price field (`SttlmPric`) at contract level. The older specification says this report is generated on the last day every two months, while the current NSE report catalogue displays dated daily entries; this discrepancy must be checked against actual current samples rather than assumed.

**Decision:** do not make mandatory. Consider as a cross-check only after current frequency, coverage and values are verified.

### 3.5 F&O FII Derivatives Statistics (XLS) — defer pending sample inspection

The current NSE All Reports catalogue lists this report, but the reviewed 2013 technical specification does not document its workbook schema. Its actual sheets, columns, units, categories and relationship to participant-wise OI were not inspected in this review.

**Decision:** do not ingest or rely on it yet. Obtain a permitted sample workbook and compare it with the FII row in participant-wise OI before deciding whether it adds distinct information.

### 3.6 Other reports

| Report | Initial treatment | Reason |
|---|---|---|
| F&O Market Activity Report (ZIP) | Defer | Inspect ZIP members and data dictionary; likely activity/turnover context, but avoid duplicate Bhavcopy measures until proven |
| F&O NCL Open Interest / Combined OI | Defer | Determine whether contract-level coverage, exchange scope and fields add anything beyond NSE Bhavcopy OI |
| Combined Delta Equivalent OI | Defer | Potentially useful normalized exposure context, but inspect calculation, coverage and schema before using |
| End-of-day SPAN | Exclude from initial signal inputs | Margin/risk parameter data, not direct evidence of directional seller positioning |
| Security ban / client position-limit / MWPL reports | Operational metadata only | Primarily stock-level position-limit/ban controls; not core NIFTY index-option pattern inputs |
| Top 10 Clearing Member Volumes | Defer | Clearing-member aggregate activity, not trader-side NIFTY positioning |
| Contract-wise ELM / haircut / exposure limits | Exclude from initial analytical inputs | Margin and collateral risk controls, not core historical price/OI evidence |

## 4. Important data-timing rule

The 2013 NSE technical specification marks participant-wise OI and volume files as **Next day** availability, while other report types have different schedules. That document is dated 2013 and the current NSE portal shows later report listings. Therefore:
- Keep `trade_date` / `report_date` separate from `retrieved_at` and any verified `published_at`.
- A missing report at the first retrieval attempt must be recorded as pending/unavailable, not as zero positions or zero volume.
- Do not add a user cutoff-time setting. The analysis uses the complete EOD report for the selected trading session, once the required source files are available.
- For reproducible historical analysis, record the exact report version, source and retrieval metadata used in the run.

## 5. Recommended first-version inventory

**Mandatory**
1. F&O UDiFF Bhavcopy Final.
2. F&O MII Contract File.
3. NIFTY 50 All Indices daily OHLC.

**Supplementary candidates to validate**
1. Participant-wise Open Interest — highest priority.
2. Participant-wise Trading Volumes.
3. F&O Daily Volatility.
4. F&O Daily Settlement Prices — reconciliation only unless proven otherwise.

**Deferred pending actual file/schema inspection**
1. FII Derivatives Statistics XLS.
2. Market Activity Report ZIP.
3. NCL OI / Combined OI / Combined Delta Equivalent OI.

No supplementary report is promoted to mandatory merely because it appears in the NSE catalogue. A sample must be obtained through a permitted method, schema-inspected, reconciled against the core dataset where applicable, and shown to add distinct analytical value.

## 6. Scope and compliance boundary

This note does not authorize automated NSE downloads. Phase 1 acquisition was a historical audit activity. Before implementing recurring or automated collection, review applicable NSE terms and confirm a permitted acquisition method. Preserve original files unchanged and do not add paid NSE Data & Analytics products as mandatory dependencies.

## 7. Sources

- NSE All Reports — Derivatives: https://www.nseindia.com/all-reports-derivatives
- NSE Data & Analytics, *Post Trade Data Technical Specification (Futures and Options Market)*, 03-Jan-2013: https://archives.nseindia.com/content/press/EOD_FAO.pdf
- Phase 1 closeout: `docs/development/phase-1-closeout.md` on `phase-1-data-audit`.
- Phase 1 row-level audit: `tools/audit_phase1_fo_reports.py` on `phase-1-data-audit`.

**Review conclusion:** retain the audited three-source core; prioritize participant-wise OI as a broad-market supplementary context dataset; keep participant volume and volatility optional; use settlement prices primarily for reconciliation; defer FII XLS and zipped/combined reports until their current contents are actually inspected.
