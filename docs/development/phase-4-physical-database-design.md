# Phase 4 — Physical Database Design

**Status:** Physical persistence design prepared for review; this document does not authorize migrations or application-code changes.  
**Branch:** `phase-4-feature-engineering`  
**Scope:** Phase 4 feature-set summaries and individual feature records only.  
**Phase 3 boundary:** Existing Phase 3 tables, validation rules, ingestion pipeline and persisted source records remain unchanged.

## 1. Design decision

Use two new tables:

1. `feature_sets` — one processing summary for an Analysis Run and feature-definition version.
2. `feature_records` — one row for each individual calculated feature, subject and context window.

This separates run-level provenance from individual feature values. It supports deterministic reprocessing, version history, missingness, spot-level features and exact-contract option features without placing the complete result set in one JSON document.

The design is additive. It does not alter `analysis_runs`, `eod_ingestion_batches`, `nifty50_eod_bars` or `nifty_option_eod_bars`.

## 2. Relationship

```text
analysis_runs (existing)
    |
    | 1-to-many across feature-definition versions
    v
feature_sets (new)
    |
    | 1-to-many individual calculated outputs
    v
feature_records (new)
```

A feature set is unique for an existing Analysis Run and one immutable feature-definition version. A new definition version creates a new feature set and preserves earlier results.

## 3. Table: feature_sets

One row represents the logical feature-set lifecycle for an Analysis Run under a particular feature-definition version. Retries reuse this row; separate per-attempt history is not stored in this table.

| Column | Suggested PostgreSQL type | Null | Purpose |
|---|---|---:|---|
| id | VARCHAR(36) | No | UUID primary key |
| analysis_run_id | VARCHAR(36) | No | FK to `analysis_runs.id`, ON DELETE RESTRICT |
| feature_definition_version | VARCHAR(64) | No | Immutable feature catalogue/formula version |
| input_source_manifest | JSON | No | Canonical manifest of every Phase 3 source row used, including source hash and stable row reference |
| input_manifest_hash | VARCHAR(64) | No | SHA-256 of the canonical, deterministically sorted input-source manifest |
| index_observation_count | INTEGER | No | Number of NIFTY spot observations considered |
| option_observation_count | INTEGER | No | Number of option-contract observations considered |
| window_coverage | JSON | No | Expected/actual coverage for 1-, 5- and 22-session contexts |
| validation_summary | JSON | No | Feature-input coverage and quality summary |
| status | VARCHAR(16) | No | PENDING, RUNNING, COMPLETED or FAILED |
| error_message | TEXT | Yes | Processing-level failure explanation |
| created_at | TIMESTAMP WITH TIME ZONE | No | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | No | Last processing/update timestamp |
| completed_at | TIMESTAMP WITH TIME ZONE | Yes | Completion timestamp |

### Constraints and indexes

- Primary key: `id`.
- Foreign key: `analysis_run_id → analysis_runs.id`, with `ON DELETE RESTRICT`.
- Unique constraint: `(analysis_run_id, feature_definition_version)`.
- Check constraint: `status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')`.
- Index on `status` for operational processing queries.
- The unique constraint is the idempotency boundary for a feature set.

A feature set may be COMPLETED even when some individual features are PARTIAL or UNAVAILABLE. Those are feature-level outcomes, not necessarily a processing failure.

## 4. Table: feature_records

One row represents one feature calculation for one subject and one context. It stores numeric and categorical values in typed columns; missing/unavailable values remain SQL NULL.

| Column | Suggested PostgreSQL type | Null | Purpose |
|---|---|---:|---|
| id | VARCHAR(36) | No | UUID primary key |
| feature_set_id | VARCHAR(36) | No | FK to `feature_sets.id`, ON DELETE RESTRICT |
| feature_name | VARCHAR(128) | No | Stable feature identifier |
| subject_type | VARCHAR(16) | No | SPOT or OPTION |
| subject_key | VARCHAR(64) | No | Stable canonical subject identity used by uniqueness |
| underlying_symbol | VARCHAR(16) | Yes | NIFTY for option-level records |
| instrument_id | VARCHAR(32) | Yes | Exact option instrument identity |
| expiry | DATE | Yes | Exact option expiry |
| strike | NUMERIC(18, 4) | Yes | Exact option strike |
| option_type | VARCHAR(2) | Yes | CE or PE |
| context_window | SMALLINT | No | 0 = no window; otherwise 1, 5 or 22 |
| value_numeric | NUMERIC(38, 18) | Yes | Numeric feature value |
| value_text | TEXT | Yes | Categorical/text feature value, such as ITM/ATM/OTM |
| unit | VARCHAR(32) | Yes | Points, percent, ratio, premium rupees, etc. |
| status | VARCHAR(16) | No | AVAILABLE, PARTIAL, UNAVAILABLE or INVALID |
| expected_observation_count | INTEGER | Yes | Required observations for the feature/context |
| actual_observation_count | INTEGER | Yes | Observations actually used/available |
| first_source_date | DATE | Yes | First source observation date |
| last_source_date | DATE | Yes | Last source observation date |
| source_refs | JSON | No | Source row/batch references and provenance |
| calculation_parameters | JSON | No | Formula parameters needed to reproduce the value |
| quality_reason | TEXT | Yes | Missingness or quality explanation |
| created_at | TIMESTAMP WITH TIME ZONE | No | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | No | Last upsert timestamp |

### Subject identity

- Spot-level records use `subject_type = 'SPOT'` and `subject_key = 'SPOT'`; all option identity columns remain NULL.
- Option-level records use `subject_type = 'OPTION'`. Their subject key is a deterministic SHA-256 digest of a canonical representation of the complete identity tuple: underlying symbol, expiry, strike, option type and instrument ID.
- The complete option identity components are also stored in their own columns for inspection and filtering. The digest is only a compact uniqueness key; it does not replace those columns.
- Canonicalization must use a fixed date format and a fixed decimal representation for strike. It must not depend on locale or display formatting.

### Constraints and indexes

- Primary key: `id`.
- Foreign key: `feature_set_id → feature_sets.id`, with `ON DELETE RESTRICT`.
- Unique constraint: `(feature_set_id, feature_name, subject_key, context_window)`.
- Check constraint: `context_window IN (0, 1, 5, 22)`.
- Check constraint: `status IN ('AVAILABLE', 'PARTIAL', 'UNAVAILABLE', 'INVALID')`.
- Check constraint: `subject_type IN ('SPOT', 'OPTION')`.
- Check constraint: no more than one of `value_numeric` and `value_text` may be populated.
- SPOT rows must use the SPOT key and have NULL option identity columns.
- OPTION rows must have a non-empty instrument ID, underlying symbol, expiry, strike and CE/PE option type.
- Index on `(feature_set_id, feature_name, context_window)` for feature lookup.
- Index on `(feature_set_id, status)` for missingness/quality review.
- Index on `(feature_set_id, expiry, strike, option_type)` for option-contract filtering.

The Analysis Run already supplies Analysis Date and selected Expiry. The feature record's Analysis Run is reachable through `feature_set_id`; duplicating those parent values in every feature row is unnecessary. The exact option expiry is still stored on option-level rows because it is part of the contract identity.

## 5. Deterministic upsert and version preservation

The approved logical identity is represented physically by:

```text
feature_set_id
+ feature_name
+ subject_key
+ context_window
```

The parent feature set is uniquely identified by:

```text
analysis_run_id + feature_definition_version
```

Together, these constraints represent the approved identity: Analysis Run, feature-definition version, feature name, exact subject/contract identity where applicable, Analysis Date (inherited from the immutable Analysis Run) and context window.

Processing rules:

1. Create or retrieve the feature set using `(analysis_run_id, feature_definition_version)`.
2. Before reusing an existing feature set, compare its `input_manifest_hash` with the SHA-256 of the current canonical `input_source_manifest`. A mismatch must fail with an explicit integrity/conflict error; do not silently replace either field under the same Analysis Run and feature version.
3. Upsert each feature record using its unique identity.
4. Reprocessing the same inputs and definition version updates the same logical rows; it must not create duplicates.
5. A changed formula/catalogue requires a new feature-definition version and therefore a separate feature set. Do not overwrite or delete earlier-version results.
6. Keep feature-set lifecycle state and feature-record writes consistent. Use an outer transaction for the feature-set row/status and a database savepoint for the complete feature-record write set. On success, release the savepoint and mark the feature set `COMPLETED` in the outer transaction. On a calculation or persistence failure, roll back the savepoint (removing all feature-record writes from that attempt), set the feature set to `FAILED` with a safe error reason in the outer transaction, and commit the failure state. This preserves the failed feature-set record without leaving partial feature records or a misleading `COMPLETED` status.

The feature-definition version is immutable. A change to formulas, parameters that alter semantics, feature identity, or output interpretation requires a version increment.

## 6. Value, missingness and precision rules

- Use `value_numeric` for numeric outputs and `value_text` for categorical outputs. A record with UNAVAILABLE or INVALID status normally has no value.
- Do not store missing values as numeric zero. Zero remains a valid value where the feature definition permits it.
- `PARTIAL` means the feature definition explicitly permits a partial result; it must include expected/actual counts and a quality reason. Features whose approved definition requires complete coverage remain UNAVAILABLE when coverage is incomplete.
- Use a fixed-precision database numeric type for persisted numeric results; calculations should use decimal-safe arithmetic where appropriate. Do not round to presentation precision before persistence. Presentation rounding remains a UI/report concern.
- Store the formula parameters and relevant source references needed to reproduce the output. Do not use the JSON metadata columns as a substitute for typed identity, status, value or count columns.

## 7. Source-history and deletion policy

- Both new tables reference their parent rows with RESTRICT semantics. Historical feature results must not disappear through cascading deletion.
- Phase 3 source rows remain read-only inputs to Phase 4.
- Missing historical contract/date observations are represented through affected feature-record status, counts, dates and quality reason; do not create fake source bars or synthetic zero-valued contracts.
- A missing contract must not prevent processing of unrelated contracts or spot-level features.

## 8. Migration and implementation sequence

When implementation is separately authorized:

1. Add a new Alembic migration after the current Phase 3 migration; do not edit or rewrite migrations `0001`–`0003`.
2. Add SQLAlchemy models for the two new tables, matching the migration constraints and indexes.
3. Add tests for table creation, FK restrictions, unique identities, subject validation, context-window validation, typed values, upsert idempotency, version preservation and source-hash mismatch handling.
4. Verify the migration against the project's supported PostgreSQL database and its SQLite test configuration.
5. Implement feature calculation and persistence only after the physical schema and API contract have been reviewed.

No migration, model, API, calculation code, Phase 3 source data or production database is changed by this design document.

## 9. Items to confirm during implementation review

The following are implementation details to verify against the repository's actual database and runtime configuration before writing a migration:

- PostgreSQL server version and the SQLAlchemy/Alembic versions in the project lock/dependency files.
- Whether the project's SQLite test setup supports all selected constraints and type variants.
- UUID storage convention. This design uses the existing repository convention of `VARCHAR(36)`.
- Whether source-hash manifests need a normalized child table later. The current design stores the complete immutable row-level manifest in JSON and its canonical SHA-256 in a separate typed column; queryable per-file lineage can be normalized if a later requirement needs it.
- **Blocking feature-grain decision:** the Phase 4 specification describes daily features calculated for each historical EOD observation, but the approved logical identity and current unique key allow only one row per feature/subject/context window. Decide whether daily historical observations need an `observation_date` column included in feature-record identity, or whether only the Analysis Date's daily feature value is persisted and historical observations are calculation inputs. Do not finalize the feature-record migration until this is resolved.
- Whether feature calculations need additional typed value kinds beyond numeric and categorical text. Add a typed column only when an approved feature requires it; do not put arbitrary result payloads into JSON.

## 10. Explicit non-goals

This design does not authorize or introduce:
- Changes to Phase 3 tables, validators, normalization or ingestion.
- New data acquisition, NSE scraping, live/intraday feeds or supplementary reports.
- Seller identification, seller ranking, support/resistance, triggers, scenarios, ML labels or trading signals.
- Dashboard/UI work, broker integration, order execution, alerts, paper tracking or backtesting.
- Production migrations, deployment or production-data mutation.
