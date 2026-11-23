# Phase 3 — Data Contract

## API boundary
Phase 2 remains responsible for Analysis Date, automatic/manual Expiry selection and idempotent AnalysisRun creation. Phase 3 consumes a persisted run. Its inputs cannot independently override the immutable run date or expiry. User input remains Analysis Date and Expiry only; cutoff-time input is forbidden.

## Source manifest contract
The processing pipeline reuses the Phase 2 archive resolver. For the selected date it requires manifest entries for F&O Bhavcopy, same-day MII Contract Master and NIFTY 50 OHLC. A previous-session MII manifest object is also included when contract identity resolution needs it. Each source must be DOWNLOADED and contain a root-relative path, byte count and SHA-256. Source path traversal, missing files, schema mismatch, size mismatch or digest mismatch rejects processing. All parsing is read-only.

## Normalized index record
One NIFTY 50 bar per trading date: trade_date, symbol, open, high, low, close, source_sha256 and source_filename. Exactly one NIFTY 50 row is required and its date and OHLC relationships must validate.

## Normalized option record
Only Bhavcopy rows with TckrSymb=NIFTY and OptnTp in CE/PE are in scope. The persisted selected-expiry dataset contains:
- trade_date, symbol, instrument_id, expiry, strike and option_type
- open, high, low, close, volume, open_interest and underlying_close
- contract_source (same-day or previous-session MII)
- source_sha256, source_filename and ingestion_batch_id

MII XpryDt is seconds from 1980-01-01; MII StrkPric is paise and is divided by 100 to normalize rupees. Bhavcopy strike is already expressed in rupees. Instrument ID, expiry, strike and option type must match. Same-day MII is preferred; previous-session MII is consulted only for a missing instrument ID.

Zero-volume contracts are retained and their zero open/high/low values are preserved. Traded rows require positive OHLC and coherent high/low. Volume and OI must be numeric and non-negative. Underlying close must equal the selected day's official NIFTY 50 close. Invalid/missing numeric values are rejected, never silently filled with zero.

## Idempotency and persistence
One ingestion batch per analysis run. Its source_set_hash is derived from sorted resolved source provenance. Repeating a completed batch with identical hashes returns it without duplicating rows. A conflicting source hash is a conflict, never an in-place overwrite. A unique (trade_date, instrument_id) constraint prevents duplicate normalized option contracts. Normalized rows and successful state are transactionally committed. Failed database writes roll back normalized rows, then record a safe failed batch/run state.

## Storage boundaries
Original NSE ZIP/GZ/CSV reports are never modified or stored in PostgreSQL. Phase 1 manifests and SHA-256 establish provenance. PostgreSQL stores normalized EOD facts and ingestion metadata. Existing B2 S3-compatible adapter remains optional; Phase 3 does not require credentials, create resources or automatically fetch source data from NSE or B2.

## Out of scope
No live data, NSE acquisition, cutoff-time input, broker APIs, order execution, features/indicators, analytics, scenarios, ML, dashboard enhancements, feedback learning or production deployment.
