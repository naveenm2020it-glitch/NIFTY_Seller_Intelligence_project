# Development Setup

This guide documents an optional local developer setup. **A local laptop is not required for the project's current repository-based workflow:** GitHub Actions installs dependencies on a clean runner, provisions temporary PostgreSQL, applies migrations, runs backend tests and builds the frontend.

## Requirements

- Python 3.12
- Node.js 22 and npm
- PostgreSQL 16 (or a compatible supported PostgreSQL version)
- Git

No paid service is required for this local setup. PostgreSQL can be installed locally or run in an environment you control.

## Repository configuration

1. Clone the repository and check out the working branch.
2. Copy `.env.example` to `.env` for reference, then replace placeholders with local values.
3. Keep `.env` untracked. Never commit credentials or historical market data.

The current FastAPI configuration reads `DATABASE_URL` from the process environment. Automatic `.env` loading is not configured, so export `DATABASE_URL` in the shell or set it in the environment used to start the backend. `DATA_STORAGE_PATH` is reserved configuration guidance at this stage; data-ingestion code does not yet consume it.

## Backend

Run these commands from the repository root:

```bash
python3.12 -m venv backend/.venv
source backend/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
export DATABASE_URL='postgresql+psycopg://USER:PASSWORD@localhost:5432/nifty_seller_intelligence'
cd backend
alembic upgrade head
python -m pytest -q
uvicorn app.main:app --reload
```

Replace the database URL placeholders with the credentials and database name configured in your PostgreSQL instance. The database must exist and be reachable before applying migrations.

Health endpoints:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/health/database`

## Frontend

In a second terminal, from the repository root:

```bash
cd frontend
npm install
npm run build
npm run dev
```

Vite prints the local development URL after the dev server starts. The production build is written to `frontend/dist/` and is ignored by Git.

## Remote validation without local setup

Push changes to `phase-0-foundation` or open a pull request targeting that branch. The **Phase 0 Foundation CI** workflow performs the backend migration and test steps against an ephemeral PostgreSQL 16 service and builds the frontend. See [remote-validation.md](remote-validation.md).

## Current limitations

- The Alembic baseline is intentionally empty; domain-specific tables have not been designed.
- No NSE data downloader, analytical engine, scenario engine or trained model is included.
- GitHub Actions databases and runners are temporary. CI is validation, not hosting.
- No persistent cloud development workspace or production deployment is configured.
