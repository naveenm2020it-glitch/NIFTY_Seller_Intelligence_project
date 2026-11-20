# Phase 0 — New Repository & Complete Foundation Setup

Scope: establish the new repository and a reproducible application foundation. This phase does not implement NIFTY analysis, NSE data acquisition or trading intelligence.

## Original seven-step plan

| # | Original task | Status | Evidence / boundary |
|---:|---|---|---|
| 1 | Finalize the new repository name | Complete | `NIFTY_Seller_Intelligence_project` |
| 2 | Create the new GitHub repository | Complete | Public repository created; `phase-0-foundation` is the working branch |
| 3 | Design folder structure and architecture | Complete | Modular-monolith layout and [architecture overview](../architecture/overview.md) |
| 4 | Establish Python/FastAPI environment | Complete | Python 3.12, FastAPI app, pinned dependencies and remote CI |
| 5 | Configure PostgreSQL and Backblaze B2 integrations | Complete for foundation | PostgreSQL/SQLAlchemy/Psycopg/Alembic; B2 S3-compatible adapter, configuration and mocked storage tests. A live B2 connection still requires owner-managed bucket credentials |
| 6 | Build initial health-check APIs and tests | Complete | `/health`, `/health/database`, `/health/storage`; backend tests include database, API, B2 mock and data-science smoke tests |
| 7 | Complete Phase 0 documentation | Complete | Architecture, setup, database, storage, health API, remote validation and this checklist |

## Foundation checklist

| Area | Status | Evidence |
|---|---|---|
| New GitHub repository and branch workflow | Complete | New repository; changes isolated on `phase-0-foundation` |
| Backend folder structure | Complete | API, core, database, storage, modules, migrations and tests |
| Frontend folder structure | Complete | React + Vite application structure |
| Documentation and scripts structure | Complete | Architecture, API, database, development, storage, setup/data/maintenance placeholders |
| Python and FastAPI | Complete | Python 3.12 CI; FastAPI application and endpoints |
| PostgreSQL | Complete for foundation | SQLAlchemy 2, Psycopg 3, connection check and temporary PostgreSQL 16 CI service |
| Alembic | Complete for baseline | Initial empty migration; domain tables intentionally deferred |
| Backblaze B2 | Complete for integration foundation | S3-compatible client, configuration, connection check and file operation adapter; live bucket access not yet verified |
| Pandas and NumPy | Complete | Pinned dependencies and CI smoke test |
| ML environment | Complete for foundation | Scikit-learn pinned and smoke-tested; no model training in Phase 0 |
| Environment configuration | Complete | Root `.env` loading; process environment takes precedence; `.env.example` |
| Security and secrets | Complete for foundation | `.env` ignored, placeholder-only example, runtime secret variables, no credentials in tests |
| Automated tests | Complete | Pytest backend tests and CI |
| Frontend build | Complete | React/Vite production build in CI |
| Render preparation | Complete, not deployed | `render.yaml`; auto-deploy disabled; no services created |
| Documentation | Complete | README, architecture, API, database, storage, setup and validation docs |

## Validation evidence

The previous CI run on commit `141b497f7347f9211fa24ecfdc5ac51c247135d0` passed both backend and frontend jobs. The Phase 0 completion changes must pass CI again before this checklist is treated as verified for the current commit.

The workflow provisions a temporary PostgreSQL 16 service, applies Alembic migrations, runs backend tests and builds the frontend. CI does not provide persistent hosting or a permanent database.

## Explicit Phase 0 exclusions

- NSE report collection or automated downloads.
- Domain tables for contracts, option-chain observations, candles, signals or analysis results.
- Analytical engines, eight-scenario decision logic or ML model training.
- Feedback-learning implementation.
- Production deployment, persistent cloud database or production runtime.
- Live-market analysis or automated trade/order execution.

These belong to later phases and must be designed against the approved requirements.

## External activation still required

A real Backblaze B2 bucket and bucket-restricted application key must be created and configured by the owner in a trusted runtime before live storage connectivity can be confirmed. The repository contains no credentials, does not create a bucket and does not provision paid services. See [storage setup](../storage/README.md).

## Phase 0 exit criteria

Phase 0 implementation is ready for final remote validation. Mark the phase closed only after the current commit's GitHub Actions run succeeds. A live B2 connection is an external credential-dependent activation, not something CI can verify with mock credentials. Phase 1 can then begin with the historical EOD data audit and approved data-model design.
