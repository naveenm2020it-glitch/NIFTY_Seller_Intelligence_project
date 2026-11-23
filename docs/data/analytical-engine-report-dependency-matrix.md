# Analytical Engine — EOD Report Dependency Research

**Status:** Research baseline for Phase 4 design; not an approved change to the three Phase 3 mandatory inputs  
**Research date:** 23 November 2026  
**Scope:** NIFTY 50 and NIFTY CE/PE only; historical EOD analysis  
**Repository baseline:** Phase 3 branch `phase-3-storage-data-processing`

## 1. Executive decision

Keep the three Phase 3 source reports as the mandatory EOD foundation:

1. NSE F&O UDiFF Common Bhavcopy Final (ZIP).
2. NSE F&O MII Contract File (GZ).
3. NSE Indices All Indices daily-close CSV.

The existing audited 22-session archive contains these three source types for each selected session. The Phase 3 contract already normalizes NIFTY 50 OHLC and selected-expiry NIFTY CE/PE OHLC, volume, open interest and underlying close, with MII contract identity and source provenance.

The official NSE All Reports — Derivatives catalogue also lists participant-wise OI, participant-wise trading volume, F&O Daily Volatility, Daily Settlement Prices, FII derivatives statistics, Market Activity, Combined Delta Equivalent OI and NCL Contract Delta. Their presence in the catalogue does **not** make them required inputs. Supplementary reports should be added only when a current sample is permitted, its schema and publication behaviour are checked, and it contributes information not already available from the core data.

**Important specification gap:** the repository architecture refers to “eight analytical engines” but does not name or define those engines. The uploaded Development Approach Review describes four feedback-learning components (Pattern Discovery, Pattern Knowledge Base, Feedback Intelligence and Pattern Optimization); those are not a specification of the eight analytical engines. Therefore, the functional mapping below is provisional and must not be represented as the approved eight-engine design.

## 2. Report-to-capability dependency matrix

The functional rows below translate capabilities explicitly present in the project material into data needs. They are not official engine names.

| Provisional analytical capability | Core fields / derived inputs | Supplementary report | Dependency decision |
|---|---|---|---|
| Underlying market regime and trend | NIFTY 50 daily OHLC; 1/5/22-session returns, ranges and realized-volatility features derived from historical closes | F&O Daily Volatility (FOVOLT) | Core is sufficient to calculate historical price features. FOVOLT is optional as an independent futures/underlying volatility reference, not an option-IV surface. |
| Price structure, levels and breakout/failure context | NIFTY 50 OHLC plus NIFTY option OHLC and contract metadata; levels must be calculated from historical observations | None identified as mandatory | Core only. Do not infer intraday sequence from daily OHLC. |
| Contract-level OI and seller/buyer pressure | NIFTY CE/PE contract OI, daily OI change across archived sessions, volume, strike, expiry and option type | Participant-wise OI | Core is mandatory and contract-specific. Participant OI is optional market-wide category context only; it cannot identify the writer/buyer of a particular NIFTY contract. |
| CE/PE premium behaviour and premium triggers | NIFTY CE/PE option OHLC, volume, OI, underlying close, strike and expiry; 1/5/22-session derived comparisons | Implied-volatility file only if a current permitted source/schema is verified | Core supports historical premium behaviour. The 2013 NSE technical specification mentions an `imp_volt` file, but this file was not found in the current public All Reports catalogue reviewed; do not depend on it. |
| Volatility and option-pricing context | NIFTY underlying and option EOD prices; time-to-expiry; any rate/volatility assumptions must be versioned and disclosed | FOVOLT optional; historical `imp_volt` candidate unverified | FOVOLT is futures/underlying volatility, not NIFTY option IV. An option-IV estimate calculated by the application would be model-derived and must be labelled as such, with its rate, dividend and pricing assumptions. |
| Participant positioning / participation context | Core NIFTY contract OI and volume; separately aggregated participant context | Participant-wise OI (priority candidate); Participant-wise Trading Volumes (lower-priority candidate) | Optional. These reports aggregate index/stock futures/options and participant categories; they are not NIFTY-strike-specific. Volume is activity, not closing position or proof of option writing. |
| Eight-scenario decision engine | Features from all validated core capabilities; scenario rules and thresholds are separately versioned | No supplementary report is proven mandatory | Core first. Scenarios must disclose unavailable inputs and avoid treating optional aggregate data as contract-level facts. |
| Pattern discovery, knowledge base, feedback and optimization | Historical features, scenario outputs, outcomes, user feedback, pattern/version metadata and validation results | No additional NSE report is inherently required | These are learning/data-lifecycle requirements, not extra market-report requirements. Outcome validation needs later historical observations, not a new same-day report. |

## 3. Supplementary report decisions

### 3.1 Participant-wise Open Interest — highest-priority optional candidate

- Current NSE All Reports catalogue lists the F&O Participant-wise Open Interest CSV.
- The NSE technical specification dated 03-Jan-2013 describes participant categories and separate index/stock futures and index/stock call/put long/short fields.
- It is useful for broad participant-category positioning context and cross-checking whether aggregate index-option positioning is changing.
- It is not NIFTY-contract-specific. Do not attribute its index-option aggregate to NIFTY alone, a strike, a selected expiry or a specific writer.
- **Decision:** inspect a current permitted sample, confirm present columns/units/category labels and report-date availability, then consider optional ingestion. Never make Phase 3 processing fail solely because this report is absent.

### 3.2 Participant-wise Trading Volumes — optional, lower priority

- Current NSE catalogue lists the F&O Participant-wise Trading Volumes CSV.
- The older specification describes participant-category volume splits for index/stock futures and index/stock calls/puts.
- It can provide activity context, but it is not a closing-position measure and does not prove net writing.
- **Decision:** defer until a current sample proves the fields and shows non-duplicative value beyond Bhavcopy volume.

### 3.3 F&O Daily Volatility (FOVOLT) — optional cross-check

- Current NSE catalogue lists F&O Daily Volatility.
- The 2013 specification describes underlying and futures closes, previous closes, log returns, daily volatility and annualised volatility.
- That description is not an option implied-volatility surface and is not strike-specific.
- **Decision:** optional reference/cross-check only. Compute the project's historical realized-volatility features from its own NIFTY price series and compare methodology before relying on FOVOLT.

### 3.4 F&O Daily Settlement Prices — reconciliation only

- Current NSE catalogue lists F&O Daily Settlement Prices.
- The Phase 3 UDiFF Bhavcopy already supplies the contract settlement field used by the audited core dataset.
- The 2013 specification describes a different historical schedule from the currently listed dated report entries; current frequency and coverage must be verified rather than inferred from the old document.
- **Decision:** not a mandatory source. Consider only for independent reconciliation after inspecting a current sample.

### 3.5 FII Derivatives Statistics — defer

- Listed in the current NSE catalogue, but the workbook sheets, current fields, units and overlap with participant-wise OI were not inspected.
- **Decision:** defer until a permitted sample workbook and data dictionary are reviewed. Do not duplicate participant OI without proving distinct coverage.

### 3.6 Market Activity Report — defer

- Listed as a ZIP in the current catalogue, but its current ZIP members and schema have not been inspected.
- **Decision:** defer. Do not ingest an opaque archive or duplicate Bhavcopy metrics without a field-level comparison.

### 3.7 Combined OI / NCL OI / Combined Delta Equivalent OI / NCL Contract Delta — research-only candidates

- The current catalogue lists Combined Delta Equivalent OI and NCL Contract Delta, and also exposes combined/NCL OI report categories.
- Their current definitions, exchange coverage, contract granularity, delta methodology and relation to NSE-only NIFTY contracts have not been verified from current samples.
- **Decision:** do not make mandatory. Review only if the project explicitly needs cross-exchange or delta-weighted exposure and the sample proves contract-level scope and reproducible methodology. Avoid double-counting NSE Bhavcopy OI.

### 3.8 Top 10 Clearing Member Volumes — defer

- The current catalogue lists this report; the 2013 specification describes aggregate index/stock futures/options volumes and turnover.
- Clearing-member aggregates are not equivalent to participant-side NIFTY option writing.
- **Decision:** defer unless a defined engine has a specific clearing-member concentration question.

### 3.9 Implied Volatility and Put/Call Ratio files in the old technical specification

The 03-Jan-2013 technical specification describes `imp_volt_ddmmyyyy.csv` with Contract Name, Strike Price, Option Type and IV, and `fo_ddmmyyyy.csv.gz` with product-level contracts, traded value and put/call ratio. These names were not visible in the current public NSE All Reports catalogue page reviewed on 23-Nov-2026. The document is old and cannot establish current availability, schema or access rights.

- **Decision:** treat both as unverified historical references, not current required sources.
- Calculate separate NIFTY-specific volume PCR and OI PCR from the NIFTY CE/PE Bhavcopy rows when the contract coverage supports it. Label the numerator/denominator and expiry/strike universe; do not substitute broad market PCR for NIFTY-specific PCR.
- Do not call FOVOLT option IV.

## 4. Data requirements that are not solved by another EOD report

1. **Intraday seller traps:** daily OHLC does not reveal the sequence of intraday price/OI changes, bid/ask pressure or the time a premium trigger occurred. The project is EOD-only; label these as historical EOD pattern candidates, not intraday-confirmed traps.
2. **Option Greeks / model IV:** these require explicit pricing assumptions and inputs beyond the core three files. Do not imply exchange-published IV unless a current source is verified.
3. **Participant attribution:** participant-wise aggregates cannot identify a particular NIFTY contract's seller.
4. **Outcome validation:** patterns need subsequent EOD observations to score what happened after the analysis date. Keep training/validation periods separate and avoid treating overlapping 22-session windows as independent samples.
5. **Report availability:** store trade/report date separately from retrieval and verified publication timestamps. Missing optional reports are unavailable/pending, never zero.

## 5. Recommended ingestion tiers

### Tier 1 — mandatory, already implemented in Phase 3
- F&O UDiFF Common Bhavcopy Final.
- F&O MII Contract File.
- NIFTY 50 All Indices daily-close CSV.

### Tier 2 — optional candidates for a later, separately tested ingestion change
1. Participant-wise OI.
2. F&O Daily Volatility.
3. Participant-wise Trading Volumes.
4. F&O Daily Settlement Prices (reconciliation only).

### Tier 3 — defer pending current sample/schema and distinct-value proof
- FII Derivatives Statistics.
- Market Activity Report.
- Combined/NCL OI and Combined Delta Equivalent OI.
- NCL Contract Delta.
- Top 10 Clearing Member Volumes.
- Legacy implied-volatility and PCR files described only in the 2013 specification.

No Tier 2 or Tier 3 report is approved for automated acquisition by this research. Review NSE terms and permitted acquisition methods before any recurring collection. No NSE download automation is authorized by this document.

## 6. Required follow-up before Phase 4 implementation

1. Obtain the approved functional specification that names all eight analytical engines, their inputs, outputs, formulas and acceptance criteria. Until then, do not assign invented engine names or claim the matrix is final.
2. For each supplementary candidate, inspect a permitted current sample and record exact filename, columns, data types, units, row grain, report date, publication/retrieval timing, missing-day behaviour and provenance.
3. Reconcile supplementary values to Bhavcopy or independently computed features where possible.
4. Demonstrate distinct analytical value using non-overlapping historical validation periods.
5. Approve any new report ingestion separately; keep Phase 3's three mandatory inputs stable unless evidence and project-owner approval justify a change.

## 7. Sources and evidence limits

- NSE India, All Reports — Derivatives: https://www.nse.in/all-reports-derivatives (current public catalogue reviewed 23-Nov-2026; establishes report listings, not detailed schemas).
- NSE Data & Analytics, *Post Trade Data Technical Specification (Futures and Options Market)*, 03-Jan-2013: https://archives.nseindia.com/content/press/EOD_FAO.pdf (legacy field/nomenclature reference only; publication schedule and schemas must not be assumed current).
- Repository `docs/development/phase-1-closeout.md`: audited 22-session archive and three-source evidence.
- Repository `docs/development/phase-3-data-contract.md`: actual Phase 3 normalized fields and source handling.
- Uploaded `Development Approach Review.txt`: four feedback-learning components and 1/5/22-session learning cautions.

**Conclusion:** the three Phase 3 reports remain sufficient as the mandatory EOD foundation for the currently documented scope. Participant OI is the first optional report worth validating. The other supplementary reports remain conditional or deferred. The exact eight-engine report mapping remains provisional until the missing eight-engine functional specification is added to the repository.
