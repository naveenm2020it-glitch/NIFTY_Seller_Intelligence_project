# Development Setup

This guide documents an optional local developer setup. A local laptop is not required for the project's repository-based workflow: GitHub Actions installs dependencies on a clean runner, provisions temporary PostgreSQL, applies migrations, runs backend tests and builds the frontend.

## Requirements

- Python 3.12
- Node.js 22 and npm
- PostgreSQL 16 (or a compatible supported PostgreSQL version)
- Git

No paid service is required for local development. PostgreSQL can be installed locally or run in an environment you control. Backblaze B2 is configured for CI connectivity verification; local object-storage use still requires the appropriate local environment variables. Usage may incur provider charges.

## Repository configuration

1. Clone the repository and check out `phase-0-foundation`.
2. Copy `.env.example` to `.env` at the repository root.
3. Replace the PostgreSQL placeholders with a local database URL.
4. For local B2 use, configure the five B2 values for the existing bucket and its bucket-restricted application key.
5. Keep `.env` untracked. Never commit credentials or historical market data.

The backend loads the repository-root `.env` file automatically when configuration is imported. Existing process environment variables take precedence, which allows CI and deployment platforms to supply their own values.

## Backend

Run these commands from the repository root:

```bash
python3.12 -m venv backend/.venv
source backend/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
cd backend
alembic upgrade head
python -m pytest -q
uvicorn app.main:app --reload
```

The PostgreSQL database must exist and be reachable before applying migrations.

Health endpoints:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/health/database`
- `http://127.0.0.1:8000/health/storage`

The storage health endpoint returns HTTP 503 until valid B2 settings and a reachable bucket are configured in the environment running the application.

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
- Live B2 bucket reachability has been verified by CI using `HeadBucket`; live upload, download and delete operations have not been validated against the real bucket.
- No NSE data downloader, analytical engine, scenario engine or trained model is included.
- GitHub Actions databases and runners are temporary. CI is validation, not hosting.
- Render configuration is prepared but no service or deployment has been created.
- No persistent cloud development workspace or production deployment is configured.
