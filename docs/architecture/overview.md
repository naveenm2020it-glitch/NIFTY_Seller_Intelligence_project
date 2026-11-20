# Architecture Overview

## Selected architecture
React + Vite frontend communicating with a Python + FastAPI modular monolith through REST/JSON APIs.

The backend is one deployable application. Its modules have distinct responsibilities and interfaces; they are not separate services.

## Backend module boundaries
- `user_config`: analysis date, intended cutoff time, expiry selection and user preferences.
- `nse_data`: acquisition of permitted NSE reports and source metadata.
- `data_validation`: file integrity, required fields, duplicate and completeness checks.
- `data_processing`: cleaning, normalization and historical data preparation.
- `feature_engineering`: session-based features for 1, 5 and 22 trading sessions.
- `analytics`: eight analytical engines, as defined by the approved functional specification.
- `scenarios`: eight-scenario decision engine.
- `ml`: four separately versioned ML models.
- `reports`: generated analysis reports and export.
- `feedback_learning`: feedback records, pattern history, candidate optimization and validation lifecycle.

## Data boundaries
1. Preserve original report files unchanged.
2. Validate source files before processing.
3. Store structured records and analysis metadata in PostgreSQL.
4. Store local raw/processed files outside version control.
5. Record analysis inputs, cutoff, expiry, source provenance and software/model versions for reproducibility.

## Operating constraints
- No mandatory paid hosting, database, storage, market-data or AI service.
- Initial execution is local.
- No live-market analysis or automatic trade execution.
- NSE acquisition methods must comply with applicable source terms.
- Approved production patterns are not replaced without validation and approval.

## Deferred decisions
Cloud hosting, cloud object storage, background job infrastructure, deployment automation and production authentication details are deferred until a demonstrated need exists.
