# NIFTY Seller Intelligence — Canonical Development Status

**Status date:** 25 November 2026  
**Canonical source:** This file and the README on the repository's `main` branch.  
**Current verified `main` HEAD at this status update:** `9f0435f6cbb8002ed03d0cfb143893c1609ee87b`.

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

### Phase 3 real archive end-to-end validation — run #45547427122
- Downloaded the immutable Phase 1 GitHub Actions artifact ID `14688805993` from run `44858251380`; the downloaded ZIP SHA-256 matched the recorded artifact digest.
- Reverified all 68 raw source files against their manifests and confirmed the Phase 1 audit remains 15/15.
- Applied the Phase 3 Alembic migration to a temporary PostgreSQL 16 CI database.
- Ran the opt-in real-archive Phase 3 API test across all 22 audited trading dates, 21-Oct-2026 through 19-Nov-2026.
- Verified 22 AnalysisRuns reached `PROCESSED`, 22 ingestion batches reached `COMPLETED`, all 22 NIFTY 50 daily bars were persisted, selected-expiry CE/PE option rows were persisted and readable through the API, and each option underlying close reconciled to the NIFTY 50 close.
- The test passed: 1 passed in 240.83 seconds. This used the preserved GitHub artifact, not a B2 download; it does not change the separate B2 smoke-test limitation.
- The PostgreSQL database was temporary CI infrastructure. This does not establish persistent hosted-database coverage or a production data load.

### Phase 3 full 22-session archive validation — PRs #14 and #15
- PR [#14](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/14), merge commit `9f0435f6cbb8002ed03d0cfb143893c1609ee87b`, integrated the opt-in real-archive Phase 3 test and its closeout/status evidence.
- PR [#15](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/15), merge commit `98bfdc6f0b2c7b3959a20e5084d08be943c185d2`, supplied the one-time branch-scoped workflow job used to execute the test against the preserved Phase 1 artifact.
- Successful real-archive test: [GitHub Actions run #45547427122](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/actions/runs/45547427122). All 22 audited sessions were processed and persisted in temporary PostgreSQL 16; 22 AnalysisRuns and batches, 22 index bars, selected-expiry CE/PE readback and underlying-close reconciliation passed.
- The temporary branch-specific artifact-download job is removed after this one-time verification; the opt-in test remains in the repository. The archived GitHub artifact is not a permanent CI dependency.

### Phase 4 specification — PR #8
- PR: [#8](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/8)
- Merge commit: `300c3f5d577231672b6ad458740752d10a1b19ff`
- Merged README roadmap corrections, the Phase 4 Feature Engineering design draft and this canonical status reference.
- PR #8 CI passed for backend/PostgreSQL migration checks and frontend build. The optional real B2 archive smoke test was skipped due to the known access/transaction-cap limitation.
- This merge integrates documentation only. It does not complete Phase 4 or authorize its implementation.

### Canonical status and Phase 3 closeout corrections — PRs #11 and #12
- PR [#11](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/11), merge commit `d10027ee8c3398fb366eb279388d695ff0c0fe8a`, corrected the recorded `main` baseline after PR #10.
- PR [#12](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/12), merge commit `33611d549206444355fcd72687fb410bf763b1ff`, corrected the Phase 3 closeout to record its actual PR #6 integration.
- Both were documentation-only changes; their GitHub Actions checks passed.

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

Phase 4 implementation is the next development phase, but its feature definitions and implementation choices are not yet approved. The real-archive Phase 3 CI test proves that all 22 audited sessions can be processed and persisted in a temporary PostgreSQL 16 database. It does not prove that those rows exist in a persistent hosted database. Before Phase 4 implementation, verify coverage in the intended persistent database if one is approved and provisioned; do not treat temporary CI data as persistent project data.

PR #9 remains a separate draft requirements document for Phases 5–6 and must not be treated as approved implementation scope.
