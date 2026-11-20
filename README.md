# NIFTY Seller Intelligence

A historical, end-of-day (EOD) NIFTY options analysis application built around the principle:

**Think like an Option Seller. Generate opportunities for an Option Buyer.**

## Project principles
- NIFTY 50 and NIFTY options only.
- Historical EOD analysis; no live-market analysis.
- No automated trading or order execution.
- Use permitted, freely accessible NSE reports and preserve original source files.
- Zero mandatory recurring software or infrastructure subscriptions.
- Reproducible analysis with recorded inputs, configurations and model versions.
- Pattern improvements require historical validation before approval.

## Technology architecture
- Frontend: React + Vite
- Backend: Python + FastAPI
- Architecture: Modular monolith
- Database: PostgreSQL
- Data processing: Pandas + NumPy (to be introduced with data-processing implementation)
- Machine learning: Scikit-learn initially (to be introduced with ML implementation)
- Testing: Pytest
- Development and validation: GitHub Actions remote CI; optional local setup

No cloud provider, paid market-data API, paid AI API, or paid hosting service is mandatory.

## Repository layout
- `backend/`: FastAPI application, database foundation and business modules.
- `frontend/`: React web application.
- `docs/`: Architecture, database, API and development documentation.
- `scripts/`: Reserved for setup, data and maintenance utilities.
- `tests/`: Cross-module integration tests.
- `storage/`: Repository placeholder only. Actual historical data must not be committed.

## Development status
**Phase 0 foundation is implemented and remotely validated.** The repository includes the FastAPI health endpoints, React/Vite production build, PostgreSQL connectivity foundation, an Alembic baseline migration, and a CI workflow that provisions a temporary PostgreSQL 16 service and runs backend tests and the frontend build.

See [Phase 0 completion checklist](docs/development/phase-0.md), [setup guide](docs/development/setup.md), and [remote validation guide](docs/development/remote-validation.md).

GitHub Actions runners are temporary validation environments, not a persistent server, database, or hosted application. The project owner can continue repository work without a local laptop; an interactive persistent development environment or deployment is a separate decision.

## Data-source compliance
Before implementing automated NSE data acquisition, review the applicable NSE terms and determine which reports and collection methods permit the intended use. Do not bypass access controls or implement collection methods prohibited by the source terms.

## Security
- Keep credentials and local configuration in an untracked `.env` file.
- Never commit API keys, passwords, tokens, personal data or raw historical archives.
- Use `.env.example` only for placeholder variable names and safe example values.
- CI database credentials are disposable test-only values for the ephemeral PostgreSQL service.

## License
No project license has been selected yet. Do not assume that this repository or its contents are open for unrestricted reuse until a license is chosen.
