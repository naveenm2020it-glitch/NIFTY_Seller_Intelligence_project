# Phase 2 — Data contract and run persistence

## Archive layout
Phase 2 reads the extracted, approved Phase 1 archive from DATA_STORAGE_PATH. The root contains artifacts/manifests/fo-download-manifest.json, artifacts/manifests/nifty50-download-manifest.json and raw source directories for F&O Bhavcopy, MII Contract Master and NIFTY 50 OHLC.

Each source manifest entry must state status=DOWNLOADED, a root-relative path, byte count, SHA-256 and source URL. The resolver rejects paths outside the configured root, absent files, size/hash mismatches and invalid schemas. It never downloads from NSE.

The Phase 1 artifact uploaded to B2 is not automatically mounted by the application. For this implementation, the archive must first be extracted to the configured local archive root. B2 download/materialization is not claimed as implemented because the archived object layout and live download permissions have not been validated end-to-end.

## Contract resolution
- Analysis dates are the intersection of both Phase 1 manifests with all three source files present and checksum-valid.
- Bhavcopy must contain one TradDt matching the selected analysis date.
- NIFTY CE/PE rows are reconciled to the selected date MII Contract Master by FinInstrmId. When IDs are absent from the same-day MII snapshot, the resolver checks the nearest prior manifest-backed MII snapshot, matching the Phase 1 expiry-day audit approach.
- MII XpryDt uses seconds from 1980-01-01; StrkPric is paise. Raw source files remain unchanged.
- Expiry candidates are NIFTY CE/PE contracts present in Bhavcopy and reconciled to MII. If the nearest MII expiry has no matching Bhavcopy contracts, the next available expiry is selected and the fallback is disclosed.
- Manual expiry must be one of the available expiries.
- No cutoff-time, saved profile, analytical threshold, model parameter, option-chain snapshot or live source is introduced.

## Persistence model
The analysis_runs table is the sole Phase 2 domain table. It stores stable UUID and unique idempotency key/request hash; analysis date, selected expiry and AUTO/MANUAL mode; immutable JSON configuration snapshot; source manifest provenance and validation summary; ordered stage outcomes, lifecycle timestamps, final status and safe error text.

No user/account foreign keys are created because Phase 2 has no authentication or user entity. No automated retention/deletion job is added; records are retained until a separately approved retention policy is established. No update endpoints expose mutation of configuration snapshots or provenance.

## Run lifecycle
RUNNING transitions to READY_FOR_PROCESSING when configuration, source, checksum and schema checks pass, or FAILED when a required check fails. Stages are CONFIGURATION_VALIDATION, EXPIRY_RESOLUTION, SOURCE_RESOLUTION, INTEGRITY_VALIDATION and PROCESSING_HANDOFF. READY_FOR_PROCESSING means only that validated EOD inputs are ready for a later phase; it does not mean analytics or a trading signal has been generated.

POST /api/v1/analysis-runs requires a unique idempotency_key. Retrying the same key and payload returns the existing run; reusing a key with a different payload returns HTTP 409.

## API
- GET /api/v1/configuration/analysis-dates — available audited dates.
- GET /api/v1/configuration/resolve?analysis_date=YYYY-MM-DD[&expiry=YYYY-MM-DD] — read-only preview of already-staged local archive metadata; no network download or analysis run starts.
- POST /api/v1/analysis-runs — explicit Start Analysis action.
- GET /api/v1/analysis-runs/{run_id} — run lifecycle details.

The request accepts analysis date, optional manual expiry and idempotency key only. Presentation preferences are not yet defined and are not accepted. Analytical rules are not user-editable.

## Operational boundary
Run from backend working directory with DATA_STORAGE_PATH pointing at the extracted Phase 1 archive root. The configured archive is read-only. NSE acquisition, B2 archive materialization, analytics, ML, scenarios, order execution, background workers, production deployment and persistent cloud infrastructure remain outside this implementation.
