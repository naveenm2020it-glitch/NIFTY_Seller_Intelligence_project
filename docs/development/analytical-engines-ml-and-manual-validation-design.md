# Analytical Engines, ML Models and Manual Validation Design

**Status:** Design draft for owner review  
**Branch:** `phase-4-feature-engineering`  
**Change type:** Documentation only  
**Implementation status:** No engine, ML model, database schema, migration, API, UI or deployment changes are authorized by this document.

## 1. Purpose and operating approach

The application must produce a complete, evidence-backed NIFTY Seller Intelligence report from validated historical EOD data. The owner will inspect the generated output, identify incorrect or weak analysis, and provide corrections. The project will use those corrections to investigate and improve the responsible analytical engine or model.

The development loop is:

1. Prepare validated historical EOD inputs.
2. Calculate the approved 1/5/22-session features.
3. Run the eight analytical engines in their defined dependency order.
4. Produce the required report outputs with evidence and limitations.
5. Let the project owner manually review the output.
6. Classify feedback as analytical, pattern or outcome feedback.
7. Identify the responsible engine, rule, feature or model.
8. Propose a versioned improvement.
9. Validate the candidate against separate chronological historical observations.
10. Promote only after review and validation; preserve the prior approved version and rollback path.

This is a controlled self-improving intelligence system, not an unrestricted self-modifying AI. A feedback cycle may improve the system, but improved accuracy is not guaranteed.

## 2. Project phase boundaries

The established roadmap separates the work:

- Phase 4 — Feature Engineering (1/5/22 sessions).
- Phase 5 — Eight Analytical Engines.
- Phase 6 — Eight-Scenario Decision Engine.
- Phase 7 — Four ML Models.
- Phase 8 — Complete Web Dashboard.
- Phase 9 — QA and Production Readiness.
- Phase 10 — Feedback and Continuous Pattern Learning.

Phase 4 remains a descriptive feature-preparation layer. It must not issue BUY CE, BUY PE or WAIT, and it does not implement the eight engines or four ML models.

The eight analytical engines and four ML models are separate components. Analytical engines establish explainable calculations and evidence; ML models learn patterns or assess defined targets using suitable historical samples. AI may explain and summarize engine outputs, but it must not invent calculations, evidence, probabilities or market facts.

## 3. Eight analytical engines — required responsibilities and outputs

The following names align with the eight-engine sequence already described in the Phase 4 feature specification. This document defines their output contracts at a design level; it does not approve unreviewed formulas, thresholds, weights or ranking methods.

### Engine 1 — Market Regime and Trend

**Purpose:** Describe the current NIFTY market regime and its 1/5/22-session context.

**Inputs:** Validated NIFTY spot OHLC and approved spot features for available 1/5/22 contexts.

**Required output:**
- Analysis Date and actual data coverage.
- Market regime classification, when the approved classification method can support it.
- Directional assessment, if supported by evidence.
- 1-session current condition, 5-session context and 22-session context.
- Trend/range/volatility evidence used.
- Conflicting evidence and unavailable inputs.
- Explanation of why the classification was selected.

**Guardrails:** Do not invent regime thresholds or a numeric trend-strength score. If the classification method is not yet approved or evidence conflicts, report indeterminate/unclear rather than forcing a direction.

### Engine 2 — Price Structure and Key Levels

**Purpose:** Identify NIFTY price structure and evidence-backed support/resistance candidates.

**Inputs:** Validated NIFTY spot OHLC history and the approved 1/5/22 spot features.

**Required output:**
- S1, S2, R1 and R2 candidates when the approved method supports them.
- Exact level values and the calculation method for each level.
- Source dates, swing/reaction observations or other supporting evidence used.
- Historical reaction/recurrence evidence and relevant context window.
- Level status, limitations and invalidation conditions.
- Clear explanation where a requested level cannot be calculated.

**Guardrails:** Do not calculate support/resistance as strike plus/minus option premium. Do not fabricate levels to fill all four slots. The exact level-detection method and any strength classification require separate approval.

### Engine 3 — Contract OI and Positioning

**Purpose:** Describe contract-specific OI and volume behaviour without claiming to know the identity or intent of market participants.

**Inputs:** Exact selected-expiry NIFTY CE/PE contract observations, including strike, option type, instrument ID, premium, OI and volume.

**Required output:**
- Contract identity and observation coverage.
- Strike-wise CE and PE OI, volume and premium context.
- Absolute and percentage OI changes where valid.
- Volume and volume/OI context where valid.
- 1/5/22 first/last observations and continuity/missingness.
- Evidence supporting any permitted positioning description.
- Explicit unavailable reasons and conflicting evidence.

**Guardrails:** OI alone does not prove seller/buyer identity, fresh writing, unwinding, long/short buildup or seller dominance. Do not label a participant action as fact based only on OI movement.

### Engine 4 — CE/PE Premium Behaviour and Ranking

**Purpose:** Compare premium behaviour across exact selected-expiry contracts and identify candidates using an approved, explainable method.

**Inputs:** Exact-contract CE/PE premium OHLC, volume, OI and approved premium features.

**Required output:**
- Contract identity for every displayed result.
- Premium movement and range for available 1/5/22 contexts.
- Continuity and valid-observation coverage.
- Candidate comparison/ranking only when its method is approved.
- Ranking explanation and evidence for each candidate.
- Missing inputs, excluded contracts and reasons.

**Guardrails:** Never join premium history across strikes, option types or expiries. Do not introduce arbitrary weights, cutoffs or a ranking score. Do not rank contracts when the available evidence cannot support a fair comparison.

### Engine 5 — Volatility and Pricing Context

**Purpose:** Describe historical spot volatility and option-premium range context.

**Inputs:** Approved NIFTY spot Yang–Zhang volatility features and exact-contract CE/PE True Range/ATR and premium features.

**Required output:**
- Spot realized-volatility context for approved 5/22 windows.
- Exact-contract premium True Range/ATR context for approved 5/22 windows.
- Calculation window, observation count and availability status.
- Explanation of the distinction between spot realized volatility and option-premium range.
- Missingness and calculation limitations.

**Guardrails:** Yang–Zhang is approved for NIFTY spot OHLC only, not option premium and not implied volatility. Do not describe historical realized volatility as option IV. Do not introduce a pricing model or IV estimate without a separately approved source and method.

### Engine 6 — Participant Positioning Context

**Purpose:** Add participant-category context only when permitted, validated and comparable participant data is available.

**Inputs:** A separately approved and validated participant report/source, if one is added to the project scope.

**Required output when data exists:**
- Source identity, report date and data coverage.
- Participant categories and reported values as supplied by the source.
- Comparable date context and changes, where valid.
- Evidence, limitations and source references.

**Required output when data is absent:** Explicitly state that participant positioning is unavailable/not supplied. Do not infer it from option-chain OI.

**Guardrails:** Phase 4's current core input boundary does not authorize acquisition or ingestion of supplementary participant reports. This engine must remain unavailable until the source, permission, validation and integration are separately approved.

### Engine 7 — Seller Pressure and Setup Detection

**Purpose:** Combine evidence from Engines 1–6 to identify potential seller pressure, trap conditions and candidate setups for review.

**Inputs:** Versioned outputs from upstream engines, with their evidence, statuses and limitations.

**Required output:**
- Potential CE-side pressure and PE-side pressure, separately.
- Candidate setup/pattern name and version, if one exists.
- Evidence supporting and contradicting the candidate.
- Relevant spot levels and exact contract references.
- Confirmation conditions and invalidation conditions.
- Missing dependencies and uncertainty.
- Explicit `No Clear Setup` when evidence is insufficient or conflicting.

**Guardrails:** A potential seller-pressure pattern is an analytical hypothesis, not proof of seller identity. Do not force a CE or PE setup. Do not introduce unapproved premium triggers, weights or thresholds.

### Engine 8 — Eight-Scenario Decision and Report

**Purpose:** Assemble the upstream evidence into the project's eight market scenarios and a coherent decision report.

**Inputs:** Outputs from Engines 1–7, plus the separately approved scenario definitions.

**Required output for each of the eight scenarios:**
- Scenario name and definition.
- Market conditions.
- CE/PE seller-pressure interpretation, with caveats.
- Expected market direction or indeterminate state.
- Trigger/confirmation conditions.
- Relevant spot levels and exact strike candidates, when supported.
- Invalidation conditions.
- Supporting and contradicting historical evidence.
- Model assessment, when a validated model is available.
- Missing data and limitations.

**Guardrails:** Do not invent or rename the project's eight canonical scenarios. The exact eight scenario names and definitions must be taken from the owner-approved scenario specification before implementation. Do not force a winning scenario when evidence is insufficient.

## 4. Four ML models — separate model responsibilities

The project has four ML models. They are not replacements for the eight analytical engines.

| Model | Responsibility | Required model output |
|---|---|---|
| 1. Market Regime and Direction Classification | Classify a defined future or current market-regime target using leakage-safe historical inputs | Predicted class/assessment, model version, input coverage, calibrated probability only if calibration is demonstrated, and limitations |
| 2. Seller Behaviour and Pattern Identification | Identify recurring seller-behaviour patterns from validated historical evidence | Pattern label/version, matched evidence, unmatched/conflicting evidence, model version and limitations |
| 3. Breakout/Breakdown Assessment | Assess a precisely defined breakout or breakdown target | Target definition, assessment, supporting features, model version, evaluation status and limitations |
| 4. Scenario Evaluation and Ranking | Evaluate the approved eight scenarios using defined targets and evidence | Scenario assessments/ranking, reasons, model version, calibrated probabilities only if validated, and no-clear-setup state |

Before training or evaluating a model, its target, label-generation method, permitted features, prediction horizon, leakage controls, evaluation metrics and minimum evidence requirements must be specified and approved. Do not invent labels from the same observations that the model is expected to predict.

Use explainable statistical/ML methods first. Add more complex models only when the available historical data supports them.

## 5. Required final user-facing output modules

The daily analysis must be more than a single Bullish/Bearish label. The final report should expose these ten modules:

1. **Market Overview** — trade date, selected expiry, NIFTY close, market structure, trend/volatility assessment, seller-side context and actual data coverage.
2. **Support & Resistance** — S1/S2/R1/R2, calculation method, evidence and limitations.
3. **CE/PE Seller Intelligence** — strike-wise CE/PE evidence, OI/volume/premium behaviour and cautious interpretation.
4. **Breakout/Breakdown** — levels, confirmation conditions, relevant seller-pressure context, candidate strikes and invalidation.
5. **Strike Selection** — ranked candidates only where an approved method supports ranking; exact expiry/strike/type, premium, OI, volume, selection reason and invalidation. Bid-ask spread only if supplied by the permitted source.
6. **Eight Market Scenarios** — all eight approved scenarios with conditions, triggers, evidence and invalidation.
7. **Final Decision Report** — primary view, important levels, preferred setup or `No Clear Setup`, confirmation requirements, alternative scenario and risk/invalidation.
8. **Historical Evidence** — 1/5/22 context, repeated patterns, OI/premium behaviour, level reactions and references to the source observations supporting each claim.
9. **ML Model Assessment** — model outputs, model versions, evaluation status, calibrated probabilities only where validated, and limitations.
10. **PDF/Excel Reports** — Daily Intelligence PDF, Detailed Analysis Excel, CE/PE Strike Analysis Excel, Eight Scenarios PDF, Historical Comparison Excel and Model Evaluation PDF.

Every material conclusion must be traceable to the engine output and its supporting source evidence. If data is missing, the report must show that limitation instead of filling it with an assumption.

## 6. AI explanation and orchestration rules

AI can:
- Summarize outputs from the analytical engines.
- Explain why a result was produced using supplied evidence.
- Compare supporting and contradicting evidence.
- Identify missing dependencies and inconsistencies.
- Route owner feedback to the likely responsible engine or model.
- Propose a candidate improvement for review.

AI must not:
- Create OHLC/OI/volume/premium values or historical observations.
- Invent support/resistance levels, strikes, triggers, thresholds, weights or scenario definitions.
- Claim seller identity or intent from OI alone.
- Generate uncalibrated confidence percentages.
- Hide missing data or conflicting engine outputs.
- silently change an approved engine formula or production model.

The deterministic engine output is the source of numeric truth. The AI explanation layer must cite the engine result and source references it used.

## 7. Manual testing and feedback workflow

The first testing interface can be a generated report or structured output; a complete dashboard is not a prerequisite for owner review.

For each test run, the owner should be able to inspect:
- Analysis Date and selected Expiry.
- Input data coverage and missing observations.
- Each engine's output and calculation/evidence references.
- The final ten output modules.
- Engine/model versions used.
- Warnings, unavailable fields and known limitations.

Feedback must be separated into three types:

| Feedback type | What it evaluates | Example |
|---|---|---|
| Analytical feedback | Correctness of calculations, levels, contract selection and interpretation | A support level is incorrect; an OI change was interpreted too strongly |
| Pattern feedback | Usefulness and completeness of a detected pattern | A recurring CE/PE behaviour was missed or falsely matched |
| Outcome feedback | Whether a defined expected condition actually occurred later | The next eligible EOD session did or did not meet the forecast target |

A simple `Good` or `Bad` response is not enough to establish accuracy. Capture the affected report section, engine/model, exact output/version, owner's correction, reason and supporting evidence. Outcome feedback requires the later actual EOD outcome; it cannot be inferred from analytical approval alone.

## 8. Engine enhancement and controlled learning

When feedback identifies a weakness:

1. Retrieve the exact run, engine/model version, inputs and output that produced it.
2. Classify the issue: source-data problem, feature/calculation problem, engine logic problem, model problem, explanation problem or unavailable evidence.
3. Identify the responsible component; do not change unrelated engines.
4. Create a candidate rule/pattern/model version and document the reason for the change.
5. Compare the candidate with the current approved version using separate chronological observations.
6. Check for look-ahead leakage, overlapping-window dependence and sample imbalance.
7. Report where the candidate improves, worsens or remains inconclusive.
8. Keep the existing approved version until the candidate passes the agreed review.
9. Preserve version history and a rollback path.

Pattern learning and model learning must remain distinct:
- **Pattern learning:** preserve reviewed patterns, identify weak patterns and propose revised pattern definitions.
- **Model learning:** retrain or update an ML model using reviewed labels and suitable historical observations.

Neither process may silently replace an approved production version.

## 9. Historical validation limitations

The 1/5/22 windows are daily analysis contexts. A 22-session sample is not sufficient by itself to establish robust predictive accuracy across market regimes.

The existing 17+4+1 proposal is a leakage-control workflow concept: Sessions 1–17 establish a baseline; Sessions 18–21 are four sequential one-session-ahead checks; Session 22 is forecast using Sessions 1–21 only. Four validation targets are not a statistically reliable performance estimate.

A meaningful model evaluation requires:
- Precisely defined prediction targets and horizons.
- Correct, incorrect and indeterminate outcome definitions.
- Approved metrics and tolerances.
- Multiple chronological evaluation periods beyond a single 22-session sample.
- Separation between training, tuning and evaluation periods.
- No look-ahead leakage or treating overlapping windows as independent samples.
- Reporting sample size, coverage, class distribution and limitations.

Do not publish accuracy claims or confidence percentages until the evaluation design and evidence support them.

## 10. Data storage principle

The objective is correct, testable engine output—not storing every intermediate calculation simply because it exists.

- Historical daily feature calculations may be used as intermediate inputs to construct 1/5/22 context and engine outputs.
- Persisting every historical daily feature observation is not a project objective by itself.
- Any persisted run result should be justified by a concrete need such as reproducibility, audit, owner feedback comparison, version tracking or report retrieval.
- The exact persistence boundary should be decided from the approved engine-output and testing workflow before database implementation.
- Preserve source data and provenance required to reproduce and investigate a result.
- This document does not approve a new schema, migration or change to the existing Phase 4 physical database/API design.

## 11. Approval gates before implementation

The following must be reviewed before engine/model code is started:

1. Approve the responsibility and output contract of each of the eight engines.
2. Confirm the canonical names and definitions of all eight scenarios from the owner-approved scenario specification.
3. Approve the exact formula/method, thresholds and ranking logic for any engine output that needs them; no values are assumed by this draft.
4. Define target, labels, horizon, features and evaluation criteria for each of the four ML models.
5. Confirm what historical archive is available for training and chronological evaluation.
6. Confirm the allowed participant-data source and licensing/permission before enabling Engine 6.
7. Approve the minimal persistence needed for reproducible runs, outputs, feedback and version history.
8. Review API security and access control before exposing processing or report endpoints.
9. Implement one engine at a time with unit tests and owner-reviewable outputs.
10. Do not merge to `main`, deploy or change production without explicit approval.

## 12. Current status

- Phase 4 formulas and feature definitions: documented and owner-approved as recorded in the Phase 4 specification.
- Phase 4 physical database/API designs: documented, not implemented.
- Eight analytical engines: design responsibilities and output expectations drafted here; formulas and implementation remain pending.
- Eight scenario definitions: must be confirmed against the canonical owner-approved specification.
- Four ML models: responsibilities identified; targets, labels, training and evaluation design remain pending.
- Manual owner testing and controlled feedback loop: workflow drafted here; implementation remains pending.
- Application code, database schema, migrations, data and deployment: unchanged by this document.
