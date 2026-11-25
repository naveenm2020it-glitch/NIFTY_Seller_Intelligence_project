# Phase 4 — Feature Engineering Specification (Review Draft)

**Status:** Review draft; session-window convention and the NIFTY spot formula decisions listed in Section 10 have been owner-approved; remaining definitions and implementation decisions remain open  
**Scope:** NIFTY 50 and selected-expiry NIFTY CE/PE historical EOD data  
**Depends on:** Phase 0–3 foundation and `docs/development/phase-3-data-contract.md`  
**User inputs:** Analysis Date and selected Expiry only

> This phase defines reproducible descriptive features from the validated Phase 3 data. It does not define seller-identification formulas, S1/S2/R1/R2 levels, option rankings, premium triggers, scenario decisions or ML models. Those belong to later phases and require separate approval.

## 1. Phase objective

Convert the persisted Phase 3 EOD records into deterministic, versioned feature sets that later analytical engines can consume.

Feature Engineering must:
- Preserve observed source values separately from derived features.
- Produce 1-, 5- and 22-session context where sufficient historical observations exist.
- Apply relevant windows to NIFTY spot, CE/PE premium, OI and volume history.
- Keep each selected-expiry contract's history distinct.
- Record exact dates, observation counts, missingness and source provenance.
- Be reproducible for the same Analysis Run, source hashes and feature-definition version.

Feature Engineering is a descriptive data-preparation layer. It must not issue BUY CE, BUY PE or WAIT.

## 2. Inputs and hard boundaries

### 2.1 Phase 3 inputs

Read only the validated Phase 3 records:
- NIFTY 50 EOD OHLC by trading date.
- NIFTY CE/PE EOD OHLC, volume and open interest.
- Contract identity: instrument ID, selected expiry, strike and option type.
- Underlying close, source filename/hash, contract-source metadata and ingestion-batch provenance.

### 2.2 Boundaries

- Historical EOD only; no live or intraday feed.
- No NSE scraping, automated report acquisition or new report ingestion.
- No broker connection, order execution, alerts, paper tracking or trading backtesting.
- No cutoff-time input; Analysis Date and Expiry remain the only user inputs.
- Do not modify Phase 3 raw/normalized records.
- Do not substitute another expiry or silently fill missing observations.
- Zero-volume rows remain valid observations and must not be dropped.
- Missing OI, volume, premium or prior-session observations are not zero.
- Do not claim that OI proves a seller, buyer, fresh writing or liquidation.
- Do not calculate support/resistance as strike plus/minus option premium.
- Do not add indicators, scoring weights, arbitrary thresholds or ML labels without separate approval.

## 3. Session-window contract — important

**Approved convention:** For N = 1, 5 or 22, the window contains exactly up to N available trading-date EOD records, including the selected Analysis Date. It is not defined as N complete close-to-close intervals.

- 1 session = Analysis Date only.
- 5 sessions = Analysis Date plus the previous 4 available trading sessions.
- 22 sessions = Analysis Date plus the previous 21 available trading sessions.
- The window ends on the selected Analysis Date and uses validated trading-date records, not calendar-day subtraction.
- Every output reports the actual first/last dates, expected window size and actual observation count.
- If fewer than N records exist, mark the feature partial or unavailable according to its definition; never fabricate history.

**Observation count is not the same as return-interval count.** N EOD records contain N-1 close-to-close intervals between the first and last records. A close-to-close return for the earliest record in a window may require one additional prior closing record. That extra record is a calculation dependency only; it is not counted as part of the N-record window. If it is absent, the relevant return is unavailable.

The 1/5/22 windows are analysis contexts, not independent validation samples. Overlapping windows must never be counted as independent observations for confidence or model validation.

## 4. Proposed feature groups

The following are proposed descriptive features. Their definitions and output schema require project-owner review before implementation. No decision thresholds are implied.

### 4.1 NIFTY 50 spot features

For each available EOD bar:
- Open, high, low and close (retain source values).
- Absolute close-to-close point change and percentage return, when a valid prior close exists.
- Intraday range in points (high minus low).
- Intraday range as a percentage of the prior close, when the prior close is valid and non-zero.
- Candle body in points (close minus open).
- Opening gap in points and percentage relative to the prior close.
- Close location within the day's high-low range, only when high is greater than low.

For each 1/5/22 observation window, where sufficient data exists:
- First/last observation dates and count.
- First and last close.
- Cumulative close change in points and percentage from the first observation to the last.
- Highest high and lowest low in the window.
- Window range in points and percentage, with the denominator explicitly recorded.
- Mean daily range and the underlying observation count.

Realized-volatility estimators may be added only after the estimator, return convention, annualization and minimum-observation rules are approved. FOVOLT is not part of the core Phase 4 input contract and must not be treated as NIFTY option IV.

### 4.2 CE/PE contract features

For each exact selected-expiry contract (NIFTY, expiry, strike and option type), retain the original EOD observations and derive, where valid:
- Close premium and OHLC range.
- Close-to-close premium change in rupees and percentage.
- Daily volume and open interest.
- Absolute OI change versus the immediately preceding valid observation for the same contract.
- OI percentage change only when the preceding OI is greater than zero.
- Volume/OI ratio only when the denominator is valid and greater than zero.
- Contract observation count and continuity/missing-session flags.

For each 1/5/22 window:
- First/last dates and observation count for the exact contract.
- First/last EOD close premium and cumulative premium change.
- Highest/lowest observed premium and premium range.
- Sum of traded volume, with zero-volume days retained.
- First/last OI and net OI change when both endpoints are available.
- Number of valid premium, volume and OI observations, separately.

Do not calculate a multi-session premium return across different strikes, option types or expiries. If a contract is absent on one or more dates, report the gap; do not forward-fill, interpolate or replace it with a nearby strike.

### 4.3 Contract and underlying context

Candidate contextual fields:
- Selected expiry, strike, option type and instrument ID for each source observation.
- Analysis-date NIFTY spot close.
- Spot-to-strike distance as a numeric value, with its exact formula and units recorded.
- Calendar days to expiry, calculated from the Analysis Date and selected expiry.

The ITM/ATM/OTM classification boundaries remain unapproved. Store the numeric spot/strike relationship first; do not invent an ATM band or silently assign a moneyness class.

### 4.4 Cross-engine 1/5/22 coverage

Feature outputs should support later engines as follows. This table describes data availability, not final engine calculations.

| Later engine | 1-session context | 5-session context | 22-session context |
|---|---|---|---|
| 1. Market Regime and Trend | Latest NIFTY EOD state | Short-term spot movement/range | Broader spot movement/range |
| 2. Price Structure and Key Levels | Current spot OHLC and option evidence | Recent spot/contract observations | Broader historical spot/contract observations |
| 3. Contract OI and Positioning | Latest OI, volume and premium | Recent OI/volume/premium changes | Broader OI/volume/premium changes |
| 4. CE/PE Premium Behaviour and Ranking | Latest contract premium | Same-contract premium behaviour | Same-contract premium behaviour, subject to continuity |
| 5. Volatility and Pricing Context | Latest available price context | Short-window volatility inputs if approved | Longer-window volatility inputs if approved |
| 6. Participant Positioning Context | Only if a permitted validated report exists | Only if comparable dated reports exist | Only if comparable dated reports exist |
| 7. Seller Pressure and Setup Detection | Latest upstream feature snapshot | Recent context from Engines 1–6 | Broader context from Engines 1–6 |
| 8. Eight-Scenario Decision and Report | Current EOD evidence | Short-term context | Broader context |

The 22-session context must not be restricted to spot S/R. Where history exists, it must also be available for CE and PE premium behaviour, OI changes, volume, seller-positioning evidence and the later engines' spot/premium pressure analysis. The actual S/R, seller-pressure and trigger formulas remain outside this phase.

Participant reports are optional and are not included in the Phase 3 core data contract. Their absence must remain unavailable/pending, never zero. This phase does not authorize their acquisition or ingestion.

## 5. Data continuity, missingness and quality

- Use the selected Analysis Date and Expiry from the existing Analysis Run.
- Select prior sessions from the validated trading-date records, not calendar-day subtraction.
- Keep a feature's source observation count separate from its expected window size.
- A missing contract/date is missing, not a zero premium, zero OI or zero volume.
- A reported zero-volume contract row remains present and distinguishable from a missing row.
- Percentage changes with a zero or missing denominator are unavailable, not infinity and not zero.
- Do not mix expiries.
- Do not bridge a missing contract observation with a different strike.
- If source values fail Phase 3 validation, Phase 4 must not repair or overwrite them; processing should surface the upstream failure.
- Preserve source trade date, instrument identity, source hash and ingestion batch reference for every feature lineage.

## 6. Feature output and versioning requirements

Each feature result should be traceable to:
- Analysis Run ID.
- Analysis Date and selected Expiry.
- Feature name and feature-definition version.
- Source trade-date range and actual observation count.
- Source row/contract identity and source provenance.
- Calculation status: available, partial, unavailable or invalid.
- Missingness/quality reason where not fully available.
- Calculation parameters required to reproduce the value.

A proposed feature-set summary should record the feature-definition version, input source hashes, number of index observations, number of option-contract observations, window coverage and validation summary.

The final persistence format and any database migration are not approved by this document. Prefer to finalize the feature schema and idempotency key before creating new tables or changing the API contract.

## 7. Acceptance criteria for Phase 4

Phase 4 implementation is complete only when all of the following are demonstrated:

1. Identical Analysis Run inputs and source hashes produce identical feature outputs.
2. 1/5/22 windows use validated trading sessions and report exact dates and counts.
3. Insufficient history is explicitly partial/unavailable; no synthetic rows are created.
4. Index features use NIFTY 50 EOD bars only.
5. Option features preserve exact selected expiry, strike and CE/PE identity.
6. Premium history is not joined across different contracts.
7. OI and volume changes use valid prior observations and explicit denominator rules.
8. Zero-volume observations remain present.
9. Missing values are not silently replaced with zero or forward-filled.
10. All feature outputs carry Analysis Run and source provenance.
11. Tests cover first available date, missing prior session, missing contract session, zero volume, zero OI denominator, expiry mismatch, duplicate input and insufficient 22-session history.
12. No S/R levels, ranking, premium triggers, scenario decisions, ML models or live functionality are introduced in Phase 4.
13. Backend tests and frontend build (if UI changes are introduced) pass.
14. Documentation records the exact feature-definition version and known limitations.

## 8. Dependencies and implementation order

1. Confirm the approved session-window semantics and approve the proposed feature catalog.
2. Confirm the exact Phase 3 repository paths, data-access functions and Analysis Run lifecycle to reuse.
3. Implement pure, deterministic feature calculations without mutating Phase 3 data.
4. Add unit tests for calculations, continuity, missingness and window boundaries.
5. Add service/API integration and persistence only after the feature output schema and idempotency rules are approved.
6. Add a small read-only feature preview only if required; do not build the full dashboard in this phase.
7. Validate outputs against hand-calculated fixtures and the preserved historical archive where access is available.
8. Close Phase 4 with test evidence and a versioned feature contract.

## 9. Decisions still requiring project-owner approval

1. **Approved:** Each N-session window means N EOD observations including the Analysis Date, not N complete close-to-close intervals.
2. Approve the proposed spot feature list and percentage denominators.
3. Approve the proposed option feature list and the exact contract continuity key.
4. Approve the spot/strike distance convention and whether/when ITM/ATM/OTM labels are needed.
5. Approve any realized-volatility estimator and annualization method.
6. Approve feature output schema, storage format and idempotency key.
7. Confirm whether Phase 4 needs an API/UI preview or only a backend feature artifact.
8. Confirm permitted source/data-use scope before any supplementary report is added.

Until these decisions are approved, this document is a design draft only. No code, schema, migration, data, report acquisition, deployment or production configuration is changed by this specification.


## 10. Owner-reviewed NIFTY spot formula decisions

The following NIFTY spot features were approved during the project-owner review on 2026-11-25. These approvals authorize their inclusion in the Phase 4 feature catalogue; they do not authorize prediction, signal generation, scoring or trading decisions.

| Feature | Definition | Review status |
|---|---|---|
| Close-to-close point change | Current close minus immediately preceding available validated trading-session close | Approved |
| Simple close-to-close return | (Current close / previous close - 1) × 100 | Approved |
| Log close-to-close return | ln(Current close / previous close), stored as a decimal log return; multiply by 100 only when a percentage-form display is required | Approved — representation refined |
| Intraday range | High - Low | Approved |
| Intraday range percentage | (High - Low) / previous close × 100 | Approved |
| Candle body points | Close - Open | Approved |
| Candle body percentage | (Close - Open) / Open × 100 | Approved |
| Candle body ratio | (Close - Open) / (High - Low) | Approved |
| Opening gap points | Open - previous close | Approved |
| Opening gap percentage | (Open - previous close) / previous close × 100 | Approved |
| Daily Close Location Value (CLV) | ((Close - Low) - (High - Close)) / (High - Low) | Approved |
| Williams %R (5) | -100 × (highest high over 5 sessions - current close) / (highest high - lowest low over 5 sessions) | Approved |
| Williams %R (22) | Same definition over 22 sessions | Approved |

### 10.1 Window application and calculation safeguards

- Approved daily features are calculated for the available EOD observations represented by the 1-, 5- and 22-session contexts, subject to each feature's required prior observation and denominator.
- The N-session context remains N available validated EOD observations including the Analysis Date. It is not N return intervals.
- Close-to-close change, simple return, log return and opening gap require the immediately preceding available validated trading-session close. If it is missing, the affected result is unavailable. A required prior close outside the N-session window is a dependency only and is not counted in that window.
- Simple return and percentage features are unavailable when their denominator is missing or zero. Store log return as the decimal value ln(Current close / previous close); convert to percentage form by multiplying by 100 only at the presentation boundary. Log return is unavailable unless both closes are valid and positive.
- Candle body ratio and CLV are unavailable when High equals Low. Do not replace unavailable results with zero.
- Calculate Williams %R separately for each observation using only that observation and its preceding available validated trading-session records within the specified 5- or 22-session lookback. Never use later observations from the Analysis Date window to calculate an earlier row. Williams %R is unavailable until the required lookback is available or when its highest high equals its lowest low. Do not invent thresholds or overbought/oversold labels.
- Retain full calculation precision internally. Store log returns as decimal values; percentage display is a presentation conversion (× 100), not a separate underlying calculation. Output rounding and display precision remain an output-schema decision.
- Calculate rolling indicators such as Williams %R independently at each historical observation using only data available up to that observation, preventing look-ahead leakage.
- Keep original OHLC values unchanged and retain provenance for every derived value.

### 10.2 Yang–Zhang volatility decision

The owner selected Yang–Zhang as the preferred advanced volatility estimator in addition to the approved basic range features. The design is approved only as a candidate for 5- and 22-session contexts; it is unavailable for a 1-session context. It is **not ready for implementation** until the exact estimator convention, minimum valid observations, annualization convention, missing-session treatment and output precision are separately approved. No Yang–Zhang value may be emitted before those rules are finalized.

### 10.3 Decisions still open within the feature catalogue

The following remain open and must not be treated as approved merely because the spot formulas above were approved:
- The full CE/PE contract feature catalogue and exact continuity key.
- Spot-to-strike distance formula and units, and any ITM/ATM/OTM classification.
- Window-summary denominator and aggregation conventions where not explicitly defined above.
- Yang–Zhang estimator parameters and validity rules.
- Feature output schema, persistence format and idempotency key.
- Backend-only output versus a read-only preview/API.

### 10.5 Owner-approved CE/PE premium movement features

The project owner approved the following two descriptive premium movement features for the Phase 4 catalogue:

| Feature | Definition | Review status |
|---|---|---|
| Absolute premium change (₹) | Current EOD closing premium minus the immediately preceding validated trading-session EOD closing premium for the exact same contract | Approved |
| Simple premium return (%) | (Current EOD closing premium / immediately preceding validated trading-session EOD closing premium - 1) × 100 | Approved |

#### Calculation and continuity safeguards

- Calculate both features independently for each exact contract identity: NIFTY underlying, selected expiry, strike, option type and instrument ID.
- Use the immediately preceding validated trading-session observation for that same contract. If that adjacent session's contract observation is missing, mark the movement unavailable; do not bridge the gap or substitute another strike, expiry, option type or instrument.
- Absolute premium change remains calculable when the previous premium is zero, provided both current and previous premium observations are valid.
- Simple premium return is unavailable when the previous premium is missing or zero. Do not replace an unavailable return with zero.
- A current premium of zero is a valid observed value and must be preserved.
- Retain source premium observations unchanged and preserve trade-date, contract identity and source provenance.
- These features describe premium movement only. They do not independently establish seller identity, fresh writing, unwinding, seller dominance or a trading signal.
- Log premium return, symmetric percentage change and spot-normalized premium change are not approved Phase 4 features. They remain outside the approved catalogue unless separately reviewed.

### 10.4 Separate 17 + 4 + 1 rolling forecast-validation concept

The owner approved the following high-level historical workflow concept:

- Sessions 1–17: establish the initial cumulative historical baseline.
- Sessions 18–21: perform four sequential one-session-ahead forecast checks. For each target session, use only EOD information available before that target, then compare the forecast with that session's actual EOD outcome after the forecast is recorded.
- Session 22: produce the final one-session-ahead assessment using only Sessions 1–21. Session 22 actual EOD data must not be used as an input to its own forecast; it may be used only for later evaluation after the forecast is fixed.

This is a later-phase forecast-validation protocol, not a Phase 4 feature window or feature calculation. Phase 4 must not generate forecasts, scenarios, BUY CE/BUY PE/WAIT decisions, trading signals, trade simulations or P&L backtests. The 17 + 4 + 1 concept is recorded separately in `docs/development/17-4-1-walk-forward-validation-proposal.md` and must be implemented only in the appropriate later phase after its evaluation methodology is approved.

Four sequential validation targets are useful for checking workflow correctness but are not enough to establish statistically reliable predictive accuracy. Any accuracy claim requires a substantially larger chronological evaluation sample, explicit target definitions and leakage-safe validation.
