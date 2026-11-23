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
- An optional live Backblaze B2 `HeadBucket` check when all five `B2_*` repository Actions secrets are configured.

## What this does not provide
- A persistent server that stays online.
- A permanent PostgreSQL database or retained application data.
- Live validation of B2 file upload, download or delete operations. The CI run verifies bucket reachability only; the default storage operation tests use a mocked S3-compatible API.
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
6. If all five B2 repository secrets are present, run a read-only `HeadBucket` check against the configured bucket. If none are present, report the live check as skipped; partial configuration fails.
7. Install Node.js 22 dependencies and run the frontend production build.

## Live B2 connectivity verification

Live bucket reachability is verified. GitHub Actions run [#15 — Phase 0 Foundation CI](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/actions/runs/44709767148) completed successfully on 20 November 2026. Its **Backend checks**, **Frontend build** and **Verify live Backblaze B2 connectivity when credentials are configured** steps all succeeded. The B2 step used `HeadBucket`, which confirms access to the configured bucket without changing its contents.

The workflow reads these repository Actions secrets: `B2_ENDPOINT_URL`, `B2_REGION`, `B2_BUCKET_NAME`, `B2_APPLICATION_KEY_ID` and `B2_APPLICATION_KEY`. Use a bucket-restricted key and do not paste credentials into chat, issues, commits or workflow logs. The check does not validate live file upload, download or delete operations. See [storage setup](../storage/README.md).

## How to inspect a validation run
Open the repository's **Actions** tab, select **Phase 0 Foundation CI**, and inspect both the **Backend checks** and **Frontend build** jobs. In the backend job, inspect the optional live B2 step: success means the real bucket responded; skipped means credentials were not configured for that run.

## Development and deployment choices
- **Repository edits and automated checks:** can continue through GitHub without a local laptop.
- **Optional local development:** see [setup.md](setup.md).
- **Render:** an optional Blueprint is checked in. The API is configured for the free compute plan, static hosting does not use a compute plan, and automatic deploy is disabled. No services have been created.
- **Interactive cloud workspace or persistent hosting:** not configured. Evaluate separately before enabling; availability, included usage and cost depend on the provider and account plan.
