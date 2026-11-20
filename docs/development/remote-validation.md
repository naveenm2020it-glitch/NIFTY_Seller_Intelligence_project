# Remote Development and Validation

The project owner currently does not have a laptop available for local development. The project therefore uses GitHub-hosted Actions runners to install dependencies and execute automated checks remotely.

## What the CI workflow validates
- A clean Ubuntu runner for each workflow execution.
- Python 3.12 environment for backend checks.
- Node.js 22 environment for frontend dependency installation and production build.
- FastAPI health-endpoint tests and database connectivity tests.
- PostgreSQL 16 service startup, Alembic migration application and database-backed tests.
- Frontend production build using the checked-in package manifest.

## What this does not provide
- A persistent server that stays online.
- A permanent PostgreSQL database or retained application data.
- A browser-based interactive development workspace.
- A production deployment or public application URL.
- A guarantee of free GitHub Actions usage beyond the account's applicable limits.

GitHub Actions usage is subject to the repository/account plan's included minutes and storage limits. No paid service is intentionally configured.

## Trigger
The workflow runs on pushes to `phase-0-foundation` and `main`, pull requests targeting either branch, or manual dispatch.

## Current CI sequence
1. Checkout repository.
2. Install Python 3.12 dependencies.
3. Start a temporary PostgreSQL 16 service.
4. Run `alembic upgrade head`.
5. Run backend tests with `pytest`.
6. Install Node.js 22 dependencies and run the frontend production build.

## How to inspect a validation run
Open the repository's **Actions** tab, select **Phase 0 Foundation CI**, and inspect both the **Backend checks** and **Frontend build** jobs. A successful run means both jobs completed successfully for that commit.

## Development environment choices
- **Repository edits and automated checks:** can continue through GitHub without a local laptop.
- **Optional local development:** see [setup.md](setup.md).
- **Interactive cloud workspace or persistent hosting:** not currently configured. Evaluate separately before enabling; availability, included usage and cost depend on the provider and account plan.
