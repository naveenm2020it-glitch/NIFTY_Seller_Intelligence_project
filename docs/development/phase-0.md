# Phase 0 — Foundation Setup

<small>Scope: establish a reproducible application foundation, not implement NIFTY analysis or trading intelligence.</small>

## Confirmed decisions
- Repository: `NIFTY_Seller_Intelligence_project`
- Frontend: React + Vite
- Backend: Python + FastAPI
- Architecture: Modular monolith
- Database: PostgreSQL
- Data analysis: Pandas + NumPy when data-processing implementation begins
- ML: Scikit-learn initially, when ML implementation begins
- Testing: Pytest
- Development approach: repository-first with remote CI validation; local setup is documented but is not a prerequisite for the project owner
- Cost principle: zero mandatory recurring software or infrastructure subscriptions

## Completion checklist

| Item | Status | Evidence / boundary |
|---|---|---|
| Repository creation and verification | Complete | GitHub repository and `phase-0-foundation` branch |
| Architecture and folder design | Complete | `docs/architecture/overview.md` and repository structure |
| Repository skeleton | Complete | Backend, frontend, docs, scripts, tests and storage directories |
| Python application foundation | Complete | FastAPI app and health endpoint |
| React + Vite foundation | Complete | Frontend dependencies and production build |
| PostgreSQL configuration foundation | Complete | SQLAlchemy engine, Psycopg driver and database health endpoint |
| Database migrations | Complete for baseline | Alembic configured; initial revision intentionally creates no domain tables |
| Environment and storage configuration guidance | Complete for foundation | `.env.example`, `.gitignore`, setup and database documentation; storage path is a documented configuration value, not yet wired into data-ingestion code |
| Health checks and automated tests | Complete | API and database tests run in CI |
| Clean setup and remote verification | Complete | GitHub Actions installs dependencies on a clean runner, applies migrations to temporary PostgreSQL 16, runs pytest and builds the frontend |

## Validation boundary
The CI workflow is the reproducibility check for this stage. It provisions a fresh PostgreSQL service for each run and destroys it when the run ends. This confirms that the checked-in dependencies, migration baseline and tests work together in that environment. It does **not** provide a persistent database, deployed API, public frontend, or local-machine verification.

The project owner does not need to run terminal commands to complete this phase. Optional local setup instructions are available in [setup.md](setup.md) for a future developer environment.

## Deliberately not included in Phase 0
- NSE report collection or automated downloads.
- Domain database tables for contracts, option-chain observations, candles, signals or analysis results.
- Analytical engine implementation.
- Scenario decision logic.
- ML training or model evaluation.
- Feedback-learning implementation.
- Cloud deployment, persistent hosting or paid service integration.
- Live-market analysis or automated trade/order execution.

These are subsequent implementation decisions and must be designed against the approved requirements rather than guessed into the foundation.

## Safety and data handling
- Do not commit raw NSE reports, historical datasets, secrets, database files or trained model artifacts.
- Confirm permitted data acquisition methods and applicable NSE terms before automating downloads.
- Preserve original source data and provenance when data ingestion is implemented.
- Keep candidate pattern improvements separate from approved patterns until historical validation supports promotion.

## Phase 0 exit decision
**Phase 0 foundation is complete based on remote CI validation.** Phase 1 can begin with requirements and data-model design. Do not interpret Phase 0 completion as evidence that the analysis engines, historical dataset, or production runtime already exist.
