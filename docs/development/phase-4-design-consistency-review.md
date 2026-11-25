# Phase 4 — Cross-Document Design Consistency Review

**Review status:** Completed, with one blocking owner decision  
**Branch:** `phase-4-feature-engineering`  
**Review scope:** Feature specification, physical database design, API contract and inspected Phase 3 persistence/API implementation  
**Implementation status:** No application code, database model, migration, data or deployment changes were made.

## 1. Overall result

The two-table persistence model and the proposed API boundary are broadly compatible with the approved Phase 4 feature specification and the inspected Phase 3 architecture. The review found two documentation gaps that have now been clarified:

1. The physical feature-set schema now explicitly stores the complete canonical row-level input manifest and its SHA-256 hash in separate fields.
2. The persistence transaction now specifies how to preserve a FAILED feature-set status while rolling back incomplete feature-record writes.

One blocking design ambiguity remains: the approved feature specification describes daily features for each historical EOD observation, but the logical feature-record identity and proposed unique key allow only one record per feature, subject and context window. The documents cannot be considered implementation-ready until the owner decides whether historical daily feature observations are persisted individually or only used internally to calculate the Analysis Date's feature snapshot.

## 2. Compatibility checks passed

### 2.1 Phase 3 integration boundary

- The API contract uses the existing Analysis Run's Analysis Date and selected Expiry; it introduces no new user-supplied analysis inputs.
- Phase 4 requires the Analysis Run to be `PROCESSED` and its Phase 3 ingestion batch to be `COMPLETED`.
- The existing Phase 3 `processed-data` route returns Analysis Date rows only. The Phase 4 design correctly requires direct, read-only database access for historical windows.
- The feature service is not permitted to read archive files, acquire new reports, or modify Phase 3 records.
- The inspected Phase 3 option table stores exact contract identity and source provenance, and has a persisted row ID. The index row is identified by trade date and carries its source hash.

### 2.2 Feature-set and feature-record identity

- The parent unique key `(analysis_run_id, feature_definition_version)` represents the Analysis Run and immutable feature-definition version.
- The child unique key `(feature_set_id, feature_name, subject_key, context_window)` represents feature name, subject/contract identity and context window.
- Analysis Date is inherited from the immutable Analysis Run, so it need not be duplicated in each feature row.
- The canonical SPOT key and SHA-256 OPTION subject key avoid SQL NULL uniqueness ambiguity.
- Exact option identity remains available in typed columns for inspection and filtering.
- New feature-definition versions remain separately identifiable; older results are preserved.

### 2.3 Status and missingness

- Feature-level `AVAILABLE`, `PARTIAL`, `UNAVAILABLE` and `INVALID` statuses are distinct from feature-set processing status.
- A feature set may complete with unavailable/partial feature records.
- Missing observations are not stored as numeric zero.
- The API exposes stored feature values and statuses; GET endpoints do not calculate or mutate results.
- The API's 404/409/422 boundaries are compatible with the processing readiness and conflict rules.

### 2.4 Source lineage and manifest integrity

- The input manifest covers all Phase 3 source rows actually used across historical dates, not just the current run's one-day batch.
- Stable row references can use the NIFTY 50 trade date and the option row's persisted ID, trade date, instrument ID and ingestion-batch ID, together with source hashes.
- The API and database documents now use the same fields: `input_source_manifest` and `input_manifest_hash`.
- Reusing a feature set with a different input-manifest hash is a conflict, not an overwrite.

### 2.5 Transaction and failure handling

The API and database documents now use a consistent savepoint strategy:

1. Keep the feature-set lifecycle/status in an outer transaction.
2. Write the complete feature-record set inside a savepoint.
3. On success, release the savepoint and commit the feature records and COMPLETED status together.
4. On processing failure, roll back the savepoint, set FAILED plus a safe error reason in the outer transaction, and commit that failure state.

This avoids both partial feature records and loss of the FAILED feature-set record. A source-manifest conflict must not alter an existing feature set.

### 2.6 API security

The current inspected FastAPI routes do not expose a reusable authentication/authorization dependency. The API contract explicitly records this as a production-exposure blocker. No authentication implementation is claimed or assumed.

## 3. Blocking issue — daily historical feature record grain

The feature specification states that approved daily features are calculated for the available EOD observations represented by the 1-, 5- and 22-session contexts. It also requires Williams %R to be calculated separately at each historical observation using only information available up to that date.

However, the current physical unique key is:

`(feature_set_id, feature_name, subject_key, context_window)`

That key permits only one value for a given feature/subject/context. The logical identity in Section 10.11 likewise does not include an observation date. The API feature-record response also has no `observation_date` field.

Consequently, the current design cannot unambiguously persist a time series of daily historical feature values for one contract/subject within a 5- or 22-session context. The source specification and persistence identity currently describe different record grains.

### Owner decision required

Choose the intended persistence behavior:

**Option A — Persist every historical daily feature observation.**  
Add an observation-date dimension to the logical feature record, physical feature-record schema and API response. Include it in the unique identity for daily observations. Window-level summaries remain separately identifiable.

**Option B — Persist only the Analysis Date's feature snapshot and window summaries.**  
Calculate historical daily intermediate values as needed, but persist only the Analysis Date's daily feature values and approved 1/5/22 window-level outputs. Historical per-date feature rows are not exposed or retained as individual feature records.

The current specification's wording ("for each available EOD bar" and per-observation Williams %R) points toward Option A, but Option A extends the already-approved logical identity. That extension must be explicitly approved before schema design is finalized. Do not silently choose either option in implementation.

## 4. Other implementation checks still required

These are verification items, not contradictions:

- Confirm PostgreSQL server version and SQLAlchemy/Alembic behavior for the proposed constraints and savepoint handling.
- Confirm SQLite test configuration supports the same logical constraints and transaction behavior.
- Define the actual immutable feature-definition version string before implementation.
- Confirm the authentication/authorization model and operator role for the processing command.
- Define the exact feature-name catalogue and distinguish daily observation features from window-summary features once the record-grain decision is made.
- Confirm whether a durable worker is needed only if real processing duration/request timeouts justify it; the initial design remains synchronous.

## 5. Files updated during this review

- `phase-4-physical-database-design.md`: clarified feature-set lifecycle semantics, separate manifest/hash fields, savepoint failure persistence and the daily-feature-grain blocker.
- `phase-4-api-contract.md`: aligned source-row provenance and manifest fields, clarified transaction behavior and recorded the daily-feature-grain blocker.
- `phase-4-feature-engineering-spec.md`: retains the approved feature definitions and logical identity; no formula or feature approval was changed.

## 6. Review conclusion

The physical database and API designs are consistent for feature-set lifecycle, versioning, exact contract identity, source lineage, missingness and read-only retrieval after the clarifications above.

**Phase 4 implementation must remain on hold until the daily historical feature record grain is explicitly decided.** After that decision, update the logical identity, physical unique key and API response together, then conduct the final schema/API approval before creating migrations or application code.
