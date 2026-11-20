# NIFTY Seller Intelligence

A historical, end-of-day (EOD) NIFTY options analysis application built around the principle:

**Think like an Option Seller. Generate opportunities for an Option Buyer.**

## Project principles
- NIFTY 50 and NIFTY options only.
- Historical EOD analysis; no live-market analysis.
- No automated trading or order execution.
- Use permitted, freely accessible NSE reports and preserve original source files.
- Zero mandatory recurring software or infrastructure subscriptions.
- Reproducible analysis with recorded inputs, configurations and model versions.
- Pattern improvements require historical validation before approval.

## Technology architecture
- Frontend: React + Vite
- Backend: Python + FastAPI
- Architecture: Modular monolith
- Database: PostgreSQL
- Data processing: Pandas + NumPy
- Machine learning: Scikit-learn initially
- Testing: Pytest
- Initial operation: Local development and local storage

No cloud provider, paid market-data API, paid AI API, or paid hosting service is mandatory.

## Repository layout
- `backend/`: FastAPI application and independently organized business modules.
- `frontend/`: React web application.
- `docs/`: Architecture, database, API and development documentation.
- `scripts/`: Setup, data and maintenance utilities.
- `tests/`: Cross-module integration tests.
- `storage/`: Repository placeholder only. Actual historical data must not be committed.

## Development status
The repository currently contains the Phase 0 foundation skeleton. Application implementation and dependency selection will follow the approved development sequence.

## Data-source compliance
Before implementing automated NSE data acquisition, review the applicable NSE terms and determine which reports and collection methods permit the intended use. Do not bypass access controls or implement collection methods prohibited by the source terms.

## Security
- Keep credentials and local configuration in an untracked `.env` file.
- Never commit API keys, passwords, tokens, personal data or raw historical archives.
- Use `.env.example` only for placeholder variable names and safe example values.

## License
No project license has been selected yet. Do not assume that this repository or its contents are open for unrestricted reuse until a license is chosen.
