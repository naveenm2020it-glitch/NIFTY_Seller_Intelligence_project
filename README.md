# NIFTY Seller Intelligence

A historical, end-of-day (EOD) NIFTY options analysis application built around the principle:

**Think like an Option Seller. Generate opportunities for an Option Buyer.**

## Project principles
- NIFTY 50 and NIFTY options only.
- Historical EOD analysis; no live-market analysis.
- No automated trading or order execution.
- Acquire and use only data whose source terms and permissions allow the intended download, temporary processing, ML analysis, and retention of derived outputs.
- Zero mandatory recurring software or infrastructure subscriptions; optional B2 usage can incur provider charges.
- Reproducible analysis with recorded inputs, configurations and model versions.
- Pattern improvements require historical validation before approval.

## Technology architecture
- Frontend: React + Vite
- Backend: Python + FastAPI
- Architecture: Modular monolith
- Database: PostgreSQL
- Object storage: Backblaze B2 through its S3-compatible API (optional credentials)
- Data processing: Pandas + NumPy
- Machine learning foundation: Scikit-learn
- Testing: Pytest
- Development and validation: GitHub Actions remote CI; optional local setup

## Repository layout
- `backend/`: FastAPI application, database, storage adapter and business modules.
- `frontend/`: React web application.
- `docs/`: Architecture, database, storage, API and development documentation.
- `scripts/`: Reserved for setup, data and maintenance utilities.
- `tests/`: Cross-module integration tests.
- `storage/`: Repository placeholder only. Actual historical data must not be committed.

## Development status
Phase 0 foundation implementation is on the `phase-0-foundation` branch. It includes FastAPI health endpoints, React/Vite, PostgreSQL connectivity and migration foundation, B2 object-storage adapter, pinned data-science dependencies, tests, Render Blueprint preparation and CI validation.

See [Phase 0 checklist](docs/development/phase-0.md), [Phase 1 acquisition and audit requirements](docs/development/phase-1-acquisition-and-audit.md), [setup guide](docs/development/setup.md), [storage guide](docs/storage/README.md), and [remote validation guide](docs/development/remote-validation.md).

GitHub Actions runners and PostgreSQL services are temporary validation environments, not a persistent server, database or hosted application. Render configuration is prepared but no deployment has been made.

## Data-source compliance and temporary acquisition
Before implementing automated NSE data acquisition, review the applicable NSE terms and determine which reports and collection methods permit the intended use. Do not bypass access controls or implement collection methods prohibited by the source terms.

The planned Phase 1 workflow uses a GitHub-hosted Ubuntu runner to download approved NIFTY EOD source files into job-local temporary storage, preserve the original archive bytes during validation, calculate SHA-256 checksums and file sizes, create a manifest, audit 22 trading sessions, and feed validated data to the analysis/ML pipeline. Raw archives, extracted files, and intermediate datasets must not be committed, cached, uploaded as workflow artifacts, or copied to persistent storage. Cleanup must run unconditionally, with a maximum six-hour job retention target; the hosted runner is discarded after the job. Only permitted audit metadata and derived outputs may be retained.

**The downloader remains disabled until permission for the proposed acquisition method, temporary storage, ML processing, and derived-output retention is documented.** The Phase 1 specification is a requirement, not evidence that the 22-session download or audit has already run.

## Security
- Keep credentials and local configuration in an untracked `.env` file or deployment secret store.
- Never commit API keys, passwords, tokens, personal data or raw historical archives.
- Use `.env.example` only for placeholder variable names and safe example values.
- CI database credentials are disposable test-only values for the ephemeral PostgreSQL service.
- B2 tests use a mock client and do not require real credentials.

## License
No project license has been selected yet. Do not assume that this repository or its contents are open for unrestricted reuse until a license is chosen.
