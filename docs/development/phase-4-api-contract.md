# Phase 4 — Feature Processing and Read-Only API Contract

**Status:** API and processing-boundary design prepared for review; no route, service, schema, migration or application-code changes are authorized by this document.  
**Branch:** `phase-4-feature-engineering`  
**Depends on:** `phase-3-data-contract.md`, `phase-4-feature-engineering-spec.md` and `phase-4-physical-database-design.md`.

## 1. Design decisions

Phase 4 will have:

1. A backend feature-engineering service that reads persisted Phase 3 records directly through the database layer.
2. One explicit processing command endpoint to calculate/persist a versioned feature set for an existing Analysis Run.
3. GET-only endpoints for reading feature-set summaries and feature records.
4. No new user-supplied analysis inputs. Analysis Date and selected Expiry come only from the existing Analysis Run. The active feature-definition version is controlled by the backend.

The result-retrieval API is read-only. The separate POST endpoint is an operational command, not a data-retrieval endpoint. It does not accept formulas, thresholds, dates, expiries, strike selections or arbitrary calculation parameters from the caller.

## 2. Existing Phase 3 integration facts

The current backend exposes these Phase 3 routes under `/api/v1`:

- `POST /analysis-runs/{run_id}/process`
- `GET /analysis-runs/{run_id}/processing`
- `GET /analysis-runs/{run_id}/processed-data`

The Phase 3 processing service persists a completed ingestion batch, NIFTY 50 EOD bars and selected-expiry option EOD rows. The current `processed-data` endpoint returns the Analysis Date's rows only; it is not a historical-window endpoint.

Therefore, Phase 4 must **not** call `processed-data` and assume it contains 5/22-session history. The feature service must read the persisted Phase 3 database models directly and select historical observations by validated trade date and exact contract identity. It must not parse archive files, acquire new reports or modify Phase 3 rows.

The existing Phase 3 `AnalysisRun` status and its `EodIngestionBatch` status are the readiness gates. Phase 4 processing is allowed only when the requested run exists, the run is `PROCESSED`, and its ingestion batch is `COMPLETED`.

## 3. Historical input selection

### 3.1 Analysis context

- Read Analysis Date and selected Expiry from the existing Analysis Run.
- Build the ordered 1/5/22 session contexts from persisted NIFTY 50 EOD trade dates on or before the Analysis Date.
- The Analysis Date is included in each context.
- Use the latest N available validated spot observations; report actual count and first/last dates when fewer than N exist.
- Do not infer sessions by subtracting calendar days.

### 3.2 Spot features

Read the NIFTY 50 EOD bars for the selected context dates. Preserve each source row's trade date and source hash. A missing index observation reduces the available session context; do not fabricate a row or fill it.

### 3.3 Option features

- Select the contracts available for the Analysis Date and the Analysis Run's selected Expiry.
- For each contract, retrieve historical rows only when the full exact identity matches: underlying symbol, expiry, strike, option type and instrument ID.
- Match option observations to the spot context dates. A missing contract/date is a missing observation, not zero.
- Never bridge a missing date, substitute another strike/expiry/instrument, or combine contracts.
- If prior Analysis Runs selected different expiries, the required historical contract rows may not exist in Phase 3 storage. Mark the affected feature/window unavailable or partial according to its approved feature definition; do not acquire missing history automatically.
- A missing option history for one contract must not stop spot features or other contracts from being calculated.

### 3.4 Source lineage and immutable inputs

The feature-set input manifest must cover every Phase 3 source row actually used by the feature calculations across all selected dates, not merely the current Analysis Run's one-day ingestion batch. It must include the relevant index and option source hashes and stable row identifiers/provenance.

Compute a canonical input-manifest hash from the sorted, deterministic source references. Persist both the manifest and its hash in `feature_sets`. Reprocessing the same Analysis Run and feature-definition version with a different historical input manifest must fail with a conflict; do not silently rewrite the inputs behind an existing result. A corrected or expanded source history must be represented by a new Analysis Run under the existing Phase 3 source-governance rules.

## 4. Processing command

### Endpoint

```http
POST /api/v1/analysis-runs/{run_id}/features/process
```

Request body: none.

The caller does not choose Analysis Date, Expiry, feature-definition version, windows, formulas or thresholds. The backend obtains Analysis Date and Expiry from the Analysis Run and uses the active feature-definition version configured in the application.

### Processing sequence

1. Load and validate the Analysis Run.
2. Require `AnalysisRun.status = PROCESSED`.
3. Require the associated Phase 3 ingestion batch to exist and have `status = COMPLETED`.
4. Acquire a database-level lock for the Analysis Run to serialize concurrent processing requests for the same run.
5. Resolve the active feature-definition version and select the required historical spot and exact-contract observations.
6. Build and hash the complete input-source manifest.
7. Create or retrieve the feature set using the unique key `(analysis_run_id, feature_definition_version)`.
8. If an existing completed feature set has the same input-manifest hash, return it as an idempotent no-op.
9. If the existing feature set has a different input-manifest hash, return a conflict; do not overwrite it.
10. Calculate features using the approved deterministic definitions and persist individual records using the unique feature-record identity.
11. Mark the feature set `COMPLETED` only after all expected feature records have been persisted successfully.

The first implementation should execute this command synchronously in the API request using a single controlled database transaction for feature-set/record persistence. This avoids introducing an unconfigured queue or an in-process background task that could be lost on restart. If real workload or request timeouts later demonstrate the need, introduce a durable worker/queue as a separately reviewed infrastructure change; do not pretend FastAPI in-process background tasks are durable.

A completed feature set may contain individual `PARTIAL` or `UNAVAILABLE` records. Those are valid feature outcomes and do not make the whole feature set fail. Mark the feature set `FAILED` only for a processing-level failure that prevents a consistent complete feature-record write.

### Successful response

HTTP 200 for an already completed idempotent result; HTTP 201 when a new feature set is created.

```json
{
  "feature_set_id": "uuid",
  "analysis_run_id": "uuid",
  "analysis_date": "YYYY-MM-DD",
  "selected_expiry": "YYYY-MM-DD",
  "feature_definition_version": "phase4-v1",
  "status": "COMPLETED",
  "input_manifest_hash": "sha256",
  "feature_record_count": 0,
  "status_counts": {
    "AVAILABLE": 0,
    "PARTIAL": 0,
    "UNAVAILABLE": 0,
    "INVALID": 0
  },
  "window_coverage": {},
  "created_at": "ISO-8601",
  "completed_at": "ISO-8601"
}
```

The example values are schema illustrations, not actual run results or approved feature counts. The version string is illustrative; the implementation must define and pin the actual initial version before coding.

### Processing errors

| HTTP | Condition |
|---|---|
| 404 | Analysis Run does not exist |
| 409 | Run is not PROCESSED; Phase 3 batch is absent/incomplete; source manifest conflicts; concurrent state conflict |
| 422 | Phase 3 input integrity/validation is invalid for this run or a deterministic feature calculation cannot be completed at processing level |
| 500 | Unexpected internal processing/persistence failure |

Do not return stack traces, SQL, filesystem paths or secrets to API clients. Preserve a safe error reason in the feature-set/run operational state and server logs.

## 5. Read-only API

All endpoints in this section are GET-only. They do not calculate, mutate, retry, delete or regenerate feature results.

### 5.1 List feature-set versions for an Analysis Run

```http
GET /api/v1/analysis-runs/{run_id}/feature-sets
```

Returns the feature-set summaries for the run, ordered by creation time. This makes earlier feature-definition versions discoverable and preserves history.

Response shape:

```json
{
  "analysis_run_id": "uuid",
  "feature_sets": [
    {
      "feature_set_id": "uuid",
      "feature_definition_version": "phase4-v1",
      "status": "COMPLETED",
      "input_manifest_hash": "sha256",
      "feature_record_count": 0,
      "status_counts": {},
      "created_at": "ISO-8601",
      "completed_at": "ISO-8601"
    }
  ]
}
```

### 5.2 Read one feature-set summary

```http
GET /api/v1/analysis-runs/{run_id}/feature-sets/{feature_set_id}
```

Returns the feature-set summary, Analysis Date/selected Expiry inherited from the Analysis Run, feature-definition version, input manifest/hash, coverage summary, validation summary, status and timestamps. The feature set must belong to the supplied Analysis Run.

### 5.3 Read feature records

```http
GET /api/v1/analysis-runs/{run_id}/feature-sets/{feature_set_id}/features
```

Supported optional query filters:

| Parameter | Meaning |
|---|---|
| `feature_name` | Exact stable feature identifier |
| `subject_type` | `SPOT` or `OPTION` |
| `expiry` | Exact option expiry |
| `strike` | Exact option strike |
| `option_type` | `CE` or `PE` |
| `window` | `0`, `1`, `5` or `22`; 0 means no context window |
| `status` | `AVAILABLE`, `PARTIAL`, `UNAVAILABLE` or `INVALID` |
| `limit` | Page size, default 100, maximum 500 |
| `offset` | Zero-based offset, default 0 |

The API must validate filter values and reject invalid combinations. For example, option-specific filters must not be used with a SPOT-only filter. Results must have deterministic ordering by feature name, subject type, subject key and context window.

Feature-record response shape:

```json
{
  "analysis_run_id": "uuid",
  "feature_set_id": "uuid",
  "feature_definition_version": "phase4-v1",
  "total": 0,
  "limit": 100,
  "offset": 0,
  "features": [
    {
      "feature_record_id": "uuid",
      "feature_name": "stable_feature_identifier",
      "subject_type": "OPTION",
      "subject": {
        "underlying_symbol": "NIFTY",
        "instrument_id": "instrument-id",
        "expiry": "YYYY-MM-DD",
        "strike": 0,
        "option_type": "CE"
      },
      "context_window": 5,
      "value_numeric": null,
      "value_text": null,
      "unit": null,
      "status": "UNAVAILABLE",
      "expected_observation_count": 5,
      "actual_observation_count": 0,
      "first_source_date": null,
      "last_source_date": null,
      "source_refs": [],
      "calculation_parameters": {},
      "quality_reason": "reason"
    }
  ]
}
```

The example is a response-shape illustration only. The API must return the actual feature value/status and source metadata stored in the database; it must not synthesize values or recalculate them while serving GET requests.

### 5.4 Readiness and empty-result behavior

- Unknown Analysis Run: 404.
- Unknown feature set, or feature set belonging to another Analysis Run: 404.
- Feature set still PENDING/RUNNING: 409 with a safe status detail; do not return a misleading empty completed result.
- Feature set FAILED: return its safe failure summary through the summary endpoint; feature-record retrieval returns 409 unless partial persisted records are explicitly supported by the final transaction design.
- Completed feature set with no matching filters: 200 with an empty `features` list and `total = 0`.

## 6. API access control and current security gap

The inspected current FastAPI routes do not show an authentication or per-user authorization dependency. The existing analysis-run and Phase 3 endpoints therefore do not provide a reusable access-control contract in the inspected code.

Before exposing Phase 4 endpoints to external users or production clients:

- Add or reuse a verified authentication dependency.
- Authorize the caller to access the requested Analysis Run before returning any feature-set metadata or records.
- Restrict the processing command to an authorized operator/service role.
- Do not treat an unguessable UUID as authorization.
- Do not expose database errors, internal source paths, secrets or stack traces.

This document specifies the required access policy; it does not claim that authentication/authorization is already implemented. Public/production exposure of these routes is blocked until that security dependency exists and is tested. Do not introduce a guessed authentication mechanism during Phase 4 without reviewing the project's actual user/session model.

## 7. API behavior and data guarantees

- GET endpoints are strictly read-only and must not create feature sets or trigger processing.
- The POST command is idempotent for the same Analysis Run, active feature-definition version and input manifest.
- New feature-definition versions create separate feature sets; older results remain queryable.
- A feature record's missing numeric value is JSON `null`, not zero.
- Return the persisted full-precision numeric value. Presentation clients may round for display but must not modify the stored result.
- Do not return a single CE/PE recommendation, seller identity, seller ranking, support/resistance level, trigger, scenario decision or ML prediction from Phase 4.
- No live/intraday data, broker access, order execution, alerting, paper tracking, trading backtesting or new source acquisition is introduced.

## 8. Implementation sequence and acceptance checks

When implementation is separately authorized:

1. Add Pydantic response schemas for feature-set summaries and feature-record pages.
2. Implement the historical input selector over existing Phase 3 SQLAlchemy models.
3. Implement deterministic source-manifest construction and integrity checks.
4. Implement the feature service and persistence transaction using the approved two-table design.
5. Add the processing command route and GET-only retrieval routes under the existing `/api/v1` router.
6. Add authentication/authorization dependencies before any external/production exposure.
7. Test run readiness, exact-contract selection, missing historical dates, 1/5/22 windows, idempotent retries, changed-manifest conflicts, new-version preservation, pagination, filtering, cross-run feature-set access rejection and GET non-mutation.
8. Verify the API against PostgreSQL and the repository's SQLite test setup.
9. Confirm that Phase 3 routes, models, migrations and data behavior are unchanged.

No route, model, migration, calculation code, authentication code, database data or deployment is changed by this design document.

## 9. Open implementation verification

Before coding, verify the project's supported PostgreSQL version, test-database behavior, and the exact source-row identity strategy for provenance. Confirm whether existing deployment clients require a particular API versioning or authentication scheme. These checks must not be replaced by invented configuration values.
