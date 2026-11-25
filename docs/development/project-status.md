# NIFTY Seller Intelligence — Canonical Development Status

**Status date:** 25 November 2026  
**Canonical source:** This file and the README on the repository's `main` branch.  
**Current verified `main` HEAD at this status update:** `348008e1efeaac429a0d7a5f9c87840670bbaa4b`.

## Source-of-truth rule

When a new chat, local note, uploaded summary or draft pull request conflicts with this document, verify the repository's `main` branch and its merged commit history. The `main` branch is authoritative for implemented and integrated work. Open or draft pull requests are proposals until merged; a specification is not an implementation.

Update this file whenever a phase is completed, a pull request is merged, or a project boundary changes. Record the merge commit and preserve any validation limitations. Do not infer phase completion from a branch name, draft PR, passing documentation check or CI run alone.

## Phase roadmap

| Phase | Name | Current status | Evidence / next step |
|---|---|---|---|
| 0 | Foundation | **Completed** | [Phase 0 closeout](phase-0.md). Foundation and CI baseline established. |
| 1 | Historical EOD Data Audit | **Completed and integrated** | [Phase 1 closeout](phase-1-closeout.md); integrated with Phase 2 through PR [#5](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/5), merge commit `82fcb219748e35ef22ab9fb51d71fd111b2d32de`. |
| 2 | User Configuration & Data Orchestration | **Completed and integrated** | [Phase 2 closeout](phase-2-closeout.md); PR [#5](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/5), merge commit `82fcb219748e35ef22ab9fb51d71fd111b2d32de`. |
| 3 | Storage & Data Processing | **Completed and integrated** | [Phase 3 closeout](phase-3-closeout.md); PR [#6](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/6), merge commit `8abbc8d125507d13ec42dde5ffec3ad81f3cbc18`. |
| 4 | Feature Engineering | **Specification merged; implementation pending** | [Phase 4 specification](phase-4-feature-engineering-spec.md), merged through PR [#8](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/8), merge commit `300c3f5d577231672b6ad458740752d10a1b19ff`. Documentation only; feature decisions and implementation remain pending. |
| 5 | Eight Analytical Engines | **Pending** | Requirements draft in PR [#9](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/9); not approved or implemented. |
| 6 | Eight-Scenario Decision Engine | **Pending** | Requirements draft in PR [#9](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/9); not approved or implemented. |
| 7 | Four ML Models | **Pending** | Requires validated upstream features and approved model requirements. |
| 8 | Complete Web Dashboard | **Pending** | To be specified after analytical requirements and outputs are established. |
| 9 | QA & Production Readiness | **Pending** | Not started; no production deployment is authorized. |
| 10 | Feedback & Continuous Pattern Learning | **Pending** | Requires separately approved feedback, validation, versioning and rollback design. |

## Integrated implementation evidence

### Phase 0 — Foundation
- Foundation repository, backend/frontend architecture, PostgreSQL/Alembic baseline, optional B2 adapter, health APIs and CI were completed.
- See [Phase 0 closeout](phase-0.md).
- Phase 0 completion does not mean the later analytical phases are implemented.

### Phases 1–2 — PR #5
- PR: [#5](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/5)
- Merge commit: `82fcb219748e35ef22ab9fb51d71fd111b2d32de`
- Phase 1 audited 22 historical EOD sessions and retained source-file provenance and audit evidence.
- Phase 2 delivered Analysis Date and Expiry selection, read-only preview, explicit run creation, manifest/checksum validation, provenance and PostgreSQL AnalysisRun persistence.
- `READY_FOR_PROCESSING` means inputs were validated for later processing; it does not mean analytics or signals were generated.

### Phase 3 — PR #6
- PR: [#6](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/6)
- Merge commit: `8abbc8d125507d13ec42dde5ffec3ad81f3cbc18`
- Delivered manifest-verified read-only parsing of the three audited core reports, NIFTY 50 and selected-expiry CE/PE normalization, contract reconciliation, validation, PostgreSQL EOD persistence, processing/status/read APIs, provenance, idempotency, source-conflict detection and retryable failures.
- Standard backend/synthetic archive tests, PostgreSQL migration upgrade/downgrade/re-upgrade tests and frontend build passed.
- **Real B2 archive integration was not passed in the Phase 3 run.** It was skipped/blocked by AccessDenied and the account's Class B transaction cap. Do not report this as a successful real-archive Phase 3 integration test.
- See [Phase 3 closeout](phase-3-closeout.md).

### Phase 4 specification — PR #8
- PR: [#8](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/8)
- Merge commit: `300c3f5d577231672b6ad458740752d10a1b19ff`
- Merged README roadmap corrections, the Phase 4 Feature Engineering design draft and this canonical status reference.
- PR #8 CI passed for backend/PostgreSQL migration checks and frontend build. The optional real B2 archive smoke test was skipped due to the known access/transaction-cap limitation.
- This merge integrates documentation only. It does not complete Phase 4 or authorize its implementation.

## Approved decisions and pending approvals

### Approved
- Analysis inputs remain **Analysis Date and Expiry only**; no cutoff-time input.
- Historical EOD analysis only.
- The 1/5/22 session-window convention: N means up to N available EOD records **including the Analysis Date**:
  - 1 = Analysis Date only.
  - 5 = Analysis Date plus the previous 4 available trading sessions.
  - 22 = Analysis Date plus the previous 21 available trading sessions.
- N EOD records contain N-1 close-to-close intervals between the first and last records. An extra earlier close may be a calculation dependency for a return, but is not counted in the N-record window.
- Missing observations must not be fabricated, forward-filled or silently replaced.

### Still pending approval
- Phase 4 feature catalogue and exact feature definitions.
- Percentage-change denominators and calculation conventions.
- Exact contract continuity key and missing-session treatment details beyond the approved no-fill rule.
- ITM/ATM/OTM classification boundaries.
- Volatility estimator, return convention, annualization and minimum-observation rules.
- Feature schema, persistence, idempotency and API/UI scope.
- Phase 5–6 S/R, seller-pressure, adaptive premium-trigger, ranking, confidence and risk formulas/thresholds.
- Phase 7 model definitions, training/validation design and acceptance criteria.
- Phase 10 feedback-learning governance and promotion/rollback criteria.

No unapproved formula, threshold, weight, confidence score or model behavior may be silently introduced.

## Non-negotiable project boundaries

- NIFTY 50 and NIFTY options; historical EOD only.
- No live/intraday monitoring or signal claims.
- No alerts, broker integration, order execution, paper tracking or trading backtesting.
- No automated NSE scraping/acquisition or supplementary report ingestion without separate authorization and data-use review.
- Preserve source data and provenance; do not overwrite Phase 3 raw/normalized records during feature work.
- Do not treat OI alone as proof of seller/writer identity, fresh writing or liquidation.
- Do not claim predictive accuracy or a success rate without a defined event, horizon, comparable sample, validation method and sufficient evidence.
- No production deployment, persistent hosted database or new paid infrastructure without explicit approval.
- Work on isolated branches and use pull requests. Do not make direct `main` changes or merge/deploy without explicit project-owner authorization.

## Current next step

Phase 4 implementation is the next development phase, but its feature definitions and implementation choices are not yet approved. Before writing Phase 4 code, first verify that the required historical 1/5/22 EOD records are actually persisted and queryable: Phase 3 processing is session-oriented, so do not assume the full 22-session window is already present in PostgreSQL. If history is missing, define and approve a safe historical loading approach before implementing features.

PR #9 remains a separate draft requirements document for Phases 5–6 and must not be treated as approved implementation scope.
