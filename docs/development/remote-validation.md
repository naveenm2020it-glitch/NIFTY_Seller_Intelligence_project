# Remote Development and Validation

The project owner currently does not have a laptop available for local development. Phase 0 therefore uses GitHub-hosted Actions runners to install dependencies and execute automated checks remotely.

## What this provides
- A clean Ubuntu runner for each workflow execution.
- Python 3.12 environment for backend checks.
- Node.js 22 environment for frontend dependency installation and production build.
- Automated FastAPI health-endpoint tests.
- Build/test logs visible in the repository's Actions tab.

## What this does not provide
- A persistent server that stays online.
- A permanent PostgreSQL database.
- A browser-based interactive development workspace.
- A production deployment or public application URL.

GitHub Actions usage is subject to the repository/account plan's included minutes and storage limits. No paid service is intentionally configured.

## Trigger
The workflow runs on pushes to `phase-0-foundation` and `main`, pull requests targeting either branch, or manual dispatch.

## Next environment tasks
1. Confirm CI workflow results.
2. Add PostgreSQL service-backed integration tests when the database layer is introduced.
3. Decide whether a browser-based Codespaces workspace is needed; availability and included usage depend on the GitHub account plan.
