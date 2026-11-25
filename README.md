# NIFTY Seller Intelligence

A historical, end-of-day (EOD) NIFTY options analysis application built around the principle:

**Think like an Option Seller. Generate opportunities for an Option Buyer.**

## Principles
- NIFTY 50 and NIFTY options only; historical EOD analysis only.
- No live-market analysis, automated trading or order execution.
- Preserve original permitted NSE source files.
- Reproducible analysis with recorded inputs, configurations and provenance.
- Pattern improvements require historical validation before approval.

## Architecture
React + Vite frontend; Python + FastAPI modular monolith; PostgreSQL; optional Backblaze B2 S3-compatible storage; Pandas + NumPy; Scikit-learn; Pytest.

## Development status

The canonical, current phase status and merge evidence are maintained in [docs/development/project-status.md](docs/development/project-status.md). For actual implementation status, use the repository's `main` branch; draft pull requests describe proposed work and do not count as completed phases.

| Phase | Status | Source |
|---|---|---|
| Phase 0 — Foundation | Completed | docs/development/phase-0.md |
| Phase 1 — Historical EOD Data Audit | Completed | docs/development/phase-1-closeout.md |
| Phase 2 — User Configuration & Data Orchestration | Completed | docs/development/phase-2-closeout.md |
| Phase 3 — Storage & Data Processing | Completed | docs/development/phase-3-closeout.md |
| Phase 4 — Feature Engineering | Pending — specification documented; implementation not started | docs/development/phase-4-feature-engineering-spec.md |
| Phase 5 — Eight Analytical Engines | Pending — functional specification draft under review | PR #9 (draft) |
| Phase 6 — Eight-Scenario Decision Engine | Pending — requirements included in PR #9 draft | PR #9 (draft) |
| Phase 7 — Four ML Models | Pending | To be specified after feature/engine validation |
| Phase 8 — Complete Web Dashboard | Pending | To be specified |
| Phase 9 — QA & Production Readiness | Pending | To be specified |
| Phase 10 — Feedback & Continuous Pattern Learning | Pending | To be specified |

Phase 1 and Phase 2 were integrated into `main` through merged PR [#5](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/5). Phase 3 was integrated through merged PR [#6](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/6). The eight-engine/eight-scenario functional specification is still in [draft PR #9](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/pull/9); it is not approved or implemented. Phase completion does not authorize production deployment.

## Phase 2 implementation boundary
The API and frontend provide analysis-date selection, automatic nearest available expiry, manual expiry override, explicit Start Analysis, idempotent run records, source-manifest provenance and checksum/schema validation. `READY_FOR_PROCESSING` means only that inputs are validated for a later phase; no analytics are executed. The application reads an extracted local Phase 1 archive and does not automate NSE collection. See the Phase 2 data contract for archive layout and API details.

## Phase 3 implementation boundary
Phase 3 adds manifest-verified, read-only parsing of the three audited core reports; NIFTY 50 and selected-expiry NIFTY CE/PE normalization; contract reconciliation; validation; PostgreSQL persistence; processing/status/read APIs; provenance; idempotency; source-conflict detection and retryable failures. Standard backend/synthetic archive tests, PostgreSQL migration upgrade/downgrade/re-upgrade tests and frontend build passed. The real B2 archive integration was skipped because of the account's AccessDenied/Class B transaction cap; it is not claimed as passed. See the Phase 3 closeout and data contract.

## Phase 4 boundary
Phase 4 is Feature Engineering (1/5/22-session descriptive features). The convention for counting 1/5/22 EOD records, including the Analysis Date, is approved. The feature catalogue, formulas, feature schema and persistence/API choices remain under review and require approval before implementation. The separate eight-engine/eight-scenario document describes proposed requirements for later Phases 5–6, not Phase 4 implementation.

## Security and operations
Keep credentials in an untracked .env or secret store. Never commit credentials or raw market archives. B2 remains optional; Phase 3 does not claim automatic application-side B2 archive materialization. The application still requires an extracted local archive. Automatic NSE collection is not implemented. No production deployment is authorized.

## License
No project license has been selected. Do not assume unrestricted reuse.
