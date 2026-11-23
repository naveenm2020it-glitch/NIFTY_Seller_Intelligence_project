# Phase 3 — Storage & Data Processing Implementation Plan

## Baseline
- Branch created from main commit 0713cc8b758877d7d11c76f2ff3bf2efe0b28c2c.
- Phase 0, Phase 1 and Phase 2 remain complete and unchanged.
- Reuse the Phase 2 manifest-backed source resolver, B2 adapter, AnalysisRun persistence model, SQLAlchemy Base/session and Alembic migration chain.
- Do not alter original NSE source bytes.

## Processing contract
- Input is an existing analysis_run selected by its analysis_date and selected_expiry; user inputs remain Analysis Date and Expiry only.
- Restrict records to NIFTY 50 index and NIFTY CE/PE options.
- Read only files already enumerated by Phase 1 manifests and verified by size and SHA-256.
- No NSE downloads, live feeds, cutoff-time input, broker connectivity or order placement.
- Normalize instrument ID, expiry, strike, option type, OHLC, volume, open interest, underlying and trade date into explicit typed fields, retaining source traceability.
- Reconcile option contracts to MII using exact ID, expiry, strike and CE/PE; reuse previous-session fallback only where required and record its provenance.
- Preserve zero-volume rows; enforce numeric, OHLC, nonnegative volume/OI and underlying-vs-index-close checks. Reject irreconcilable rows; never silently coerce invalid market values to zero.

## Persistence
- Add versioned Alembic migration with normalized daily index bars, normalized NIFTY option EOD bars, and ingestion batch metadata.
- Unique keys make ingestion idempotent. Matching re-run is a no-op; conflicting content hash for the same source/session is an explicit conflict.
- Persist batch status, run linkage, source manifest hashes, row counts, validation summary, timestamps and safe failure reason.
- Use transactional writes per session/batch, rollback on failure, and update AnalysisRun lifecycle only after successful persistence.
- Store large raw files in existing source archive/B2. Do not duplicate raw files in PostgreSQL.

## Processing stages
1. Validate AnalysisRun is READY_FOR_PROCESSING.
2. Resolve selected session manifest-backed source file set.
3. Reverify archive root containment, source status, file size and SHA-256.
4. Parse ZIP/GZ/CSV without writing to or mutating source files.
5. Normalize index and NIFTY option datasets.
6. Reconcile instrument IDs against MII with previous-session fallback.
7. Run schema, completeness, duplicate, OHLC, volume/OI, expiry/strike/type and underlying-close validations.
8. Persist ingestion batch and normalized rows atomically.
9. Mark batch and run status with precise stage outcomes and provenance.
10. On failure, rollback normalized data, persist safe FAILED batch/run state, and allow deterministic retry with the same approved source hashes.

## APIs
- Preserve all Phase 2 endpoints and payload contracts.
- Add explicit processing action for a previously created run, plus read-only batch/status and processed-data summaries.
- Do not trigger processing on preview or GET.
- Keep extra=forbid on request models and do not add cutoff-time fields.

## Testing
- Unit tests for parsers, normalization, validation, contract mapping, checksums, path traversal, malformed ZIP/GZ/CSV and deterministic IDs.
- Database integration tests for migration, uniqueness, atomic rollback, retries and status persistence.
- Historical fixture tests shaped from Phase 1 schemas, using minimized synthetic content (never commit archive market data).
- Opt-in CI integration test downloads verified B2 archive using existing credential-gated path; ordinary PR CI remains runnable without B2 secrets.
- Existing Phase 0–2 tests and frontend build remain green.

## Operational safeguards
- B2 remains optional; no new paid service, persistent database or recurring infrastructure.
- No production deployment.
- No raw market data or secrets in Git.
- No indicators, feature engineering, scenarios, ML or feedback learning in Phase 3.

## Acceptance gates
- Migration upgrades and downgrades cleanly in disposable PostgreSQL.
- Existing Phase 0–2 tests pass.
- Valid historical session ingests deterministically and is traceable to at least three manifest source records.
- Repeat ingestion cannot duplicate records.
- Invalid, corrupt or mismatched data is rejected with actionable safe diagnostics.
- Failed transactions leave no partial normalized rows.
- Backend tests, frontend build and all new CI jobs pass.
- README, data contract, architecture, tests and Phase 3 closeout are updated.
- PR targets main; no merge or deployment without explicit approval.