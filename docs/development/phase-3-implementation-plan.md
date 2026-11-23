# Phase 3 — Storage & Data Processing Implementation Plan

## Baseline and reuse
Phase 0–2 are complete and remain unchanged. Phase 3 builds on the Phase 2 FastAPI modular monolith, PostgreSQL/SQLAlchemy, Alembic, manifest-backed archive resolver and optional B2 adapter. Existing AnalysisRun and source provenance are reused. No parallel orchestration service is introduced.

## Processing contract
Processing consumes a persisted AnalysisRun. Its immutable Analysis Date and selected Expiry remain the only user configuration inputs. NIFTY 50 index EOD and NIFTY CE/PE options only. Live-market feeds, broker connectivity, order execution, cutoff-time input, automatic NSE acquisition and signal generation are explicitly excluded.

## Storage
- Raw ZIP/GZ/CSV source bytes remain unchanged, outside Git and PostgreSQL.
- Read only files enumerated by Phase 1 manifests; verify path containment, download status, byte size and SHA-256 before parsing.
- PostgreSQL stores typed NIFTY 50 daily bars, selected-expiry NIFTY option bars and an ingestion-batch audit record.
- Source filename/hash, contract-resolution source, trade date, expiry, row counts and validation summary remain traceable.
- Existing local storage / optional B2 adapter is reused; no new paid storage or always-on infrastructure.

## Processing stages
1. Validate AnalysisRun exists and is in READY_FOR_PROCESSING or retryable PROCESSING_FAILED state.
2. Resolve manifest source set for the selected day using Phase 2 archive resolver.
3. Verify manifest metadata and original file bytes before reading.
4. Parse Bhavcopy ZIP, MII GZ and NIFTY 50 index CSV read-only.
5. Normalize NIFTY 50 OHLC and NIFTY option IDs, expiry, strike, CE/PE, OHLC, volume, OI and underlying close.
6. Reconcile same-day MII first; use previous-session MII only for absent IDs, retaining that provenance.
7. Validate required schema, trading dates, contract metadata, duplicates, finite/nonnegative values, OHLC relationships, zero-volume semantics and underlying-close consistency.
8. Persist normalized rows and batch metadata transactionally.
9. Mark run PROCESSED only after successful commit.
10. On failure, rollback normalized rows, persist a safe failure state and allow retry without accepting conflicting verified source changes.

## API contract
- POST /api/v1/analysis-runs/{run_id}/process explicitly starts processing.
- GET /api/v1/analysis-runs/{run_id}/processing returns the ingestion status and audit record.
- GET /api/v1/analysis-runs/{run_id}/processed-data returns normalized records.
GET/preview operations do not trigger ingestion. Existing Phase 2 APIs remain intact. Request models do not add cutoff time.

## Persistence and idempotency
Alembic revision 0003 adds eod_ingestion_batches, nifty50_eod_bars and nifty_option_eod_bars. Unique trade_date/instrument_id constraint plus source hash comparisons prevent duplicate or conflicting rows. Completed same-source batch retry is idempotent. Failure marker is used only when source verification fails before a trustworthy source-set can be constructed; the first subsequent verified source set binds the retry. Failures after source verification retain immutable source-set comparison.

## Tests
- Unit tests cover numeric validation, option types, MII epoch/strike conversions, contract mismatch and zero-volume rows.
- Synthetic manifest-backed integration tests exercise explicit processing, idempotent retry, failed source validation and recovery, persistence/read APIs and immutable source bytes.
- PostgreSQL CI covers migration upgrade, downgrade and re-upgrade.
- Existing Phase 0–2 tests and frontend build remain part of CI.
- Real Phase 1 B2 archive smoke remains an explicit opt-in job to avoid repeated Class B reads; it was not executed in this implementation run because the earlier account response reported the Class B cap exceeded.

## Acceptance gates
Backend test suite and frontend build pass; migration round-trip passes; processing is explicit; raw files remain unchanged; all rows are provenance-linked; retry and duplicate semantics are covered; no secrets/raw market files are committed; no production deployment or changes to main.
