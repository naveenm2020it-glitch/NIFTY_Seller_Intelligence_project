# Development Setup

This guide documents an optional local developer setup. A local laptop is not required for the project's repository-based workflow: GitHub Actions installs dependencies on a clean runner, provisions temporary PostgreSQL, applies migrations, runs backend tests and builds the frontend.

## Requirements

- Python 3.12
- Node.js 22 and npm
- PostgreSQL 16 (or a compatible supported PostgreSQL version)
- Git

No paid service is required for local development. PostgreSQL can be installed locally or run in an environment you control. Backblaze B2 is configured for CI connectivity verification; local object-storage use still requires the appropriate local environment variables. Usage may incur provider charges.

## Repository configuration

1. Clone the repository and check out `phase-2-user-config-orchestration`.
2. Copy `.env.example` to `.env` at the repository root.
3. Replace the PostgreSQL placeholders with a local database URL.
4. Set DATA_STORAGE_PATH to the extracted Phase 1 archive root. The root must contain artifacts/manifests/fo-download-manifest.json, artifacts/manifests/nifty50-download-manifest.json and artifacts/raw/nse with the three audited source folders. The application reads these files locally and verifies their manifest byte sizes and SHA-256 values.
5. B2 is optional. Phase 2 does not download or materialize the archive from B2; extract the verified archive locally first.
6. Keep .env untracked. Never commit credentials or historical market data.

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

The storage health endpoint returns HTTP 503 until valid B2 settings and a reachable bucket are configured in the environment running the application. The Phase 2 configuration endpoints require the extracted local archive and DATA_STORAGE_PATH.

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

- Phase 2 adds only the analysis_runs table to persist immutable run snapshots and lifecycle outcomes; later domain tables remain deferred.
- Live B2 bucket reachability has been verified by CI using `HeadBucket`; live upload, download and delete operations have not been validated against the real bucket.
- The Phase 2 archive resolver reads local files only; it does not download from NSE or materialize the B2 archive. No analytical engine, scenario engine or trained model is included.
- GitHub Actions databases and runners are temporary. CI is validation, not hosting.
- Render configuration is prepared but no service or deployment has been created.
- No persistent cloud development workspace or production deployment is configured.
