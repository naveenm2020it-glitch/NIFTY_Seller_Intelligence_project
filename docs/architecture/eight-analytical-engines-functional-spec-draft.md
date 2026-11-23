# Eight Analytical Engines — Functional Specification Draft

**Status:** Draft for project-owner review; proposed functional decomposition, not yet approved  
**Project:** NIFTY Seller Intelligence  
**Scope:** NIFTY 50 and NIFTY CE/PE only; historical end-of-day (EOD) analysis  
**Depends on:** Phase 0–3 foundation and the Phase 3 EOD data contract  
**Purpose:** Define what each of the eight analytical engines is responsible for before finalizing the EOD report inventory.

> **Approval boundary:** The project materials establish the need for eight analytical engines and describe the required analytical capabilities, but they do not provide an approved list of eight engine names, formulas or contracts. The eight names and boundaries below are a proposed decomposition of those documented capabilities. They must be reviewed and approved before implementation. No formula or report dependency in this draft should be treated as final.

---

## 1. Design principles and scope

The engines should work together as a traceable analytical pipeline. Each engine has a distinct responsibility, consumes validated EOD data or outputs from earlier engines, and produces structured results with evidence and limitations.

The system is intended to:
- Analyze the selected Analysis Date and Expiry using historical EOD information.
- Use the specified 1-, 5- and 22-session views where relevant, while retaining the larger historical archive for research, pattern validation and model development.
- Analyze NIFTY 50 and NIFTY CE/PE contracts only.
- Identify historical price structure, contract positioning clues, premium behaviour, possible seller traps and option-buyer opportunities.
- Generate the project's eight market scenarios through a separate decision engine.
- Explain which observations support a conclusion and which data are missing.

The system is not intended to:
- Provide live or intraday analysis.
- Claim that daily OHLC proves the sequence of intraday events, bid/ask pressure or the exact time a seller trap occurred.
- Claim that aggregate participant reports identify the writer of a particular NIFTY strike or expiry.
- Execute trades, connect to brokers or place orders.
- Treat a model-estimated value as an exchange-published value.
- Change approved rules or models without validation, versioning and controlled approval.

**User inputs remain Analysis Date and Expiry only.** No cutoff-time input is introduced.

## 2. Proposed eight-engine overview

| No. | Proposed engine | Main responsibility | Main output |
|---:|---|---|---|
| 1 | Market Regime and Trend Engine | Describe the broader NIFTY 50 market condition and recent trend | Regime, trend and supporting measurements |
| 2 | Price Structure and Key Levels Engine | Identify historical support/resistance areas and price-structure events | Levels, structure observations and break/failure candidates |
| 3 | Contract OI and Positioning Engine | Analyze NIFTY CE/PE contract-level OI, OI changes and volume | Contract positioning observations and evidence strength |
| 4 | CE/PE Premium Behaviour Engine | Analyze option premium movement and relative CE/PE behaviour | Premium behaviour, relative strength and candidate triggers |
| 5 | Volatility and Pricing Context Engine | Describe realized-volatility context and clearly labelled pricing estimates | Volatility context and assumption-labelled estimates |
| 6 | Participant Positioning Context Engine | Add broad participant-category positioning/activity context when verified data exists | Aggregate participation context with scope warnings |
| 7 | Seller Trap and Setup Detection Engine | Combine outputs from Engines 1–6 to identify possible seller traps and option-buyer setups | Explainable setup candidates, direction and invalidation conditions |
| 8 | Eight-Scenario Decision Engine | Evaluate the defined eight market scenarios using validated upstream outputs | Scenario classification, evidence, alternatives and confidence |

These are proposed names and responsibilities. The eight-scenario engine is retained as one of the eight because the project roadmap explicitly calls for an eight-scenario decision engine. The other seven are a proposed split of the documented analytical capabilities.

## 3. Functional specification by engine

### Engine 1 — Market Regime and Trend Engine

**Purpose**

Describe the current historical EOD condition of NIFTY 50 so that downstream engines do not interpret option data without underlying-market context.

**What it will do**
- Read the validated NIFTY 50 daily OHLC history.
- Calculate and compare 1-, 5- and 22-session price changes and ranges, where the available history supports the selected window.
- Describe trend direction, trend persistence, range-bound behaviour and changes in realized volatility.
- Compare the selected session with the preceding historical context.
- Flag conflicting evidence, such as a positive short window inside a negative longer window.
- Return a neutral/uncertain classification when evidence is mixed or insufficient.

**Expected inputs**
- NIFTY 50 EOD OHLC by trade date.
- Historical session calendar and validated prior sessions.
- Versioned feature definitions and parameters.

**Expected outputs**
- Regime label (the allowed label set is to be approved).
- Trend direction and strength descriptors.
- 1/5/22-session measurements and the observations used.
- Data sufficiency and conflict flags.
- Explanation and source provenance.

**Boundaries**
- This engine describes the underlying index; it does not decide whether to buy CE or PE.
- EOD data cannot confirm an intraday trend path.
- FOVOLT, if later approved, is a supplementary underlying/futures volatility reference, not option implied volatility.

**Acceptance checks**
- Reproducible results for the same source data and feature version.
- Correct handling of missing sessions and insufficient lookback.
- No fabricated zero values for unavailable observations.
- Output clearly distinguishes measured values from descriptive labels.

### Engine 2 — Price Structure and Key Levels Engine

**Purpose**

Identify historically supported NIFTY 50 price areas and describe whether the selected EOD close is approaching, testing, crossing or rejecting those areas.

**What it will do**
- Derive candidate support/resistance areas from historical NIFTY 50 OHLC observations.
- Identify relevant prior highs/lows, repeated reaction areas and range boundaries according to approved rules.
- Compare the selected session's OHLC and close with those candidate levels.
- Identify EOD breakout, breakdown, hold and failure candidates only where the daily observations support the label.
- Provide the historical observations behind each level and its age/relevance.
- Pass level context to the Seller Trap and Setup Detection Engine.

**Expected inputs**
- NIFTY 50 EOD OHLC history.
- Approved lookback and level-calculation definitions.
- Market-session dates.

**Expected outputs**
- Candidate support/resistance levels or zones.
- Level type, calculation method/version and supporting dates.
- Distance from selected close, expressed in the approved units.
- EOD interaction label and evidence.
- Invalidation or re-evaluation conditions.

**Boundaries**
- Do not describe a daily high/low touch as a confirmed intraday rejection.
- Do not invent precision beyond the source price precision.
- No supplementary NSE report is currently identified as mandatory for this engine.

**Acceptance checks**
- Every level can be traced to historical observations.
- Same inputs and rule version produce the same levels.
- The engine marks weakly supported levels and avoids presenting them as certain support/resistance.

### Engine 3 — Contract OI and Positioning Engine

**Purpose**

Analyze NIFTY CE/PE contract-level open interest and trading activity to identify changes in contract positioning that may be relevant to option sellers and buyers.

**What it will do**
- Analyze contract rows for the selected expiry and supported NIFTY strikes.
- Compare current OI with prior available EOD sessions and calculate OI changes using an approved definition.
- Compare OI changes with option premium and underlying movement.
- Examine volume alongside OI without treating volume as a closing position.
- Identify concentrations and changes across strikes, calls and puts.
- Distinguish observed contract facts from inferred interpretations such as possible long build-up, short build-up, short covering or long unwinding.
- Flag insufficient history, contract mapping problems and expiry changes.

**Expected inputs**
- NIFTY CE/PE contract EOD OHLC, volume and OI.
- Contract identity: instrument ID, expiry, strike and option type.
- Underlying close and historical session records.
- MII contract metadata and source provenance.

**Expected outputs**
- Per-contract OI and OI-change measurements.
- Strike/expiry-level summaries and CE/PE comparisons.
- Positioning interpretation candidates with evidence and caveats.
- Data coverage and confidence/sufficiency flags.

**Boundaries**
- OI alone does not identify whether a new position is a buyer or seller.
- OI plus price/volume behaviour can support an interpretation, not prove the identity or intent of a writer.
- Participant-wise OI is aggregate context and cannot be attributed to a specific NIFTY contract.
- Do not mix different expiries without explicitly labelling the aggregation.

**Acceptance checks**
- Contract identity and expiry are validated before comparison.
- OI changes use the correct prior contract/session.
- Zero-volume and missing-contract cases are handled explicitly.
- Interpretations are labelled as inference, not direct observation.

### Engine 4 — CE/PE Premium Behaviour Engine

**Purpose**

Understand how NIFTY call and put premiums behave relative to the underlying index and to each other, and identify historically derived premium conditions that may become option-buyer triggers.

**What it will do**
- Analyze CE/PE EOD OHLC for the selected expiry.
- Compare premium movement with NIFTY 50 movement, strike position and time-to-expiry context.
- Compare premium behaviour across 1-, 5- and 22-session windows where sufficient data exists.
- Identify expansion, contraction, relative strength/weakness and unusual EOD premium changes using approved definitions.
- Generate candidate CE/PE premium trigger levels or conditions for downstream evaluation.
- Record the conditions under which a trigger becomes invalid.

**Expected inputs**
- NIFTY CE/PE EOD OHLC, volume and OI.
- Strike, expiry and option type.
- NIFTY 50 EOD OHLC/close.
- Historical contract continuity and session dates.

**Expected outputs**
- Per-contract and selected-strike premium behaviour.
- CE-versus-PE relative behaviour.
- Candidate premium trigger and invalidation conditions.
- Measurement window, calculation version and supporting observations.

**Boundaries**
- A trigger derived from EOD data is an EOD condition, not an intraday entry instruction.
- Do not assume a premium change is caused by directional demand alone; volatility and time-to-expiry can also affect premium.
- Do not label a trigger as adaptive until the adaptation method and validation criteria are approved.

**Acceptance checks**
- Premium comparisons use matching contract identities and dates.
- Expiry and strike differences are not silently mixed.
- Trigger values are reproducible and accompanied by evidence and invalidation conditions.

### Engine 5 — Volatility and Pricing Context Engine

**Purpose**

Provide volatility context for interpreting option premiums and, only when approved assumptions are available, calculate clearly labelled model-derived option-pricing measures.

**What it will do**
- Calculate historical realized-volatility features from the NIFTY 50 EOD series using an approved methodology.
- Compare current realized-volatility context with historical observations.
- Optionally consume FOVOLT as an independently sourced underlying/futures volatility reference after its current schema and methodology are verified.
- If separately approved, estimate option implied volatility or pricing sensitivities from option prices using a documented pricing model and explicit assumptions.
- Record assumptions such as interest rate, dividend treatment, day-count convention, expiry-time convention and model choice.
- Flag estimates that are unstable or not identifiable from the available EOD data.

**Expected inputs**
- NIFTY 50 EOD price history.
- NIFTY option EOD prices and contract metadata.
- Time-to-expiry calculation and approved pricing assumptions.
- Optional verified FOVOLT report.
- Any separately approved rate/dividend inputs.

**Expected outputs**
- Realized-volatility measurements and methodology version.
- Optional FOVOLT comparison with source provenance.
- If approved, model-derived IV/Greeks or pricing context with all assumptions disclosed.
- Quality flags and reasons an estimate is unavailable.

**Boundaries**
- FOVOLT is not NIFTY option implied volatility and is not a strike-wise volatility surface.
- A model-derived IV estimate must never be represented as an exchange-published IV.
- The old 2013 NSE technical-specification reference to an implied-volatility file is unverified and is not a current dependency.
- Do not publish Greeks or IV when required inputs/assumptions are missing.

**Acceptance checks**
- Every model-derived value carries its model and assumption version.
- Independent test cases validate numerical implementation.
- Missing assumptions result in unavailable estimates, not invented defaults.

### Engine 6 — Participant Positioning Context Engine

**Purpose**

Add broad market participant-category context where a current, permitted and validated supplementary report provides useful information beyond contract-level Bhavcopy data.

**What it will do**
- If approved and available, parse participant-wise OI by its documented participant and instrument categories.
- Compare category-level index-option/index-futures long and short measures across report dates.
- Optionally compare participant-wise trading volume as activity context.
- Identify broad category-level changes and compare them with the NIFTY market context.
- Keep this context separate from contract-specific OI and avoid attributing aggregate positions to NIFTY strikes.
- Mark each optional report as available, pending, unavailable or invalid; absence must not be interpreted as zero.

**Expected inputs**
- Optional current-format participant-wise OI report.
- Optional current-format participant-wise volume report.
- Verified schema, units, category definitions, report date and publication behaviour.
- Core NIFTY EOD context for comparison.

**Expected outputs**
- Participant-category aggregate observations.
- Report availability and validation status.
- Broad participation context with explicit instrument-scope labels.
- Provenance and caveats.

**Boundaries**
- Participant reports are not NIFTY-strike-specific.
- Participant volume is activity, not closing position and not proof of net writing.
- FII derivatives statistics, Market Activity, Combined/NCL OI and clearing-member reports remain deferred until current samples and distinct value are demonstrated.
- This engine must be optional to the core pipeline; missing supplementary data must not block analysis.

**Acceptance checks**
- Current report schema and units are documented and validated.
- Aggregate values are not presented as NIFTY-only facts unless the source explicitly supports that scope.
- Missing reports remain unavailable/pending rather than zero.
- The engine demonstrates distinct value before any report becomes a recurring dependency.

### Engine 7 — Seller Trap and Setup Detection Engine

**Purpose**

Combine validated outputs from Engines 1–6 to identify possible option-seller traps and explainable CE/PE opportunities for option buyers.

**What it will do**
- Combine underlying regime, price structure, contract OI, premium behaviour and volatility context.
- Identify confluence and contradiction between independent evidence groups.
- Detect candidate situations where the observed EOD evidence suggests that an option-selling position may be vulnerable.
- Distinguish CE-side and PE-side setup candidates.
- Explain the suspected seller-trap mechanism using the evidence actually available.
- Produce candidate option-buyer setups with trigger conditions, invalidation conditions and reasons to avoid a setup.
- Assign an evidence-strength/confidence description using an approved method, not an unsupported probability.
- Store the exact upstream engine versions and source records used for each candidate.

**Expected inputs**
- Outputs and evidence from Engines 1–6.
- Approved seller-trap definitions and setup rules.
- Historical pattern records and validation results, when available.

**Expected outputs**
- Setup candidate ID and direction (CE/PE/none).
- Seller-trap classification candidate and explanation.
- Supporting and conflicting evidence.
- Candidate trigger and invalidation conditions.
- Evidence sufficiency, confidence method/version and risk warnings.
- Exact source/engine versions used.

**Boundaries**
- EOD data can identify historical EOD seller-trap candidates; it cannot confirm the intraday sequence or exact moment of a trap.
- A high OI value or a single premium move is not sufficient by itself to prove a seller trap.
- The engine must be allowed to return no setup.
- It must not issue an order or imply guaranteed profit.

**Acceptance checks**
- Every setup is explainable from recorded upstream evidence.
- Conflicting evidence reduces confidence or produces an indeterminate result.
- Historical validation uses later observations not used to create the candidate.
- The engine can return no-trade/no-setup when evidence is inadequate.

### Engine 8 — Eight-Scenario Decision Engine

**Purpose**

Evaluate the project's eight defined market scenarios and consolidate upstream analysis into a consistent, explainable decision output.

**What it will do**
- Evaluate each of the eight scenarios against approved scenario definitions and conditions.
- Consume upstream engine outputs rather than independently re-parsing raw source files.
- Record which scenario conditions are met, not met, conflicting or unevaluable.
- Rank or classify scenario relevance only after the ranking method is approved.
- Connect a scenario to relevant CE/PE setup candidates where evidence supports it.
- Explain the alternative scenarios and what future EOD evidence would strengthen or invalidate the current classification.
- Return an uncertain/insufficient-evidence result when the data does not support a reliable classification.

**Expected inputs**
- Outputs from Engines 1–7.
- Approved definitions for all eight scenarios.
- Versioned thresholds, priority rules and conflict-resolution rules.
- Data sufficiency and provenance metadata.

**Expected outputs**
- Results for all eight scenarios.
- Conditions satisfied/failed/unknown for each scenario.
- Primary and alternative scenario classifications, if the approved rules permit ranking.
- Related CE/PE setup candidates or explicit no-setup result.
- Evidence summary, uncertainty, invalidation conditions and version metadata.

**Important unresolved item**

The current reviewed project documents do not enumerate the names or definitions of the eight scenarios. This draft therefore does not invent them. The scenario catalogue, conditions and acceptance examples must be documented and approved separately before this engine can be fully specified or implemented.

**Acceptance checks**
- All eight scenarios have an explicit approved definition.
- Unknown or missing inputs are not silently treated as false or zero.
- Scenario results can be reproduced from the same upstream versions.
- The engine explains why a scenario was selected and why alternatives were not selected.

## 4. Supporting feedback-learning architecture — separate from the eight engines

The uploaded Development Approach Review defines four feedback-learning components. They should support the eight analytical engines, but they should not be counted as four of the eight market-analysis engines.

1. **Pattern Discovery Engine:** discovers candidate recurring patterns from historical 1/5/22-session analysis and the larger archive.
2. **Pattern Knowledge Base:** stores approved patterns, evidence, confidence, provenance and versions.
3. **Feedback Intelligence Engine:** classifies analytical, pattern and outcome feedback and identifies which engine or rule may need review.
4. **Pattern Optimization Engine:** proposes candidate improvements and compares them with the approved version through historical validation.

Learning safeguards:
- Positive feedback alone does not prove a pattern was correct; negative feedback alone does not prove it was wrong.
- Outcome feedback requires subsequent EOD observations.
- Candidate changes must be tested on separate historical observations and must not use overlapping windows as if they were independent samples.
- Approved patterns/models must remain versioned and rollback-capable.
- No unrestricted self-modification. Production changes require validation and approval.

## 5. Proposed engine execution flow

1. Phase 3 validates and persists the selected Analysis Date and Expiry EOD data.
2. Engines 1 and 2 analyze the NIFTY 50 underlying context and price structure.
3. Engines 3, 4 and 5 analyze contract positioning, premium behaviour and volatility/pricing context.
4. Engine 6 adds optional participant-category context when verified data is available; otherwise it reports unavailable and continues.
5. Engine 7 combines the evidence and produces seller-trap/setup candidates.
6. Engine 8 evaluates the eight scenarios and creates the consolidated decision output.
7. The feedback-learning components store feedback, outcomes and candidate pattern improvements separately.

This is a logical dependency flow, not a commitment to a specific runtime, queue or parallel-execution design.

## 6. Common output and audit contract

Every engine result should include, at minimum:

- Analysis Run ID, Analysis Date and selected Expiry.
- Engine name, engine version and rule/feature version.
- Input record references and source provenance.
- Calculation window and relevant historical session dates.
- Measured values separated from inferred labels.
- Result, explanation and supporting evidence.
- Missing, invalid or conflicting input flags.
- Confidence/evidence method and value only where formally defined.
- Limitations and invalidation conditions.
- Created timestamp and reproducibility metadata.

An engine must not silently substitute missing values, mix incompatible expiries, or present an inference as a directly observed fact.

## 7. EOD report dependency implications — preliminary only

This section is a starting point for the next report review. It does not finalize the report inventory.

| Engine | Current core EOD inputs | Supplementary report position |
|---|---|---|
| 1. Market Regime and Trend | NIFTY 50 All Indices OHLC | FOVOLT optional cross-check; core history can support internally calculated realized-volatility features |
| 2. Price Structure and Key Levels | NIFTY 50 OHLC | No supplementary report currently identified |
| 3. Contract OI and Positioning | F&O Bhavcopy + MII contract identity | Participant-wise OI optional aggregate context only |
| 4. CE/PE Premium Behaviour | F&O Bhavcopy + MII contract identity + NIFTY close | No additional report proven mandatory; option IV source remains unverified |
| 5. Volatility and Pricing Context | NIFTY OHLC + option EOD prices + contract metadata | FOVOLT optional; it is not option IV |
| 6. Participant Positioning Context | Core contract data for comparison | Participant-wise OI highest-priority candidate; participant volume lower-priority optional |
| 7. Seller Trap and Setup Detection | Validated outputs from Engines 1–6 | No extra report inherently required; depends on approved definitions and evidence |
| 8. Eight-Scenario Decision | Validated outputs from Engines 1–7 | No extra report proven mandatory; scenario definitions are still required |

The three Phase 3 mandatory source reports remain the starting foundation:
1. F&O UDiFF Common Bhavcopy Final.
2. F&O MII Contract File.
3. NSE Indices All Indices daily-close CSV.

Do not add optional reports merely because they appear in the NSE catalogue. A supplementary report should be considered only after its current permitted sample, schema, units, row grain, report date, publication behaviour, missing-day behaviour, provenance and distinct analytical value are verified.

Known evidence limits:
- Participant-wise OI/volume is aggregate index/stock category context, not NIFTY-contract-specific attribution.
- FOVOLT is an underlying/futures volatility reference, not option IV.
- Daily OHLC cannot confirm intraday price sequence or exact seller-trap timing.
- Option IV/Greeks need explicit, versioned assumptions unless a current exchange-published source is verified.
- Missing optional reports are unavailable/pending, never zero.

## 8. Decisions required to approve this specification

The following must be reviewed before the engine contracts are treated as final:

1. Approve, rename, combine or split the eight proposed engines.
2. Confirm the purpose and boundary of each engine and whether Engine 6 (participant context) should remain one of the eight or be treated as an optional supporting module.
3. Define the exact eight scenario names and their conditions for Engine 8.
4. Approve the measurements, formulas, thresholds, lookback definitions and confidence method for each engine.
5. Define the exact output fields and acceptance examples for each engine.
6. Confirm which engines must still produce a result when optional supplementary reports are unavailable.
7. Only after these decisions, finalize the engine-to-report dependency matrix and decide whether any additional EOD report ingestion is justified.

## 9. Source basis and evidence boundary

This draft is based on:
- Uploaded **Development Approach Review.txt**: 1/5/22-session analysis, seller-pattern discovery, potential seller traps, adaptive CE/PE premium triggers, eight scenarios, and the four separate feedback-learning components with controlled validation/versioning.
- Repository **docs/data/analytical-engine-report-dependency-matrix.md**: capability-level data needs, three mandatory Phase 3 reports, supplementary report caveats and unresolved eight-engine specification gap.
- Repository **docs/data/eod-report-inventory-review.md**: current report inventory research and supplementary-report limitations.
- Repository **docs/development/phase-3-data-contract.md**: actual normalized NIFTY 50 and NIFTY CE/PE EOD data contract.

The source materials do not provide the final eight engine names, formulas, thresholds, scenario definitions or acceptance criteria. Those remain proposed or unresolved in this document. No new NSE report acquisition, implementation, deployment or change to Phase 3 is authorized by this draft.
