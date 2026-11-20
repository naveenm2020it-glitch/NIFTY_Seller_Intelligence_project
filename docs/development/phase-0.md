# Phase 0 — Foundation Setup

## Confirmed decisions
- Repository: NIFTY_Seller_Intelligence_project
- Frontend: React + Vite
- Backend: Python + FastAPI
- Architecture: Modular monolith
- Database: PostgreSQL
- Data analysis: Pandas + NumPy
- ML: Scikit-learn initially
- Testing: Pytest
- Initial operation: Local development
- Cost principle: Zero mandatory recurring software or infrastructure subscriptions

## Phase 0 sequence
1. Repository creation and verification — completed.
2. Architecture and folder design — completed.
3. Create repository skeleton — in progress.
4. Establish Python virtual environment and FastAPI application.
5. Establish React + Vite dependencies and development workflow.
6. Configure local PostgreSQL and migrations.
7. Configure local environment variables and storage paths.
8. Implement health-check endpoints and basic tests.
9. Complete setup documentation and verify clean local setup.

## Not included in this phase
- NSE report collection implementation.
- Analytical engine implementation.
- Scenario decision logic.
- ML training.
- Cloud deployment or paid service integration.

## Safety and data handling
Do not commit raw NSE reports, historical datasets, secrets, database files or trained model artifacts. Confirm permitted data acquisition methods before automating downloads.
