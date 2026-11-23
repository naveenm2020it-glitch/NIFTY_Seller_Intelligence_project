# NSE F&O EOD Report Inventory — Review Note

**Review date:** 23 November 2026  
**Project:** NIFTY Seller Intelligence  
**Branch:** `phase-2-user-config-orchestration`  
**Purpose:** Identify official NSE EOD reports to retain as core inputs, supplementary context, or deferred candidates. This is a research note, not authorization for automated NSE collection.

## 1. Evidence reviewed

1. Phase 1 closeout and audit on `phase-1-data-audit`: the 22-session archive contains F&O UDiFF Bhavcopy, daily MII contract master and NIFTY 50 All Indices OHLC. The Phase 1 audit reconciled 43,966 NIFTY CE/PE Bhavcopy rows against contract-master snapshots, including the documented previous-session snapshot fallback.
2. NSE All Reports — Derivatives page: confirms that the F&O catalogue includes participant-wise OI, participant-wise trading volumes, FII derivatives statistics, daily volatility, daily settlement prices, market activity, NCL OI, combined OI, combined delta-equivalent OI, SPAN and other risk/operational files.
3. NSE Data & Analytics, *Post Trade Data Technical Specification (Futures and Options Market)*, dated 03-Jan-2013, especially pages 6 and 12–15. This is an older specification. Use it as a field/nomenclature reference only; do not assume publication timings or schemas remain unchanged without inspecting current samples.

## 2. Existing core inputs — mandatory

| Report | Status | Role |
|---|---|---|
| F&O UDiFF Common Bhavcopy Final (ZIP) | Phase 1 audited | Contract-level option/futures OHLC, settlement, volume, OI and underlying fields |
| F&O MII Contract File (GZ) | Phase 1 audited | Contract identity and metadata; expiry, strike and option type mapping |
| NSE Indices All Indices daily-close CSV | Phase 1 audited | NIFTY 50 daily OHLC and underlying cross-check |

These remain the first-version mandatory EOD source set. Preserve raw bytes, source URL, report/trading date, retrieval timestamp, byte size, SHA-256, parser/schema version and audit outcome.

## 3. Supplementary reports — assessment

### 3.1 Participant-wise Open Interest — high-priority supplementary candidate

**Filename pattern in the 2013 technical specification:** `fao_participant_oi_DDMMYYYY.csv`.

The specification lists:
- Client Type
- Future Index Long / Future Index Short
- Future Stock Long / Future Stock Short
- Option Index Call Long / Option Index Put Long
- Option Index Call Short / Option Index Put Short
- Option Stock Call Long / Option Stock Put Long
- Option Stock Call Short / Option Stock Put Short
- Total Long Contracts / Total Short Contracts

**Potential value:** participant-category positioning context for index futures and index options.

**Critical limitation:** these are segment/category aggregates, not NIFTY-contract-specific positions. Do not attribute aggregate values to NIFTY alone or infer the exact writer/buyer of a particular NIFTY strike. Interpret long/short columns separately; total long/short sums combine different instruments and option directions.

**Decision:** validate current-format sample files, category labels, units, totals, report date and actual publication/availability behaviour before ingestion.

### 3.2 Participant-wise Trading Volumes — medium-priority supplementary candidate

**Filename pattern:** `fao_participant_vol_DDMMYYYY.csv`. The 2013 specification lists the same participant and instrument-side breakdown as the OI report, with total long/short contracts.

**Potential value:** compare participant-category trading activity with end-of-day positioning to identify broad participation shifts.

**Critical limitation:** volume measures activity, not closing positions or net option writing. It is not NIFTY-specific and must not replace Bhavcopy contract-level traded volume.

**Decision:** optional candidate, lower priority than participant OI. Inspect the current file and test for non-duplicative signal before inclusion.

### 3.3 F&O Daily Volatility — medium-priority supplementary candidate

**Filename pattern:** `FOVOLT_DDMMYYYY.csv`. The 2013 specification describes underlying and futures close prices, previous closes, log returns, previous/current daily volatility and annualised volatility. It describes an EWMA-style update and an applicable volatility as the maximum of underlying/futures daily volatility.

**Potential value:** exchange-published futures/underlying volatility reference for regime context and cross-checking a separately computed volatility feature.

**Critical limitation:** the specification describes futures/underlying volatility, not NIFTY option implied volatility or a strike-wise volatility surface. Do not use it as option IV.

**Decision:** optional volatility-regime cross-check. Do not make it mandatory because the core price series supports independently computed volatility; compare current report values and methodology first.

### 3.4 F&O Daily Settlement Prices — reconciliation candidate

**Filename pattern:** `FOSett_prce_DDMMYYYY.csv`. The 2013 specification lists DATE, INSTRUMENT, UNDERLYING, EXPIRY DATE and MTM SETTLEMENT PRICE.

**Potential value:** independent settlement reference and reconciliation check.

**Critical limitation:** Phase 1 UDiFF Bhavcopy already contains contract-level settlement price (`SttlmPric`). The older specification says this report is generated on the last day every two months, while the current NSE report catalogue displays dated entries. Verify current frequency, coverage and values using an actual sample.

**Decision:** not mandatory; consider only as a cross-check after verification.

### 3.5 F&O FII Derivatives Statistics (XLS) — defer

The current NSE All Reports catalogue lists this report, but the reviewed 2013 technical specification does not document its workbook schema. Actual sheets, columns, units, categories and relationship to participant-wise OI were not inspected.

**Decision:** do not ingest or rely on it yet. Obtain a permitted sample workbook and compare it with the FII row in participant-wise OI before deciding whether it adds distinct information.

### 3.6 Other reports

| Report | Initial treatment | Reason |
|---|---|---|
| F&O Market Activity Report (ZIP) | Defer | Inspect ZIP members and data dictionary; avoid duplicate Bhavcopy measures until proven |
| F&O NCL Open Interest / Combined OI | Defer | Determine whether contract-level coverage, exchange scope and fields add anything beyond NSE Bhavcopy OI |
| Combined Delta Equivalent OI | Defer | Potentially useful normalized exposure context; inspect calculation, coverage and schema first |
| End-of-day SPAN | Exclude from initial signal inputs | Margin/risk parameter data, not direct evidence of directional seller positioning |
| Security ban / client position-limit / MWPL reports | Operational metadata only | Primarily stock-level position-limit/ban controls; not core NIFTY index-option pattern inputs |
| Top 10 Clearing Member Volumes | Defer | Clearing-member aggregate activity, not trader-side NIFTY positioning |
| Contract-wise ELM / haircut / exposure limits | Exclude from initial analytical inputs | Margin and collateral risk controls, not core historical price/OI evidence |

## 4. Important data-timing rule

The 2013 NSE technical specification marks participant-wise OI and volume files as **Next day** availability, while other report types have different schedules. The document is dated 2013 and the current NSE portal shows later report listings. Therefore:
- Keep `trade_date` / `report_date` separate from `retrieved_at` and any verified `published_at`.
- A missing report at first retrieval must be recorded as pending/unavailable, not as zero positions or zero volume.
- Do not add a user cutoff-time setting. Analysis uses the complete EOD report for the selected trading session, once required source files are available.
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

No supplementary report becomes mandatory merely because it appears in the NSE catalogue. Obtain a sample through a permitted method, inspect its schema, reconcile it against core data where applicable, and demonstrate distinct analytical value first.

## 6. Scope and compliance boundary

This note does not authorize automated NSE downloads. Phase 1 acquisition was a historical audit activity. Before implementing recurring or automated collection, review applicable NSE terms and confirm a permitted acquisition method. Preserve original files unchanged and do not add paid NSE Data & Analytics products as mandatory dependencies.

## 7. Sources

- NSE All Reports — Derivatives: https://www.nseindia.com/all-reports-derivatives
- NSE Data & Analytics, *Post Trade Data Technical Specification (Futures and Options Market)*, 03-Jan-2013: https://archives.nseindia.com/content/press/EOD_FAO.pdf
- Phase 1 closeout: `docs/development/phase-1-closeout.md` on `phase-1-data-audit`.
- Phase 1 row-level audit: `tools/audit_phase1_fo_reports.py` on `phase-1-data-audit`.

**Review conclusion:** retain the audited three-source core; prioritize participant-wise OI as broad-market supplementary context; keep participant volume and volatility optional; use settlement prices primarily for reconciliation; defer FII XLS and zipped/combined reports until current contents are inspected.


## 8. Analytical-engine dependency research

The report-to-capability mapping and ingestion tiers are documented separately in [Analytical Engine — EOD Report Dependency Research](analytical-engine-report-dependency-matrix.md).

Key findings:
- Keep the three audited Phase 3 core reports mandatory.
- Participant-wise OI is the highest-priority optional report, but it is aggregate index/stock participant context and cannot identify a NIFTY strike's writer.
- Participant volume, FOVOLT and settlement prices remain optional candidates, not mandatory dependencies.
- The 03-Jan-2013 technical specification also mentions legacy implied-volatility and traded-volume PCR files. They were not visible in the current public NSE All Reports catalogue reviewed on 23-Nov-2026; treat them as unverified, not current dependencies.
- The architecture refers to eight analytical engines but does not define their names or contracts. Exact engine-by-engine mapping remains provisional until the approved functional specification is added.
- No supplementary report is approved for automated acquisition by this research. Current samples, schema, availability, distinct value and permitted acquisition method must be checked first.
