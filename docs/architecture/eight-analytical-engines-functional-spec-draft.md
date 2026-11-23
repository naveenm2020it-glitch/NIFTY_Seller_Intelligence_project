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

### Engine 2 — Seller-Based Support, Resistance and Spot Pressure Levels

**Purpose:** Identify NIFTY spot support/resistance levels from likely option-seller positioning, then calculate the spot pressure/breakout level at which that positioning may become vulnerable.

**What it will do**
- Analyse selected-expiry NIFTY CE/PE strike-wise OI, OI changes, volume, premium behaviour and available historical context.
- Identify likely CE-side seller concentration as candidate resistance (R1/R2) and likely PE-side seller concentration as candidate support (S1/S2), while clearly labelling these as inferred positioning rather than verified seller identity.
- Rank candidate levels using an approved, versioned method; show the evidence behind each level rather than relying on OI alone.
- Use NIFTY spot OHLC history to assess whether a seller-derived level is relevant to current market structure and whether the level is approaching, being tested, holding, breaking, recovering or rejecting.
- Calculate a distinct spot pressure/breakout threshold where the candidate seller positioning may become vulnerable. This threshold is not automatically equal to the option strike.
- Keep the seller-positioning strike, NIFTY spot support/resistance level and option premium panic-exit trigger as three separately labelled values.
- Pass the level, evidence and pressure state to Engines 7 and 8.

**Inputs**
- NIFTY 50 historical EOD OHLC.
- Selected-expiry NIFTY CE/PE EOD OHLC, OI, volume and contract identity.
- Historical 1/5/22-session context and approved derived observations.

**Outputs**
- Seller-derived S1/S2 support and R1/R2 resistance spot levels, or explicitly unavailable.
- Relevant CE/PE seller-positioning candidate strikes, separately identified from spot levels.
- Spot pressure/breakout/breakdown threshold and the methodology/version used.
- Supporting OI, OI change, volume, premium and price-structure evidence.
- Current NIFTY close, distance to each level, EOD interaction/status and invalidation/reassessment conditions.
- Evidence strength, data sufficiency and explicit inference limitations.

**Important separation**
- CE seller concentration is a resistance candidate; PE seller concentration is a support candidate. Neither is proof of a particular seller's position.
- A seller-positioning strike, NIFTY spot S/R level and CE/PE premium trigger are not interchangeable.
- Do **not** calculate NIFTY support/resistance as strike plus CE premium or strike minus PE premium.
- Do **not** automatically equate the seller strike with the NIFTY spot level; any relationship must be established by the approved calculation and evidence.
- The exact ranking, level and pressure-threshold formulas, lookbacks, evidence requirements and minimum sample sizes remain unapproved and must be historically validated. Do not invent fixed offsets or arbitrary thresholds.

**Boundaries:** Daily OHLC cannot prove the intraday order of events or an intraday rejection. OI/volume/premium patterns support an estimate of likely seller positioning; they do not prove seller identity or intent.

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
- Calculate the adaptive primary upper premium panic-exit trigger for the option side expected to rise and the adaptive opposite lower premium trigger for the side expected to fall, after the formulas are approved.
- Treat these as estimated levels at which inferred seller positioning may come under pressure; do not describe them as verified seller liquidation.
- Derive thresholds from comparable historical seller-positioning and price/premium behaviour, not by copying the prior EOD close or applying an arbitrary fixed percentage.
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

### Engine 7 — Seller Pressure, Panic-Exit Trigger and Setup Detection

**Purpose:** Combine upstream outputs to estimate when likely option-seller positioning may come under pressure and calculate paired premium trigger levels for a possible option-buyer setup.

**What it will do**
- Combine market regime, seller-derived spot levels, contract OI/volume, CE/PE premium behaviour and volatility context.
- Identify likely seller-pressure candidates and explain the evidence and uncertainty.
- Calculate an adaptive upper premium trigger for the option side expected to rise and an adaptive lower premium trigger for the opposite side expected to fall, using an approved historical method.
- Keep the spot breakout/breakdown threshold separate from both option premium thresholds.
- Apply the agreed Option 2 rule: the spot condition plus the primary option premium trigger are the two required conditions for the initial directional signal; the opposite option premium trigger is additional confirmation.
- Record whether the primary conditions are met, whether opposite-side confirmation is present, and whether evidence conflicts or invalidation applies.
- Estimate historical confidence only through a defined and separately validated method. Do not turn an unvalidated score into a probability claim.
- Permit no-setup/WAIT when evidence is inadequate.

**Outputs**
- Seller-pressure candidate and explanation.
- Relevant NIFTY spot S/R level and separate spot pressure/breakout threshold.
- Selected primary option contract, strike, expiry, EOD reference premium and adaptive panic-exit trigger.
- Selected opposite-side contract, strike, expiry, EOD reference premium and adaptive confirmation trigger.
- Expected primary premium rise and opposite premium fall.
- Primary trigger status, additional confirmation status, invalidation and WAIT reasons.
- Historical confidence estimate, validation sample count/period, success definition, method/version and evidence quality where validated.
- Supporting/conflicting evidence, data gaps and upstream source/model versions.

**Boundaries:** A premium trigger is an estimated seller-pressure/panic-exit threshold, not proof of actual seller liquidation. EOD data cannot observe a live intraday trigger. No guaranteed-profit, guaranteed seller-panic or automatic-order claim.

### Engine 8 — Eight-Scenario Decision and Consolidated Report

**Purpose:** Evaluate all eight scenarios using validated upstream outputs and produce the final user-facing report.

**What it will do**
- Evaluate every scenario independently.
- Consume outputs from Engines 1–7 rather than independently re-parsing raw source reports.
- Record scenario conditions as met, not met, conflicting, unknown or invalidated.
- Include scenario-specific CE and PE Rank 1–3 results from Engine 4.
- Identify which option side is expected to rise and which opposite side is expected to fall.
- Apply the approved sequential Option 2 model: spot condition plus primary premium trigger are required for the initial signal; opposite-side premium trigger is additional confirmation.
- Produce BUY CE, BUY PE or WAIT only according to approved conditions and invalidation/evidence rules.
- Explain why a scenario qualifies or does not qualify and preserve alternative scenario evidence.

**Outputs**
- All eight scenario results.
- Scenario-specific CE and PE ranked contract tables.
- Expected premium direction for both sides.
- Reference premiums and adaptive triggers, where calculable.
- Spot-level condition and sequential primary/additional-confirmation stage.
- Historical confidence/success estimate with numerator, denominator, comparable sample count, validation period and method/version; show unavailable if not validated.
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
- Adaptive primary upper panic-exit and opposite lower confirmation triggers, with their separate status.
- Explicit unavailable status when the data do not support a rank or trigger.

A scenario's primary option is the side expected to rise. The opposite option is the side expected to fall. Both sides must be shown; the system must not show only the recommended BUY side.

---

## 5. Premium panic-exit triggers, Option 2 confirmation and confidence

The agreed trigger mode is **both_adaptive**: both the primary upper premium trigger and the opposite lower premium trigger are adaptive. The agreed confirmation timing is **sequential**. The user-approved decision rule is **Option 2**: two primary conditions can generate the initial directional signal; the opposite-side premium condition is additional confirmation, not a mandatory prerequisite for the initial signal.

### 5.1 BUY CE — Option 2

1. NIFTY crosses the applicable seller-derived upward spot pressure/breakout threshold.
2. The selected CE premium crosses its adaptive upper panic-exit trigger.
3. When both primary conditions are met and no invalidation rule applies, the system may issue the initial **BUY CE** signal.
4. The selected opposite PE premium falling below its adaptive lower trigger is additional confirmation. If it occurs, increase the confirmation/evidence status; do not delay the initial signal solely because this third condition has not yet occurred.
5. If the primary spot or CE premium condition is absent, conflicting or invalidated, remain WAIT or show the appropriate pending status.

### 5.2 BUY PE — reverse Option 2

1. NIFTY crosses the applicable seller-derived downward spot pressure/breakdown threshold.
2. The selected PE premium crosses its adaptive upper panic-exit trigger.
3. When both primary conditions are met and no invalidation rule applies, the system may issue the initial **BUY PE** signal.
4. The selected opposite CE premium falling below its adaptive lower trigger is additional confirmation. If it occurs, increase the confirmation/evidence status; it is not mandatory for the initial signal.
5. If the primary spot or PE premium condition is absent, conflicting or invalidated, remain WAIT or show the appropriate pending status.

### 5.3 Example — illustrative values only

For a seller-derived NIFTY resistance/pressure threshold of 25,100:
- NIFTY spot crosses above 25,100.
- Selected 25,000 CE crosses its adaptive upper premium trigger of ₹155.
- These two conditions meet the primary BUY CE rule.
- Selected 25,150 PE falling below ₹100 is additional confirmation.

The values 25,100, ₹155 and ₹100 are only an illustration of the requested output shape. They are not approved constants, formula outputs or fixed project thresholds.

### 5.4 Stage and decision statuses

Each condition must be represented as met, not met, unknown or invalidated. The report must distinguish:
- **WAIT / primary conditions incomplete:** one or both primary conditions are not met or cannot be evaluated.
- **Primary signal:** spot condition and primary option premium trigger are met, subject to invalidation and evidence-quality rules.
- **Additional confirmation present:** opposite-side premium trigger is also met.
- **Invalidated:** an approved invalidation condition is met.
- **Unavailable:** required data or validated calculation is missing.

The opposite premium confirmation can strengthen the evidence status, but it must not be described as proof that sellers actually liquidated.

### 5.5 Confidence score and 60% reporting requirement

The system may report a historical confidence/success estimate for a seller-pressure level and its premium trigger only when the estimate is supported by a defined historical validation procedure.

- The user's requested reference point is **60% historical confidence**. The application must not automatically assign 60% to a new signal.
- A displayed 60% means that the exact, pre-defined historical success condition was met in 60% of eligible, comparable validation observations. It is a measured historical rate, not a guarantee, certainty about an individual seller, or a promise of future results.
- Define the success event before calculating the rate. It must specify the relevant spot condition, selected option premium trigger, opposite-side confirmation outcome (reported separately), observation horizon and invalidation/failure criteria.
- Show the numerator, denominator, validation date range, comparable-sample count, methodology/version and evidence quality beside the percentage.
- Keep model fitting/development observations separate from chronological validation observations. Avoid look-ahead leakage and do not count overlapping 22-session windows as independent observations.
- If there are too few comparable observations, unstable results, missing timestamp granularity or no valid independent validation set, display **insufficient evidence / confidence unavailable** rather than 60%.
- Report the measured rate even if it is below 60%; do not round or tune a model merely to reach 60%.
- This is historical pattern/trigger validation, not trade backtesting, paper tracking, live monitoring or automatic trading. No P&L or executable-fill performance claim is implied.

### 5.6 Calculation methods still require approval

Do not invent:
- Seller concentration and spot pressure-level formulas.
- Adaptive primary upper premium trigger formula.
- Adaptive opposite lower premium trigger formula.
- Historical comparable-event definition and minimum sample size.
- Success/failure event, observation horizon and confidence estimator.
- Trigger persistence, sequence tolerance and invalidation rules.
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
- Adaptive primary upper panic-exit trigger and opposite lower confirmation trigger, if calculable.
- Sequential spot/primary-premium/additional-confirmation status.
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

5. **Premium panic-exit confirmation**
   - Seller-derived spot pressure/breakout threshold.
   - Selected primary option strike and adaptive upper premium panic-exit trigger.
   - Opposite option strike and adaptive lower premium confirmation trigger.
   - Option 2 primary signal status and additional-confirmation status.
   - Historical confidence/success estimate, numerator/denominator, validation sample count/period, success definition and method/version; unavailable when not validated.

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
11. Approve confidence/evidence scoring, the definition of a successful seller-pressure/premium-trigger event, historical validation period, minimum comparable sample size and reporting method. The requested 60% is a reference level to measure, not a guaranteed or hardcoded score.
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
- The user-approved Option 2 rule: NIFTY spot condition plus primary option premium trigger are the two primary conditions; opposite-side premium trigger is additional confirmation.
- The user-requested 60% confidence reference, represented only as a historical validation result when supported by comparable observations; never as a fixed or guaranteed value.

The source materials do not provide approved formulas, ranking weights, numeric thresholds, final S/R methodology, final engine names or final report dependencies. Those remain open decisions. No application code, schema, migrations, data, report ingestion, deployment or production configuration is changed by this document.
