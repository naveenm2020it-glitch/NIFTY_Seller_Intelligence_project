# Phase 4 — Feature Engineering Specification (Review Draft)

**Status:** Design decisions reviewed and owner-approved as recorded in Sections 3 and 10; physical database schema, migrations, exact API contract and implementation remain pending  
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

The following are descriptive feature groups. Formula and design approvals are recorded in Section 10; any item not explicitly approved remains pending. No decision thresholds are implied.

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

Yang–Zhang realized volatility is approved for NIFTY 50 spot OHLC in the 5- and 22-session contexts under Section 10.2. It is a historical spot-volatility feature, not option implied volatility. FOVOLT is not part of the core Phase 4 input contract and must not be treated as NIFTY option IV.

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
- Spot-to-strike distance in points and percentage, using the Analysis Date NIFTY spot close and each selected-expiry strike, under the formulas in Section 10.11.
- ITM/ATM/OTM classification using the standard call/put moneyness rules and nearest-listed-strike ATM convention in Section 10.11.
- Calendar days to expiry, calculated from the Analysis Date and selected expiry.

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

The logical feature-record contract and deterministic idempotency identity are approved in Section 10.11. The physical persistence design, database tables, migrations and exact read-only API request/response contract remain implementation-level decisions and must be reviewed before any schema or API change.

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
5. Implement the approved logical feature-record contract and idempotency rules; finalize and review physical persistence and API contracts before database or API changes.
6. Add a small read-only feature preview only if required; do not build the full dashboard in this phase.
7. Validate outputs against hand-calculated fixtures and the preserved historical archive where access is available.
8. Close Phase 4 with test evidence and a versioned feature contract.

## 9. Decision status and remaining implementation reviews

The following design decisions have been owner-approved and are detailed in Section 10:
1. N-session windows contain N validated EOD observations including the Analysis Date.
2. The reviewed NIFTY spot and CE/PE feature formulas and their continuity/denominator safeguards.
3. Yang–Zhang volatility for NIFTY 50 spot OHLC only, using the approved 5/22-session conventions.
4. CE/PE True Range and SMA-based ATR (5/22), including exact-contract continuity rules.
5. Spearman OI–premium correlation only when all 22 paired observations are valid in the 22-session context.
6. Feature-specific display precision, with full precision retained internally.
7. Spot-to-strike distance in points and percentage, plus standard ITM/ATM/OTM classification.
8. The logical structured feature-record contract and versioned deterministic upsert identity.
9. Backend feature calculation with a read-only API; no full dashboard/UI in Phase 4.
10. Missing contract observations invalidate only affected contract features/windows, not the entire Analysis Run.

The following implementation/source-governance items remain open and are not authorized by these design decisions:
- Physical database persistence design, table definitions and migrations.
- Exact read-only API endpoints, payload schemas, permissions and integration details.
- Permitted source/data-use scope before any supplementary report or data source is introduced. Phase 4 remains restricted to validated Phase 3 records unless separately approved.

Until implementation-level reviews are completed, this document remains a design specification. It does not authorize application-code changes, database schema changes, migrations, data mutation, report acquisition, deployment or production-configuration changes.


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

### 10.2 Owner-approved Yang–Zhang volatility feature

The project owner approved the Yang–Zhang volatility estimator for **NIFTY 50 spot OHLC only**, in the 5- and 22-session contexts. It is not calculated for the 1-session context and is not an option-premium volatility feature. The output is an annualized, backward-looking realized-volatility estimate; it is not implied volatility, a directional forecast, a seller signal or a trading signal.

#### Approved estimator and parameters

For a window containing \(n\) validated EOD observations, where \(n=5\) or \(n=22\), use the following Yang–Zhang estimator:

- \(O_i,H_i,L_i,C_i\) are the NIFTY 50 spot open, high, low and close for observation \(i\).
- \(C_{i-1}\) is the immediately preceding validated trading-session close. For the first observation in the selected window, this close is a calculation dependency outside the window and is not counted among its \(n\) observations.
- Use natural logarithms:
  - Opening-gap return: \(o_i=\ln(O_i/C_{i-1})\)
  - Close-to-open return: \(c_i=\ln(C_i/O_i)\)
  - Rogers–Satchell term: \(RS_i=\ln(H_i/C_i)\ln(H_i/O_i)+\ln(L_i/C_i)\ln(L_i/O_i)\)
- Calculate the sample variances of the opening-gap and close-to-open returns using divisor \(n-1\):
  - \(V_o=\operatorname{SampleVar}(o_1,\ldots,o_n)\)
  - \(V_c=\operatorname{SampleVar}(c_1,\ldots,c_n)\)
- Calculate the mean Rogers–Satchell term using divisor \(n\):
  - \(V_{RS}=\frac{1}{n}\sum_{i=1}^{n}RS_i\)
- Use \(\alpha=1.34\) and calculate the estimator weight separately for each window size:
  - \(k=\frac{0.34}{1.34+\frac{n+1}{n-1}}\)
- Combine the components:
  - \(V_{YZ}=V_o+kV_c+(1-k)V_{RS}\)
- Use 252 trading sessions per year as the project's annualization convention:
  - Annualized Yang–Zhang volatility (%) \(=\sqrt{252\times V_{YZ}}\times100\)

The value 252 is the approved project annualization convention; it is not an intrinsic constant of the Yang–Zhang estimator. Retain full calculation precision internally and present the annualized result as a percentage per annum. Display rounding remains governed by the feature output/presentation specification.

#### Window completeness and input validation

- Calculate the estimator only for complete 5- or 22-observation windows, including the Analysis Date, under the Phase 4 session-window contract. Do not calculate a partial-window Yang–Zhang result.
- All \(n\) OHLC observations and the immediately preceding validated session close required for the first opening-gap return must be present and valid. If any required observation or dependency is missing, the entire window's Yang–Zhang result is unavailable; do not bridge a gap, reduce the sample, forward-fill or interpolate.
- All required OHLC prices and the preceding close must be positive. Each bar must satisfy \(H_i\geq\max(O_i,C_i)\) and \(L_i\leq\min(O_i,C_i)\). Invalid source data must not be repaired in Phase 4; surface the invalidity and preserve the Phase 3 validation boundary.
- Use \(n=5\) for the 5-session estimator and \(n=22\) for the 22-session estimator when calculating \(k\). Do not substitute the number of return intervals or a different sample count.
- The prior close before the first window observation is a calculation dependency only. It does not increase the window observation count.
- If the required window or dependency is incomplete or invalid, report the feature as unavailable with its missingness/quality reason. Do not replace the result with zero or publish a partial estimate.
- Preserve the estimator components, window size, calculated \(k\), annualization factor, observation dates, prior-close dependency, input validity and calculation status so the result can be reproduced from the validated source data.
- Do not calculate Yang–Zhang volatility for CE/PE option premiums under this approval. Any option-premium volatility estimator requires a separate review and approval.

#### Interpretation limits

Yang–Zhang is a historical spot-volatility estimator that incorporates overnight opening gaps and intraday OHLC information. It measures realized historical variability, not market direction or future movement. It does not identify buyers or sellers, establish fresh writing or unwinding, demonstrate seller dominance, or independently create a setup, ranking or trading signal.

### 10.3 Remaining implementation-level decisions

The feature formulas and logical design decisions approved in Section 10 are not pending. The following implementation details remain open and require review before implementation:
- Physical database persistence design, table/column definitions, indexes and migrations.
- Exact read-only API routes, request/response schemas, permissions and integration details.
- Any supplementary source/data-use scope beyond validated Phase 3 records; no supplementary report acquisition or ingestion is authorized by this specification.

### 10.6 Owner-approved CE/PE premium range and candle features

The project owner approved the following six descriptive features for the Phase 4 CE/PE contract feature catalogue:

| Feature | Definition | Review status |
|---|---|---|
| Intraday premium range | High premium - Low premium | Approved |
| Premium range percentage | (High premium - Low premium) / immediately preceding validated trading-session closing premium × 100 | Approved |
| Premium candle body points | Closing premium - Opening premium | Approved |
| Premium candle body percentage | (Closing premium - Opening premium) / Opening premium × 100 | Approved |
| Premium candle body ratio | (Closing premium - Opening premium) / (High premium - Low premium) | Approved |
| Premium Close Location Value (CLV) | ((Closing premium - Low premium) - (High premium - Closing premium)) / (High premium - Low premium) | Approved |

#### Calculation and continuity safeguards

- Calculate each feature separately for the exact contract identity: NIFTY underlying, selected expiry, strike, option type and instrument ID.
- Preserve original source OHLC values unchanged.
- Premium range percentage requires a valid, non-zero immediately preceding validated trading-session closing premium for the same contract. If unavailable, the result is unavailable; do not bridge missing contract sessions.
- Premium candle body percentage is unavailable when opening premium is missing or zero.
- Premium candle body ratio and CLV are unavailable when High equals Low.
- Do not replace unavailable results with zero. Preserve valid observed zero premiums.
- These features describe the contract's EOD premium candle; they do not independently establish seller identity, fresh writing, unwinding, seller dominance or a trading signal.

#### Owner-approved True Range

The project owner approved True Range (TR) as a daily descriptive CE/PE premium-range feature:

`TR_t = max(H_t - L_t, |H_t - P_{t-1}|, |L_t - P_{t-1}|)`

Here, `H_t` and `L_t` are the current exact contract's EOD high and low premiums, and `P_(t-1)` is the immediately preceding validated trading-session closing premium for that same exact contract.

- Calculate TR independently for each exact contract identity: NIFTY underlying, selected expiry, strike, option type and instrument ID.
- The immediately preceding validated trading-session close is required. If that contract observation is missing, TR is `UNAVAILABLE`; do not bridge the gap or substitute another contract.
- Preserve valid observed zero premiums. Missing values are not zero.
- Use the validated Phase 3 OHLC values without modifying the source observations.
- TR is expressed in premium points (₹) and is descriptive only; it does not identify sellers, prove writing/unwinding or create a trading signal.

#### Owner-approved Average True Range (ATR) — SMA (5/22)

The project owner selected the Simple Moving Average (SMA) convention for CE/PE ATR in the 5- and 22-session contexts:

`ATR_N = (TR_1 + TR_2 + ... + TR_N) / N`, where `N` is 5 or 22.

- Calculate ATR separately for each exact contract identity and each window; never combine strikes, option types or expiries.
- The window contains exactly N validated EOD observations including the Analysis Date, consistent with Section 3. The first TR in the window may require the immediately preceding validated session close outside the window; that close is a calculation dependency and is not counted in N.
- ATR is available only when all N required TR values are valid. If any required TR is unavailable because of a missing contract observation or missing prior close, the ATR is `UNAVAILABLE`; do not calculate from a reduced subset or label a partial average as a complete ATR.
- Preserve the expected and actual TR observation counts, first/last dates, contract identity, source provenance and unavailable reason.
- Retain full calculation precision internally. Display precision follows the feature-specific presentation rule in Section 10.11.
- ATR is a historical premium-range summary, not a directional forecast, seller-identification method or trading signal.

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

### 10.7 Owner-approved CE/PE open-interest movement features

The project owner approved the following two descriptive open-interest (OI) movement features for the Phase 4 CE/PE contract feature catalogue:

| Feature | Definition | Review status |
|---|---|---|
| Absolute OI change | Current EOD OI minus the immediately preceding validated trading-session EOD OI for the exact same contract | Approved |
| Percentage OI change (%) | (Current EOD OI / immediately preceding validated trading-session EOD OI - 1) × 100 | Approved |

#### 1/5/22-session context and window summaries

- **1-session context:** Report the Analysis Date's absolute OI change and percentage OI change against the immediately preceding validated trading-session observation for the exact same contract. That prior observation is a calculation dependency outside the 1-session window; it is not counted as a window observation.
- **5- and 22-session contexts:** Report first and last OI, net OI change (last OI minus first OI) and net OI change percentage ((last OI / first OI - 1) × 100), where the exact contract has valid, continuous OI observations throughout the selected window.
- The 5- and 22-session window summaries are first-to-last changes, not sums of daily OI changes or sums/averages of daily percentage changes.
- If a contract OI observation is missing within a window, report the window-level OI change as unavailable; do not bridge the gap. Preserve the actual observation count and continuity/missing-session status.
- Percentage OI change is unavailable when its reference OI is missing or zero. Do not replace an unavailable percentage with zero.

#### Calculation and continuity safeguards

- Calculate each feature separately for the exact contract identity: NIFTY underlying, selected expiry, strike, option type and instrument ID.
- Use the immediately preceding validated trading-session OI observation for daily changes. If that adjacent session's observation is missing, mark the daily change unavailable; do not bridge the gap or substitute another contract.
- A valid OI value of zero must be preserved as an observed value, not treated as missing.
- Absolute OI change remains calculable when the previous OI is zero, provided both current and previous OI observations are valid.
- Percentage OI change is unavailable when the previous OI is zero or missing. Do not emit infinity, substitute zero or use another denominator.
- For 5- and 22-session net changes, both endpoints and all intervening expected contract observations must be valid for the exact same contract. A missing observation makes that window-level summary unavailable.
- Retain source OI observations unchanged and preserve trade-date, contract identity and source provenance.
- OI change describes the change in outstanding open contracts only. It does not independently establish buyer/seller identity, fresh writing, unwinding, long buildup, short buildup, seller dominance or a trading signal.
- Logarithmic OI change and symmetric percentage OI change are not approved Phase 4 features. They remain outside the approved catalogue unless separately reviewed.

### 10.8 Owner-approved CE/PE volume features

The project owner approved the following descriptive volume features for the Phase 4 CE/PE contract feature catalogue:

| Feature | Definition | Review status |
|---|---|---|
| Absolute volume change | Current EOD traded volume minus the immediately preceding validated trading-session EOD traded volume for the exact same contract | Approved |
| Percentage volume change (%) | (Current EOD traded volume / immediately preceding validated trading-session EOD traded volume - 1) × 100 | Approved |
| Volume/OI ratio | Current EOD traded volume / current EOD open interest for the exact same contract and date | Approved |
| Total volume | Sum of valid observed EOD traded volume within the selected 1-, 5- or 22-session context | Approved |
| Average daily volume | Total valid observed EOD traded volume divided by the number of valid volume observations in the selected context | Approved |

#### 1/5/22-session context

- **Daily changes:** Calculate absolute and percentage volume change for each available EOD observation against the immediately preceding validated trading-session observation for the exact same contract. For the 1-session context, the prior observation is a calculation dependency outside the window and is not counted as a window observation.
- **Volume/OI ratio:** Calculate for each available EOD observation using that date's volume and OI for the exact same contract. Preserve the daily ratio observations in the 1-, 5- and 22-session contexts. No additional window average or aggregate ratio is approved.
- **Total volume:** Sum valid observed volume within each 1-, 5- or 22-session context.
- **Average daily volume:** Divide the context's total valid observed volume by its actual number of valid volume observations, not by calendar days or an assumed number of sessions.
- Report the expected window size, actual valid volume observation count and calculation status. If one or more expected contract observations are missing, a total or average based on the remaining valid observations must be marked partial and must not be presented as a complete-window result. If no valid volume observations exist, the result is unavailable.
- For a complete window, total volume is the sum across all expected valid contract observations and average daily volume is that total divided by the number of observations in the window. In a 1-session complete window, total and average daily volume both equal that session's volume.

#### Calculation and continuity safeguards

- Calculate each feature separately for the exact contract identity: NIFTY underlying, selected expiry, strike, option type and instrument ID.
- Use the immediately preceding validated trading-session volume observation for daily changes. If that adjacent session's contract observation is missing, mark the daily change unavailable; do not bridge the gap or substitute another contract.
- A valid zero-volume observation must be preserved and included in window totals and observation counts. Missing volume is not zero.
- Absolute volume change remains calculable when previous volume is zero, provided both current and previous volume observations are valid.
- Percentage volume change is unavailable when previous volume is zero or missing. Do not emit infinity or substitute zero.
- Volume/OI ratio is unavailable when current OI is zero or missing, or when current volume is missing. A valid zero-volume observation with positive valid OI produces a valid ratio of zero.
- Do not bridge missing contract observations. Preserve actual observation counts, partial/unavailable status and continuity/missing-session flags.
- Retain source volume and OI observations unchanged and preserve trade-date, contract identity and source provenance.
- Volume and Volume/OI ratio describe recorded traded quantity relative to open interest. They do not independently establish buyer/seller identity, fresh writing, unwinding, long buildup, short buildup, seller dominance or a trading signal.
- Logarithmic volume change, symmetric percentage volume change, volume moving average as a separate indicator, cumulative volume as a separate feature and relative-volume indicators are not approved in this section. They remain outside the Phase 4 catalogue unless separately reviewed.

### 10.9 Owner-approved CE/PE volume-weighted premium return

The project owner approved Volume-Weighted Premium Return (VWPR) as a descriptive CE/PE premium–volume relationship feature for 5- and 22-session contexts only.

For a selected context of N observations:

`VWPR_N = sum(R_t × V_t) / sum(V_t)`

Where:
- `R_t` is the daily simple premium return in percentage points for the exact same contract: `(P_t / P_(t-1) - 1) × 100`.
- `V_t` is the current session's valid EOD traded volume for that exact same contract.
- `N` is 5 or 22 validated EOD observations, including the Analysis Date.

VWPR is the volume-weighted average of the daily simple premium returns in the selected window. It is not the cumulative premium return across the window and must not be labelled as such.

#### Window and calculation rules

- Calculate VWPR independently for each exact contract identity: NIFTY underlying, selected expiry, strike, option type and instrument ID. Never combine CE and PE, different strikes or different expiries.
- Calculate daily premium return using the immediately preceding validated trading-session closing premium for the same contract. For the earliest observation in a 5- or 22-session window, the preceding close is a calculation dependency outside the window and is not counted as a window observation.
- VWPR is available only when all N daily premium returns and their corresponding EOD volume observations are valid and the sum of volume across the window is greater than zero. If any required return or volume observation is missing, or if total volume is zero, mark VWPR unavailable; do not silently calculate a complete-window result from a reduced subset.
- A valid zero-volume observation remains part of the window and its daily return must be valid, but it contributes zero weight to the numerator and denominator. Missing volume is not zero.
- Preserve the daily premium returns and volume observations used in the calculation, along with expected and actual observation counts, first/last dates and calculation status.
- Use full calculation precision internally. Presentation rounding remains an output-schema decision.

#### Interpretation limits

- VWPR describes the volume-weighted average of observed daily premium returns for one exact contract over the selected historical window.
- A positive or negative VWPR does not establish whether buyers or sellers initiated the trades, identify participant positions, prove fresh writing or unwinding, or establish seller dominance or a trading signal.
- VWPR is not actual traded turnover. Do not calculate turnover as EOD closing premium multiplied by reported volume.
- Pearson correlation, Spearman correlation, premium-change-times-volume, log-volume relationships, turnover proxies and additional premium–volume indicators are not approved by this decision. They remain outside the Phase 4 catalogue unless separately reviewed.
- VWPR is not defined for the 1-session context; retain the already-approved daily premium return and volume features separately for that context.

### 10.10 Owner-approved CE/PE OI–premium relationship analysis

The project owner approved Spearman Rank Correlation as the selected descriptive method for examining the relationship between daily percentage OI change and daily simple premium return for an exact CE/PE contract.

**Selected relationship measure:**

`Spearman ρ = SpearmanRankCorrelation(ΔOI%, R_p)`

Where:
- `ΔOI%` is the approved daily percentage OI change for the exact same contract: `(OI_t / OI_(t-1) - 1) × 100`.
- `R_p` is the approved daily simple premium return in percentage points for the exact same contract: `(P_t / P_(t-1) - 1) × 100`.
- Each OI-change value and premium-return value must refer to the same contract and the same trading-date observation.

#### Window application

- **1-session context:** Do not calculate a correlation coefficient. Retain the Analysis Date's daily percentage OI change and daily simple premium return as separate features, subject to their existing validity rules.
- **5-session context:** Preserve the date-aligned valid OI-change/premium-return pairs and report their count and coverage. Do not calculate or publish a 5-session correlation coefficient; five observations are too few to support a useful relationship assessment.
- **22-session context:** Calculate Spearman Rank Correlation only when all 22 expected date-aligned OI-change/premium-return pairs are valid (22/22). If even one pair is missing or invalid, the 22-session coefficient is `UNAVAILABLE`; do not calculate from a reduced subset or publish a partial coefficient.
- Report the expected pair count (22), actual valid paired-observation count, first/last paired dates, coverage status and missing-pair reasons alongside the statistic. The prior-session OI and premium observations needed to calculate the first pair remain dependencies outside the 22-observation window.

#### Pairing, continuity and calculation safeguards

- Calculate independently for the exact contract identity: NIFTY underlying, selected expiry, strike, option type and instrument ID. Never combine CE and PE, different strikes or different expiries.
- Pair `ΔOI%` and `R_p` by the same trading date and exact contract. Each daily value uses the immediately preceding validated trading-session observation for that same contract.
- If the prior OI or prior closing premium is missing, if either current input is missing, or if either percentage-change denominator is zero, that date does not produce a valid pair. Do not bridge missing contract observations, substitute another contract or replace unavailable values with zero.
- Preserve valid observed zero OI and zero premium values. The existing percentage-change rules still apply: percentage OI change is unavailable when prior OI is zero, and premium return is unavailable when prior closing premium is zero.
- The prior-session OI and premium observations needed for the earliest date in the selected window are calculation dependencies only; they are not counted as observations in the N-session window.
- If either variable has no variation across the valid paired observations, Spearman correlation is undefined and must be reported as unavailable with the reason. Handle tied ranks using a standard Spearman rank-correlation implementation; do not add custom tie-breaking rules.
- Preserve the paired input values and their dates so the coefficient can be reproduced. Retain full calculation precision internally; presentation rounding remains an output-schema decision.

#### Interpretation limits and exclusions

- Spearman correlation describes the strength and direction of a monotonic association between daily percentage OI changes and daily premium returns in the observed exact-contract sample. It does not establish causation or predictive power.
- A positive or negative coefficient does not identify buyers or sellers, prove fresh writing or unwinding, establish long/short buildup, demonstrate seller dominance or create a trading signal.
- Do not define coefficient thresholds, labels, scoring weights or decision rules in Phase 4.
- Pearson correlation, OI-change-times-premium-return, OI-weighted premium return, directional quadrant classification and other OI–premium relationship measures are not approved by this decision. They remain outside the Phase 4 catalogue unless separately reviewed.


### 10.11 Owner-approved remaining Phase 4 design decisions

#### Feature display precision

- Retain full calculation precision internally; do not round or overwrite stored calculation values for presentation.
- Display decimal precision is feature-specific and should be selected according to the feature's units, scale and report/UI readability. There is no single fixed decimal-place rule for every feature.
- Apply rounding only at the presentation boundary. The presentation layer may choose the appropriate number of decimal places for each feature without changing the underlying stored value.

#### Spot-to-strike distance

For each selected-expiry contract, using the Analysis Date NIFTY spot close:

- Distance in points: `Spot Close - Strike Price`.
- Distance percentage: `((Spot Close - Strike Price) / Spot Close) × 100`.
- A missing or zero Spot Close makes the percentage distance unavailable; preserve the points value only when both Spot Close and Strike Price are valid.
- Retain the signed values. Do not convert the distance into an absolute value in the stored feature.
- These are descriptive context features, not standalone trading signals.

#### ITM / ATM / OTM classification

Use the standard option moneyness convention for the selected expiry and Analysis Date:

| Classification | CE (Call) | PE (Put) |
|---|---|---|
| ITM | Spot Close > Strike | Spot Close < Strike |
| ATM | Strike is the nearest listed strike to Spot Close | Strike is the nearest listed strike to Spot Close |
| OTM | Spot Close < Strike | Spot Close > Strike |

- Determine the nearest listed strike from the valid listed strikes available for the selected expiry and Analysis Date; do not introduce a fixed arbitrary ATM point band.
- If Spot Close exactly equals a listed strike, that strike is ATM.
- If Spot Close is exactly midway between two nearest listed strikes, mark both as ATM candidates; do not arbitrarily select one.
- Apply the ITM/OTM comparison separately for CE and PE to all other strikes.
- If the required spot close or selected-expiry strike universe is unavailable, classification is unavailable with a reason.
- Moneyness is descriptive contract context only. It does not establish premium value, seller identity or a trading signal.

#### Logical feature output record

Each calculated feature is represented as its own structured feature record, rather than placing all features into one undifferentiated JSON result. The logical record includes:

- Feature name and feature-definition version.
- Feature value, where available.
- Calculation status: `AVAILABLE`, `PARTIAL`, `UNAVAILABLE` or `INVALID`.
- Analysis Run ID, Analysis Date and selected Expiry.
- Context window (1, 5 or 22 sessions), where applicable.
- Exact contract identity (NIFTY underlying, expiry, strike, option type and instrument ID), where applicable; spot-level features do not require a contract identity.
- Expected and actual observation counts, plus first/last source dates where applicable.
- Source references and provenance, including source hashes/row references required to reproduce the calculation.
- Calculation parameters and missingness/quality reason when the result is partial, unavailable or invalid.

This is the approved logical output contract. Physical database table design, column types, indexes and migrations remain subject to implementation review.

#### Versioned deterministic upsert and history preservation

- Use a deterministic record identity composed of Analysis Run ID, feature-definition version, feature name, contract identity when applicable, Analysis Date and context window.
- Reprocessing the same logical feature under the same identity must upsert the existing record rather than create a duplicate.
- A new feature-definition version must create a separately identifiable result; do not overwrite or delete results produced by an earlier feature-definition version.
- Preserve source provenance and calculation parameters with each record so that a result can be traced and reproduced.
- Spot-level features omit contract identity from the identity components; contract-level features include the full exact contract identity.
- This defines logical idempotency behaviour only; it does not authorize a database migration or dictate a physical storage implementation.

#### Phase 4 delivery boundary

- Implement feature calculations in a backend feature engine.
- Expose calculated feature results through a read-only API.
- Do not build the full dashboard/UI as part of Phase 4; later dashboard work may consume the read-only API.
- Exact API routes, request/response schemas, authentication/permissions and integration details remain implementation-level design work and must be reviewed before implementation.
- This boundary does not authorize live/intraday data, broker connectivity, order execution, alerts, paper trading or backtesting.

#### Missing contract observation handling

- A contract row absent for a required trading date is a missing observation, never a zero-valued observation.
- Mark only the affected contract feature or feature window as `UNAVAILABLE` when its required observations are incomplete.
- Continue calculating other contracts and unaffected features normally; one missing contract observation must not reject the entire Analysis Run.
- Do not bridge missing sessions, forward-fill, interpolate or substitute another strike, option type, expiry or instrument.
- Preserve the missing date, exact contract identity, expected/actual observation counts and the reason for unavailability.
