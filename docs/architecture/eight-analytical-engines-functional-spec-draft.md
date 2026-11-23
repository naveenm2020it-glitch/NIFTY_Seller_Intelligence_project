# Eight Analytical Engines — Functional and Output Requirements (Revised Draft)

**Status:** Draft for project-owner review; not approved for implementation  
**Project:** NIFTY Seller Intelligence  
**Scope:** NIFTY 50 and NIFTY CE/PE options; historical end-of-day (EOD) analysis only  
**Inputs:** Analysis Date and user-selected Expiry  
**Depends on:** Phase 0–3 foundation and the Phase 3 EOD data contract

> **Approval boundary:** This document defines the proposed eight-engine responsibilities and the outputs the application is expected to provide. Engine names, formulas, thresholds, ranking methods and scenario rules remain subject to project-owner approval and historical validation. This document does not finalize the EOD report inventory or authorize additional report acquisition.

---

## 1. Purpose and operating boundaries

The application will analyse the selected Analysis Date and Expiry using validated historical EOD data. It will combine NIFTY 50 market structure, NIFTY CE/PE contract data, OI, volume, premium behaviour and available volatility/participant context to evaluate eight directional scenarios.

The intended user-facing result is not only a market-direction label. For every scenario, the application must show:
- The relevant NIFTY spot level and its S1/S2/R1/R2 identity.
- The CE strikes and premiums expected to rise or fall.
- The PE strikes and premiums expected to rise or fall.
- Independent Rank 1, Rank 2 and Rank 3 contracts for both CE and PE sides.
- The reference EOD premium and the approved adaptive premium trigger conditions.
- The scenario's evidence, status, risks and invalidation conditions.
- A BUY CE, BUY PE or WAIT outcome where the approved conditions support one.

### 1.1 Scope exclusions

The application will not:
- Provide live or intraday market monitoring or confirmation.
- Connect to brokers, place orders or execute trades.
- Claim that EOD OHLC proves the intraday sequence, exact time of a breakout/rejection or exact seller intent.
- Treat aggregate participant reports as strike-specific NIFTY positioning.
- Silently substitute another expiry for the user's selected Expiry.
- Invent missing values, seller-writing premiums, report data, triggers, levels or rankings.
- Change approved analytical rules or models without validation, versioning and controlled approval.
- Introduce a cutoff-time input.

**The only user inputs remain Analysis Date and Expiry.**

### 1.2 EOD interpretation

The application produces an EOD analysis and a next-session scenario plan. Premium direction is an evidence-based expectation, not a guarantee. Since the application is EOD-only, it cannot monitor whether spot, CE and PE conditions occur sequentially during the next session. It may evaluate the next session retrospectively after permitted EOD data for that session is available.

---

## 2. Proposed eight-engine overview

| No. | Proposed engine | Responsibility | Main output |
|---:|---|---|---|
| 1 | Market Regime and Trend Engine | Describe NIFTY 50 market condition and 1/5/22-session context | Regime, trend, measurements and conflicts |
| 2 | Price Structure and Key Levels Engine | Identify NIFTY spot S1/S2/R1/R2 levels and price-structure events | Spot levels, evidence, breakout/breakdown/recovery/rejection status |
| 3 | Contract OI and Positioning Engine | Analyse contract-level OI, OI changes and volume | Strike-wise positioning observations and evidence limits |
| 4 | CE/PE Premium Behaviour and Ranking Engine | Analyse both option sides and rank contracts independently for every scenario | CE/PE Rank 1–3 strikes, reference premiums and adaptive triggers |
| 5 | Volatility and Pricing Context Engine | Provide realized-volatility and approved option-pricing context | Volatility measures and assumption-labelled estimates |
| 6 | Participant Positioning Context Engine | Add broad participant-category context when verified data is available | Aggregate positioning/activity context and limitations |
| 7 | Seller Trap and Setup Detection Engine | Combine market, positioning, premium and volatility evidence | Explainable setup candidates, risk and invalidation |
| 8 | Eight-Scenario Decision and Consolidated Report Engine | Evaluate all eight scenarios and assemble the final report | Eight scenario results and consolidated BUY CE/BUY PE/WAIT outcome |

These engine names and boundaries are proposed. They must be reviewed before implementation. The four feedback-learning components in Section 8 are separate from these eight market-analysis engines.

---

## 3. Functional requirements by engine

### Engine 1 — Market Regime and Trend

**Purpose:** Describe the selected EOD condition of NIFTY 50 and provide context for the other engines.

**What it will do**
- Read validated NIFTY 50 daily OHLC history.
- Produce 1-, 5- and 22-session comparisons where sufficient history exists.
- Describe trend direction, persistence, range-bound behaviour and changes in price range/realized volatility.
- Identify agreement or conflict between short- and longer-session views.
- Return neutral/uncertain when the evidence is mixed or insufficient.

**Inputs**
- NIFTY 50 EOD OHLC.
- Validated market-session calendar and prior sessions.
- Approved, versioned feature definitions.

**Outputs**
- Market regime and trend description.
- 1/5/22-session measurements and supporting dates.
- Directional context and conflicting evidence.
- Data sufficiency flags, explanation and provenance.

**Boundaries:** This engine does not decide BUY CE or BUY PE. EOD data does not establish the intraday path.

### Engine 2 — Price Structure and Key Levels

**Purpose:** Identify NIFTY spot support/resistance references and evaluate the selected EOD observations against them.

**What it will do**
- Identify S1 and S2 support references and R1 and R2 resistance references from NIFTY 50 historical price structure using a methodology that must be approved.
- Use historical OHLC observations, prior highs/lows, repeated reaction areas and range structure where supported by the approved method.
- Assess whether the selected EOD observations indicate approach, test, breakout, breakdown, recovery, rejection, hold or failure.
- Provide the dates and observations supporting each level.
- Pass the spot-level state to the scenario engine.

**Outputs**
- S1, S2, R1 and R2 spot price levels, or explicitly unavailable.
- Level type, source observations, supporting dates and method/version.
- Current spot close and distance from each relevant level.
- EOD interaction/status, evidence strength and invalidation/reassessment conditions.

**Important separation**
- S1/S2/R1/R2 are NIFTY spot reference levels.
- Option strike prices are selected separately by Engine 4 for each scenario.
- Do **not** calculate a resistance/support level by adding an option premium to a CE strike or subtracting a premium from a PE strike.
- Do **not** present an option strike as the NIFTY spot resistance/support level.
- The exact spot-level formula, lookback, clustering, evidence and strength criteria remain unapproved and must be historically validated. Do not hardcode arbitrary point distances or levels.

**Boundaries:** A daily high/low touch does not prove an intraday rejection. The engine must not invent precision or report a weak level as certain.

### Engine 3 — Contract OI and Positioning

**Purpose:** Analyse NIFTY CE/PE contract-level OI and trading activity to identify positioning changes relevant to the scenarios.

**What it will do**
- Analyse strikes for the user's selected expiry.
- Compare OI with prior EOD sessions and calculate OI changes using an approved definition.
- Compare OI changes with option premium, underlying movement and volume.
- Identify strike-wise concentrations and changes across CE and PE.
- Produce carefully labelled interpretations such as possible long build-up, short build-up, short covering or long unwinding only where evidence supports them.
- Keep observed facts separate from inferred positioning.

**Inputs**
- NIFTY CE/PE EOD OHLC, volume and OI.
- Instrument ID, expiry, strike and option type.
- NIFTY 50 close and historical sessions.
- MII contract metadata and provenance.

**Outputs**
- Strike-wise OI, OI change, volume and premium observations.
- CE/PE positioning comparison.
- Potential positioning interpretations, evidence and caveats.
- Contract continuity, expiry and data-quality flags.

**Boundaries**
- OI alone does not identify whether a buyer or seller initiated a position.
- OI plus price/volume behaviour supports an interpretation; it does not prove the identity or intent of a writer.
- A sell-side execution is not automatically a fresh short-opening trade.
- Do not label a premium as an actual seller-writing premium unless the source data can verify that the trade opened a short position.
- Participant-wise OI is aggregate context, not strike-specific attribution.
- Do not mix expiries without explicitly labelling the aggregation.

### Engine 4 — CE/PE Premium Behaviour and Ranking

**Purpose:** Identify how CE and PE premiums behave and independently rank the most suitable candidate strikes for both sides of every scenario.

**What it will do**
- Analyse EOD CE and PE premiums for the selected expiry.
- Compare premium movement with NIFTY spot movement, strike/moneyness, OI, volume and time-to-expiry context.
- Use 1/5/22-session premium behaviour where sufficient contract history exists.
- Identify premium expansion, contraction, relative strength/weakness and unusual changes using approved definitions.
- For **each of the eight scenarios**, independently rank CE contracts and PE contracts.
- Return Rank 1, Rank 2 and Rank 3 for each side only when eligible contracts satisfy the approved ranking criteria.
- Identify the side expected to rise and the opposite side expected to fall for that scenario.
- Calculate the agreed adaptive primary upper premium trigger and opposite lower premium trigger after the formulas are approved.
- Explain why each contract ranked where it did and why alternatives ranked lower.

**Required ranking output for every scenario**

| Field | Required content |
|---|---|
| Scenario | Exact scenario name |
| Option side | CE or PE |
| Expected premium behaviour | Expected to rise or expected to fall |
| Rank | Rank 1, Rank 2 or Rank 3 |
| Strike | Exact option strike |
| Expiry | User-selected expiry |
| Moneyness | ITM, ATM or OTM under the approved classification |
| Reference premium | Actual EOD premium from the selected Analysis Date |
| OI and volume | Available EOD contract observations |
| Ranking explanation | Evidence and reason for the rank |
| Premium trigger | Adaptive upper/lower trigger, if calculable under approved rules |
| Eligibility | Eligible, insufficient evidence or unavailable |

The CE ranking and PE ranking are separate rankings. They are also scenario-specific: a strike ranked first for one scenario must not automatically be reused as Rank 1 for another scenario without evaluating it again.

If fewer than three contracts qualify, show only the qualifying ranks and explain why the remaining ranks are unavailable. Do not force a Rank 1, Rank 2 or Rank 3 when the evidence is insufficient.

**Contract-selection boundaries**
- The user-selected expiry must be preserved; no silent expiry substitution.
- No fixed strike offset, fixed premium band or arbitrary OI/volume threshold is approved.
- Ranking may consider moneyness, premium behaviour, volume, OI, data continuity and expiry context only through an approved, validated method.
- Current core EOD data does not establish bid/ask spread or executable fill quality. Do not claim it does.

### Engine 5 — Volatility and Pricing Context

**Purpose:** Provide volatility and option-pricing context needed to interpret premium behaviour.

**What it will do**
- Calculate realized-volatility features from NIFTY 50 EOD history using an approved methodology.
- Compare current volatility context with historical observations.
- Optionally use FOVOLT only after its current schema and meaning are verified; treat it as an underlying/futures volatility reference, not NIFTY option IV.
- Calculate model-derived IV/Greeks only if the project separately approves the model and all required assumptions and inputs.
- Label all model estimates and preserve the assumptions/version used.

**Outputs**
- Realized-volatility measurements and methodology.
- Optional FOVOLT context with provenance.
- Approved model-derived IV/Greeks, if enabled, with assumptions.
- Quality flags and unavailable reasons.

**Boundaries:** Do not represent model-derived IV as an exchange-published value. Do not publish IV/Greeks when required inputs or assumptions are missing. The old 2013 IV-file reference is not a verified current source.

### Engine 6 — Participant Positioning Context

**Purpose:** Add broad participant-category context when a current, permitted and validated report is available.

**What it will do**
- Parse participant-wise OI by documented participant and instrument categories if approved.
- Compare category-level index-option/index-futures positioning across report dates.
- Optionally analyse participant-wise trading volume as activity context.
- Keep aggregate participant data separate from NIFTY strike-level contract data.
- Mark optional report status as available, pending, unavailable or invalid.

**Outputs**
- Participant-category OI/activity observations.
- Report validation and availability status.
- Broad market context with instrument-scope warnings and provenance.

**Boundaries**
- Participant-wise reports do not identify the writer of a particular NIFTY strike.
- Participant volume is activity, not a closing position and not proof of net writing.
- Missing optional reports are unavailable/pending, never zero.
- This engine is optional to the core analysis and must not block the report if supplementary data is absent.

### Engine 7 — Seller Trap and Setup Detection

**Purpose:** Combine the outputs of Engines 1–6 to identify possible seller traps and explainable option-buyer setups.

**What it will do**
- Combine market regime, spot structure, contract OI/volume, CE/PE premium behaviour and volatility context.
- Identify supporting and conflicting evidence.
- Detect candidate CE-side or PE-side seller-trap situations where available evidence supports the interpretation.
- Explain why a seller-side position may be vulnerable without claiming knowledge of a specific seller's identity or intent.
- Produce setup candidates, trigger conditions, invalidation conditions and reasons to avoid a setup.
- Permit no-setup/WAIT when evidence is inadequate.

**Outputs**
- Setup direction: CE, PE or none.
- Seller-trap candidate and explanation.
- Relevant spot level and scenario.
- Selected CE and PE candidate contracts/ranks from Engine 4.
- Supporting and conflicting evidence.
- Trigger, invalidation, risk and evidence-sufficiency details.
- Source and upstream engine versions.

**Boundaries:** EOD data cannot prove the intraday sequence or exact moment of a seller trap. High OI or one premium move alone is not proof. No guaranteed-profit or automatic-order claim.

### Engine 8 — Eight-Scenario Decision and Consolidated Report

**Purpose:** Evaluate all eight scenarios using validated upstream outputs and produce the final user-facing report.

**What it will do**
- Evaluate every scenario independently.
- Consume outputs from Engines 1–7 rather than independently re-parsing raw source reports.
- Record scenario conditions as met, not met, conflicting, unknown or invalidated.
- Include scenario-specific CE and PE Rank 1–3 results from Engine 4.
- Identify which option side is expected to rise and which opposite side is expected to fall.
- Apply the approved sequential confirmation model.
- Produce BUY CE, BUY PE or WAIT only according to approved conditions.
- Explain why a scenario qualifies or does not qualify and preserve alternative scenario evidence.

**Outputs**
- All eight scenario results.
- Scenario-specific CE and PE ranked contract tables.
- Expected premium direction for both sides.
- Reference premiums and adaptive triggers, where calculable.
- Spot-level condition and sequential confirmation stage.
- Selected setup, entry reference, stop-loss, targets and invalidation only where approved methods and sufficient evidence exist.
- Final BUY CE, BUY PE or WAIT result with evidence and limitations.
- Run ID, source provenance and rule/model versions.

---

## 4. The eight required scenarios and paired premium behaviour

The system must evaluate these eight scenarios separately. The expected premium direction is the directional hypothesis to be tested against historical evidence; it is not a guaranteed outcome.

| No. | Scenario | Spot event | Option premium expected to rise | Opposite premium expected to fall | Direction if fully qualified |
|---:|---|---|---|---|---|
| 1 | S1 Breakdown | Break below S1 | PE | CE | BUY PE |
| 2 | S2 Breakdown | Break below S2 | PE | CE | BUY PE |
| 3 | S1 Recovery | Recover S1 | CE | PE | BUY CE |
| 4 | S2 Recovery | Recover S2 | CE | PE | BUY CE |
| 5 | R1 Breakout | Break above R1 | CE | PE | BUY CE |
| 6 | R2 Breakout | Break above R2 | CE | PE | BUY CE |
| 7 | R1 Rejection | Reject/fail at R1 | PE | CE | BUY PE |
| 8 | R2 Rejection | Reject/fail at R2 | PE | CE | BUY PE |

**WAIT is an outcome, not a ninth scenario.** WAIT applies when no scenario qualifies, evidence conflicts, required conditions are incomplete, the data are insufficient or an invalidation condition is met.

For each scenario, Engine 4 must independently provide:
- CE Rank 1–3, with strike and EOD reference premium.
- PE Rank 1–3, with strike and EOD reference premium.
- Expected direction for each side, as specified in the table.
- Ranking explanation and available OI/volume/premium evidence.
- Adaptive premium triggers and their status when the approved method can calculate them.
- Explicit unavailable status when the data do not support a rank or trigger.

A scenario's primary option is the side expected to rise. The opposite option is the side expected to fall. Both sides must be shown; the system must not show only the recommended BUY side.

---

## 5. Premium confirmation and sequence

The previously agreed trigger mode is **both_adaptive**: the primary upper premium trigger and the opposite lower premium trigger are both adaptive. The previously agreed confirmation timing is **sequential**.

### 5.1 BUY CE confirmation

1. NIFTY satisfies the applicable upward spot condition (recovery or breakout).
2. The selected CE premium crosses its adaptive upper trigger.
3. The selected opposite PE premium falls below its adaptive lower trigger.
4. The setup is qualified only when all required scenario conditions and invalidation checks are satisfied.

### 5.2 BUY PE confirmation

1. NIFTY satisfies the applicable downward spot condition (breakdown or rejection).
2. The selected PE premium crosses its adaptive upper trigger.
3. The selected opposite CE premium falls below its adaptive lower trigger.
4. The setup is qualified only when all required scenario conditions and invalidation checks are satisfied.

### 5.3 Status values

Each stage must be represented as met, not met, unknown or invalidated. The overall result may be pending/partially confirmed, qualified, invalidated or WAIT, according to approved rules.

**EOD limitation:** The sequence describes the required next-session confirmation plan. This EOD-only application does not observe or confirm live intraday execution of those stages. Retrospective outcome evaluation requires later permitted EOD data.

### 5.4 Trigger formulas not yet approved

The following are not yet defined and must not be invented:
- Adaptive primary upper premium trigger formula.
- Adaptive opposite lower premium trigger formula.
- Lookback weighting and minimum sample requirements.
- Trigger persistence, tolerance and invalidation rules.
- How volatility, OI, volume, moneyness and time-to-expiry contribute to the trigger.

---

## 6. Required scenario output layout

For each scenario, show a paired table similar to the following structure. Values below are field labels only; this is not a market example and contains no assumed prices.

### Example layout — R1 Breakout

**Scenario:** R1 Breakout  
**Spot condition:** NIFTY breakout status and R1 spot reference  
**Expected direction:** BUY CE, only if all approved conditions qualify

| Rank | CE strike | CE EOD premium | CE expected behaviour | PE strike | PE EOD premium | PE expected behaviour |
|---:|---:|---:|---|---:|---:|---|
| 1 | Selected CE strike | Actual EOD premium | Rise | Selected PE strike | Actual EOD premium | Fall |
| 2 | Alternative CE strike | Actual EOD premium | Rise | Alternative PE strike | Actual EOD premium | Fall |
| 3 | Alternative CE strike | Actual EOD premium | Rise | Alternative PE strike | Actual EOD premium | Fall |

The CE and PE ranks are calculated independently. Rank 1 CE does not have to share the same strike as Rank 1 PE. Each row is a compact display pairing of two independent ranked lists, not a claim that the strikes are matched or equivalent.

**Additional details for the scenario**
- Moneyness and expiry for every ranked contract.
- Reference EOD premium for every ranked contract.
- OI, OI change and volume evidence.
- Why each contract received its rank.
- Adaptive CE upper trigger and PE lower trigger, if calculable.
- Sequential spot/CE/PE condition status.
- Selected candidate, entry reference, stop-loss, targets and invalidation if supported by approved methods.
- Evidence, conflicts, data gaps and reason for BUY CE or WAIT.

The same output layout is required for all eight scenarios, with CE/PE expected direction reversed according to Section 4.

---

## 7. Consolidated report — outputs the user can receive

For the selected Analysis Date and Expiry, the final report should contain the following sections.

1. **Market overview**
   - NIFTY 50 EOD close.
   - Market regime and trend.
   - 1/5/22-session analysis.
   - Conflicting evidence and data sufficiency.

2. **Spot support/resistance**
   - S1, S2, R1 and R2.
   - Historical observations and dates supporting each level.
   - Level status, evidence strength and invalidation.
   - Spot breakout, breakdown, recovery or rejection status.

3. **Seller/contract positioning**
   - Important CE/PE strikes.
   - OI, OI change and volume.
   - Premium and underlying price context.
   - Potential positioning interpretation with evidence limits.
   - No unsupported claim of actual fresh writing or seller identity.

4. **Eight scenario analyses**
   - All eight scenario statuses.
   - For every scenario, CE Rank 1–3 and PE Rank 1–3 independently.
   - Strike, expiry, moneyness and EOD reference premium.
   - Which side is expected to rise and which side is expected to fall.
   - Ranking explanation, adaptive triggers and confirmation status.

5. **Premium confirmation**
   - Primary upper and opposite lower adaptive triggers.
   - Trigger methodology/version when approved.
   - Sequential stage status and invalidation.

6. **Final decision**
   - BUY CE, BUY PE or WAIT.
   - Leading qualified scenario, if any.
   - Selected contract and ranked alternatives.
   - Reasons other scenarios did not qualify.

7. **Trade-planning references**
   - EOD entry reference.
   - Stop-loss reference.
   - Target reference(s).
   - Invalidation and reasons to avoid.
   - These values must remain unavailable if no approved method or sufficient evidence exists; they are not live executable prices.

8. **Evidence and provenance**
   - Source report availability and validation status.
   - Analysis Run ID and source hashes.
   - Engine, rule and model versions.
   - Historical sessions used.
   - Missing data, limitations and confidence method.

The report must distinguish observed EOD values, calculated spot levels, model-derived estimates and inferred interpretations.

---

## 8. Separate feedback-learning architecture

The following four components are part of the project's learning approach. They are **separate from the eight market-analysis engines**.

1. **Pattern Discovery Engine**
   - Discovers recurring patterns from historical 1/5/22-session analysis and the retained historical archive.
   - Produces candidate patterns with supporting observations.

2. **Pattern Knowledge Base**
   - Stores approved patterns, evidence, confidence/method details and version history.
   - Preserves prior approved versions and their rationale.

3. **Feedback Intelligence Engine**
   - Processes analytical, pattern and outcome feedback.
   - Identifies which analytical component or pattern needs review.
   - Links feedback to the exact analysis and rule/model versions.

4. **Pattern Optimization Engine**
   - Proposes candidate pattern or model improvements.
   - Validates candidates against separate historical observations.
   - Presents evidence for review; it does not silently replace approved logic.

Learning must be controlled, explainable, historically validated, versioned and rollback-capable. Positive feedback alone is not proof of correctness, and negative feedback alone is not proof that a rule is wrong. Overlapping 22-session windows must not be counted as independent validation observations.

---

## 9. Data and report dependency position — not finalized

The three Phase 3 core reports remain the established ingestion foundation:
1. NSE F&O UDiFF Common Bhavcopy Final.
2. NSE F&O MII Contract File.
3. NSE Indices All Indices daily-close CSV.

This document does **not** decide which additional reports must be acquired. The report inventory will be reviewed only after the engine responsibilities and required outputs are reviewed and approved.

Current dependency principles:
- Core analysis should operate from the validated Phase 3 data contract.
- Supplementary reports are optional until their current sample, schema, units, row grain, publication behaviour, permitted acquisition and distinct analytical value are verified.
- Participant-wise OI is broad participant-category context, not NIFTY-strike attribution.
- Participant-wise volume is activity, not closing position or proof of writing.
- FOVOLT is an underlying/futures volatility reference, not option IV.
- Missing optional reports remain unavailable/pending, never zero.
- No automated NSE collection, new subscription or supplementary report ingestion is authorized by this draft.

After approval of the engine/output requirements, the project owner and development team will review the report dependency matrix and decide which reports are actually needed.

---

## 10. Decisions still requiring approval

The following remain open and must not be silently assumed:

1. Approve, rename, combine or split the eight proposed engines.
2. Approve the exact S1/S2/R1/R2 spot-level methodology, lookback, clustering and evidence-strength criteria.
3. Approve the ITM/ATM/OTM classification boundaries.
4. Approve the independent CE and PE ranking method for each scenario, including scoring inputs, weights, tie-breaking and minimum eligibility.
5. Approve how many ranked alternatives to show when fewer than three qualify; default display requirement is up to three, with no forced ranks.
6. Approve the adaptive primary upper premium trigger formula.
7. Approve the adaptive opposite lower premium trigger formula.
8. Approve sequential confirmation persistence, tolerance and invalidation rules.
9. Approve the EOD evidence definitions for breakdown, recovery, breakout and rejection.
10. Approve entry-reference, stop-loss and target calculation methods.
11. Approve confidence/evidence scoring and historical validation requirements.
12. Approve the final report layout and whether any outputs should be omitted or added.

All numeric methods and thresholds must be tested on historical data with separate training and validation observations. The 1/5/22-session views are analysis windows, not independent validation samples. Retain the larger archive for validation across market regimes.

---

## 11. Source basis and evidence boundaries

This draft uses:
- Uploaded **Development Approach Review.txt** for 1/5/22-session analysis, seller-pattern discovery, potential seller traps, adaptive CE/PE premium triggers, eight scenarios and the four separate feedback-learning components.
- Repository **docs/data/analytical-engine-report-dependency-matrix.md** for the Phase 3 core reports, capability-level dependencies and supplementary-report limitations.
- Repository **docs/data/eod-report-inventory-review.md** for the EOD report inventory research and supplementary-report caveats.
- Repository **docs/development/phase-3-data-contract.md** for the normalized NIFTY 50 and NIFTY CE/PE EOD data contract.
- The project decisions recorded during requirements review: both premium triggers adaptive, sequential confirmation, user-selected expiry preserved, and eight independent scenario mappings.

The source materials do not provide approved formulas, ranking weights, numeric thresholds, final S/R methodology, final engine names or final report dependencies. Those remain open decisions. No application code, schema, migrations, data, report ingestion, deployment or production configuration is changed by this document.
