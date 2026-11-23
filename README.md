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
| Phase | Status | Source |
|---|---|---|
| Phase 0 — Foundation | Completed | docs/development/phase-0.md |
| Phase 1 — Historical EOD Data Audit | Completed — 23 November 2026 | docs/development/phase-1-closeout.md |
| Phase 2 — User Configuration & Data Orchestration | Completed — 23 November 2026 | docs/development/phase-2-closeout.md |

Phase 1 history and audit tooling are integrated into the Phase 2 working branch. Phase 2 is complete on that branch; neither Phase 1 nor Phase 2 work has been merged to main or authorizes deployment.

## Phase 2 implementation boundary
The API and frontend provide analysis-date selection, automatic nearest available expiry, manual expiry override, explicit Start Analysis, idempotent run records, source-manifest provenance and checksum/schema validation. READY_FOR_PROCESSING means only that inputs are validated for a later phase; no analytics are executed. The application reads an extracted local Phase 1 archive and does not automate NSE collection. See the Phase 2 data contract for archive layout and API details.

## Security and operations
Keep credentials in an untracked .env or secret store. Never commit credentials or raw market archives. B2 remains optional; this phase does not claim remote B2 archive materialization. CI uses temporary PostgreSQL; the real-archive smoke test passed, and CI does not host the application. The application still requires an extracted local archive; automatic B2 materialization and NSE collection are not implemented. No production deployment is authorized.

## License
No project license has been selected. Do not assume unrestricted reuse.
