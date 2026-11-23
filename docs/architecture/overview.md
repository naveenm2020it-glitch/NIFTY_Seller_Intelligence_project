# Architecture Overview

## Selected architecture
React + Vite frontend communicating with a Python + FastAPI modular monolith through REST/JSON APIs.

The backend is one deployable application. Its modules have distinct responsibilities and interfaces; they are not separate services.

## Backend module boundaries
- `user_config`: analysis date, intended cutoff time, expiry selection and user preferences.
- `nse_data`: acquisition of permitted NSE reports and source metadata.
- `data_validation`: source integrity, schema, contract, OHLC, volume/OI and underlying-close validation (Phase 3).
- `data_processing`: manifest-backed historical normalization and transactional EOD persistence (Phase 3).
- `feature_engineering`: session-based features for 1, 5 and 22 trading sessions.
- `analytics`: eight analytical engines, as defined by the approved functional specification.
- `scenarios`: eight-scenario decision engine.
- `ml`: four separately versioned ML models.
- `reports`: generated analysis reports and export.
- `feedback_learning`: feedback records, pattern history, candidate optimization and validation lifecycle.
- `storage`: Backblaze B2 object-storage adapter using the S3-compatible API.

## Data boundaries
1. Preserve original report files unchanged.
2. Validate source files before processing.
3. Store structured records and analysis metadata in PostgreSQL.
4. Store raw source archives in a configured B2 bucket when storage is enabled; keep local working files outside version control.
5. Record analysis inputs, cutoff, expiry, source provenance and software/model versions for reproducibility.

## Operating constraints
- No mandatory paid hosting, database, storage, market-data or AI service.
- Initial execution is local.
- No live-market analysis or automatic trade execution.
- NSE acquisition methods must comply with applicable source terms.
- Approved production patterns are not replaced without validation and approval.

## Deployment boundary
A Render Blueprint is checked in as an optional deployment definition. The API service declares the free compute plan, automatic deploy is disabled, and the static frontend has no compute plan. No Render service, persistent database or production environment has been created. Actual availability and provider pricing must be checked before any deployment.

## Deferred decisions
Persistent cloud database provisioning, background job infrastructure, production authentication and data-ingestion scheduling are deferred until their requirements are available. The B2 adapter and CI bucket-connectivity check are configured; live file upload, download and delete behavior remains to be validated when those operations are implemented in a later phase.
