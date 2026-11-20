# Remote Development and Validation

The project uses GitHub-hosted Actions runners to install dependencies and execute automated checks. The project owner does not need a local laptop to validate repository changes.

## What the CI workflow validates
- A clean Ubuntu runner for each workflow execution.
- Python 3.12 environment for backend checks.
- Installation of FastAPI, PostgreSQL, B2, Pandas, NumPy and Scikit-learn dependencies.
- A temporary PostgreSQL 16 service, Alembic migration application and database-backed tests.
- API health checks and mocked B2 storage integration tests.
- Basic Pandas/NumPy operations and a Scikit-learn smoke test.
- Node.js 22 environment, frontend dependency installation and production build.

## What this does not provide
- A persistent server that stays online.
- A permanent PostgreSQL database or retained application data.
- A live Backblaze B2 bucket connection; tests mock the S3-compatible API.
- A browser-based interactive development workspace.
- A production deployment or public application URL.
- A guarantee of free GitHub Actions usage beyond the account's applicable limits.

GitHub Actions usage is subject to the repository/account plan's included minutes and storage limits. No paid service is intentionally provisioned by CI.

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

## Development and deployment choices
- **Repository edits and automated checks:** can continue through GitHub without a local laptop.
- **Optional local development:** see [setup.md](setup.md).
- **Render:** an optional Blueprint is checked in with automatic deploy disabled. No services have been created.
- **Interactive cloud workspace or persistent hosting:** not configured. Evaluate separately before enabling; availability, included usage and cost depend on the provider and account plan.
