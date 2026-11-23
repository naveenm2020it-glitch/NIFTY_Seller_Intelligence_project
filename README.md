# NIFTY Seller Intelligence

A historical, end-of-day (EOD) NIFTY options analysis application built around the principle:

**Think like an Option Seller. Generate opportunities for an Option Buyer.**

## Project principles
- NIFTY 50 and NIFTY options only.
- Historical EOD analysis; no live-market analysis.
- No automated trading or order execution.
- Use permitted, freely accessible NSE reports and preserve original source files.
- Zero mandatory recurring software or infrastructure subscriptions; optional B2 usage can incur provider charges.
- Reproducible analysis with recorded inputs, configurations and model versions.
- Pattern improvements require historical validation before approval.

## Technology architecture
- Frontend: React + Vite
- Backend: Python + FastAPI
- Architecture: Modular monolith
- Database: PostgreSQL
- Object storage: Backblaze B2 through its S3-compatible API (optional credentials)
- Data processing: Pandas + NumPy
- Machine learning foundation: Scikit-learn
- Testing: Pytest
- Development and validation: GitHub Actions remote CI; optional local setup

## Repository layout
- `backend/`: FastAPI application, database, storage adapter and business modules.
- `frontend/`: React web application.
- `docs/`: Architecture, database, storage, API and development documentation.
- `scripts/`: Reserved for setup, data and maintenance utilities.
- `tests/`: Cross-module integration tests.
- `storage/`: Repository placeholder only. Actual historical data must not be committed.

## Development status

| Phase | Status | Source of truth |
|---|---|---|
| Phase 0 — New Repository & Complete Foundation Setup | **Completed** | [Phase 0 checklist](docs/development/phase-0.md) |
| Phase 1 — Historical EOD Data Audit | **Completed — 23 November 2026** | [Phase 1 closeout](docs/development/phase-1-closeout.md) |
| Phase 2 — User Configuration & Data Orchestration | **In progress — requirements documented; application implementation pending** | [Phase 2 requirements](docs/development/phase-2-user-configuration-and-orchestration.md) |

Phase 1 acquisition and audit tooling, closeout evidence and preservation utilities are integrated into the Phase 2 development branch. The Phase 1 branch history is retained as a parent of the integration commit. This integration does not merge into `main` and does not authorize production deployment.

See the [Phase 1 closeout](docs/development/phase-1-closeout.md), [Phase 1 sample audit](docs/development/phase-1-sample-audit.md), [Phase 2 requirements](docs/development/phase-2-user-configuration-and-orchestration.md), [EOD report inventory review](docs/data/eod-report-inventory-review.md), [Phase 0 checklist](docs/development/phase-0.md), [setup guide](docs/development/setup.md), [storage guide](docs/storage/README.md), and [remote validation guide](docs/development/remote-validation.md).

GitHub Actions runners and PostgreSQL services are temporary validation environments, not a persistent server, database or hosted application. Render configuration is prepared but no deployment has been made.

## Data-source compliance
Before implementing automated NSE data acquisition, review the applicable NSE terms and determine which reports and collection methods permit the intended use. Do not bypass access controls or implement collection methods prohibited by the source terms.

## Security
- Keep credentials and local configuration in an untracked `.env` file or deployment secret store.
- Never commit API keys, passwords, tokens, personal data or raw historical archives.
- Use `.env.example` only for placeholder variable names and safe example values.
- CI database credentials are disposable test-only values for the ephemeral PostgreSQL service.
- B2 tests use a mock client and do not require real credentials.

## License
No project license has been selected yet. Do not assume that this repository or its contents are open for unrestricted reuse until a license is chosen.
