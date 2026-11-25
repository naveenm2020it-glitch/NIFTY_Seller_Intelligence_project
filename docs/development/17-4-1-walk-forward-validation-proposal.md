# 17 + 4 + 1 — Walk-Forward Forecast-Validation Proposal

**Status:** Owner-approved high-level workflow concept; detailed evaluation definitions and implementation remain pending.  
**Phase placement:** Later prediction/validation phase, not Phase 4 Feature Engineering.  
**Data scope:** Historical NIFTY 50 and selected-expiry NIFTY CE/PE EOD observations already validated and persisted by Phase 3.

## 1. Objective

Use a chronological 22-session sample to establish an initial baseline, perform four sequential one-session-ahead forecast checks, and then produce a final one-session-ahead assessment for the 22nd session without using that session's actual EOD data as an input.

This protocol is intended to check whether the later analytical engines use only information that would have been available at the time of each forecast. It is not a trading strategy, order simulation or P&L backtest.

## 2. Session allocation

| Sessions | Role | Permitted information | Required action |
|---|---|---|---|
| 1–17 | Initial baseline | EOD data from Sessions 1–17, plus a prior close dependency only where the approved feature requires it | Establish the initial cumulative historical context and feature baseline |
| 18 | First validation target | Sessions 1–17 only | Record a one-session-ahead forecast for Session 18; after it is fixed, compare with Session 18 actual EOD |
| 19 | Second validation target | Sessions 1–18 only | Record a one-session-ahead forecast for Session 19; then compare with actual EOD |
| 20 | Third validation target | Sessions 1–19 only | Record a one-session-ahead forecast for Session 20; then compare with actual EOD |
| 21 | Fourth validation target | Sessions 1–20 only | Record a one-session-ahead forecast for Session 21; then compare with actual EOD |
| 22 | Final forecast target | Sessions 1–21 only | Record the one-session-ahead assessment for Session 22; do not use Session 22 actual EOD as an input |

## 3. No-look-ahead rules

1. A forecast for target session T may use only validated observations dated before T.
2. The target session's OHLC, option premium, OI, volume or any other EOD value must not enter its own forecast features.
3. Freeze and timestamp or otherwise immutably identify each forecast output before joining it to the target session's actual EOD outcome.
4. Actual target-session data may be used only for evaluation after the forecast is fixed.
5. Do not use future contract identity, future expiry availability or future source data to construct an earlier forecast.
6. Preserve source hashes, Analysis Run IDs, feature-definition version, target date, input date range and forecast output version for every evaluation record.
7. Missing observations remain missing. Do not forward-fill, interpolate, substitute another strike/expiry or treat missing values as zero.
8. Keep each option contract's history separate using the approved exact contract identity.

## 4. Relationship to Phase 4

Phase 4 supplies deterministic, versioned 1/5/22-session descriptive features. It does not implement this forecast-validation loop.

The 17 + 4 + 1 protocol consumes Phase 4 features in a later phase, together with separately approved analytical-engine definitions. It must not be used to redefine the Phase 4 N-session window contract.

## 5. Evaluation limitations

- Four validation targets (Sessions 18–21) are a small workflow check, not a statistically reliable estimate of predictive accuracy.
- Do not publish confidence percentages, accuracy claims, model performance rankings or generalization claims from this 4-target sample alone.
- A meaningful evaluation requires more chronological windows, explicit target/outcome definitions, consistent scoring rules and leakage-safe separation of development and evaluation periods.
- The exact forecast targets (for example, direction, range, volatility or contract-level outcome), evaluation metrics, tolerances and minimum sample requirements remain unapproved.
- No trading P&L, simulated orders, broker execution or live/intraday functionality is included.

## 6. Decisions required before implementation

1. Define the exact forecast targets for NIFTY spot and selected-expiry CE/PE contracts.
2. Define what constitutes a correct, incorrect or indeterminate forecast for each target.
3. Approve evaluation metrics and any tolerances; do not invent thresholds.
4. Define how unavailable or incomplete EOD sessions affect a 22-session sample.
5. Decide how many chronological 22-session windows are required for a meaningful evaluation.
6. Define immutable forecast-record storage and idempotency.
7. Confirm the later phase responsible for the validation workflow and its relationship to the eight analytical engines.

Until these decisions are approved, this document records the workflow concept only. No forecast engine or validation code is authorized by this proposal.
