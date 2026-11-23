# Phase 3 — Data Contract

## API and inputs
Phase 3 consumes an existing Phase 2 AnalysisRun. Its Analysis Date and selected Expiry are immutable inputs. User inputs remain Analysis Date and Expiry only. No cutoff time, live data or automatic exchange download is permitted.

Endpoints:
- POST /api/v1/analysis-runs/{run_id}/process
- GET /api/v1/analysis-runs/{run_id}/processing
- GET /api/v1/analysis-runs/{run_id}/processed-data

## Verified source reports
The Phase 2 resolver identifies F&O Bhavcopy, same-day MII contract master and NIFTY 50 index EOD CSV from Phase 1 manifests, checking root-contained paths, DOWNLOADED status, bytes and SHA-256. If contract IDs are missing from same-day MII, the resolver's previous-session fallback is retained and marked. Parsing never writes to source files.

## NIFTY 50 index record
Exactly one NIFTY 50 index row per selected trade date, normalized to trade_date, symbol, open, high, low, close and source provenance.

## NIFTY option record
NIFTY symbol and CE/PE only. Each normalized row contains:
- trade_date, instrument_id, expiry, strike, option_type
- open, high, low, close, volume, open_interest, underlying_close
- contract_source, source_sha256, source_filename, ingestion_batch_id

MII expiry seconds are converted from 1980-01-01. MII strike price in paise is divided by 100 to rupees. Bhavcopy strike is rupees. Instrument ID, expiry, strike and option type must match exactly within the numeric precision used by the audited archive.

Zero-volume records are retained and source zero OHLC values are not replaced. Traded rows require finite positive OHLC with coherent high/low. Negative volume/OI, malformed numeric fields, duplicate instrument IDs, mismatched contracts or underlying close differing from the official NIFTY 50 close reject processing.

## Persistence and provenance
PostgreSQL tables:
- eod_ingestion_batches: one batch per AnalysisRun, state, selected expiry, source-set SHA-256, source manifests, counts, validation summary, safe failure and timestamps.
- nifty50_eod_bars: one index OHLC bar per trade date.
- nifty_option_eod_bars: normalized selected-expiry EOD contract rows, unique by trade_date/instrument_id.

Matching completed retries are no-ops. Conflicting source hashes or normalized values reject rather than overwrite. Normalized rows and success states commit as one transaction. Failed persistence rolls back market rows and stores failure status separately.

Raw archive files are not copied into PostgreSQL or Git. B2 remains optional and the real Phase 1 archive integration is opt-in in CI.
