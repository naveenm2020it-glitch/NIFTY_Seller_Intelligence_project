# Phase 2 — User Configuration & Data Orchestration

**Status: STARTED — 23 November 2026**  
**Working branch:** `phase-2-user-config-orchestration`  
**Base:** `phase-0-foundation`

## 1. Objective

Implement the application boundary that accepts an analysis request, validates and persists its configuration, and coordinates the permitted historical-data workflow in a reproducible way.

Phase 2 is limited to user configuration and orchestration. It does not implement the eight analytical engines, eight-scenario decision logic, four ML models, production dashboard, feedback learning, live-market analysis or automated trading.

## 2. Requirements confirmed by the project architecture and user decisions

The `user_config` module owns:
- Analysis date.
- Expiry selection.
- User preferences.

**There is no analysis cutoff-time setting.** Do not add a cutoff-time field to the configuration UI, API contract or database schema.

The application must preserve reproducibility by recording the analysis date, actual selected expiry, expiry-selection mode, source provenance and software/model versions.

### 2.1 Expiry selection rules — confirmed

- When the user selects an analysis date, the system automatically selects the nearest available expiry applicable to that date.
- If that nearest expiry is unavailable, the system automatically moves to the next available expiry.
- The user may override the automatic choice and select another available expiry manually.
- Record both the actual selected expiry and the selection mode (`AUTO` or `MANUAL`) in every analysis run.
- When the system moves to a later expiry because the nearest one is unavailable, clearly disclose that it was an automatic fallback in the review screen and run details.

### 2.2 Explicit user action before data retrieval and analysis — confirmed

Selecting or changing the analysis date or expiry must not start a download, data retrieval or analysis automatically.

The frontend must show the resolved configuration for review. Data retrieval/download, validation and analysis orchestration may begin only after the user explicitly activates the **Start Analysis** action.

The action must submit the reviewed configuration to the backend. The backend then creates/starts the run and reports its lifecycle status; the frontend must not imply that processing has started or completed before the backend confirms it.

The architecture is a React + Vite frontend with a Python + FastAPI modular monolith, PostgreSQL persistence and optional Backblaze B2 object storage. Initial execution is local. No production deployment is authorized.

## 3. Orchestration responsibility

The orchestration layer will coordinate discrete stages and record their state. The intended high-level sequence is:

1. Accept the user's explicit Start Analysis request and reviewed configuration.
2. Validate the request against approved configuration rules.
3. Resolve and record the actual expiry and whether it was selected automatically or manually, including any automatic fallback.
4. Resolve the selected historical input set and record its provenance.
5. Check source-file presence and integrity before processing.
6. Hand validated inputs to the data-processing layer.
7. Persist run status, timestamps, configuration snapshot and stage outcomes.
8. Return a traceable run identifier and a clear status/error result.

This layer coordinates work; it must not contain analytics, scenario rules or model logic.

## 4. Operating constraints

- Historical EOD processing only; no live-market analysis.
- No order placement, trade execution or broker integration.
- Preserve original NSE source files unchanged.
- Do not implement automated NSE collection until applicable NSE terms and permitted collection methods have been reviewed.
- Do not assume that the current Phase 1 archive contains every input needed for option-chain analysis. Confirm required source datasets before declaring an analysis run executable.
- Never store credentials in configuration records or logs.
- Keep B2 optional; the application must report unavailable storage clearly rather than silently claiming archival success.
- No persistent cloud database, hosted service or production deployment in this phase without separate approval.
- Do not create domain tables until entities, relationships and retention rules are documented and approved.

## 5. Proposed implementation sequence

### 2.1 Requirements and data contract
- Define configuration fields, types, allowed values and validation rules, incorporating the confirmed expiry-selection and explicit-start rules above.
- Define the analysis-run lifecycle and status transitions.
- Define source-dataset manifest and provenance contract.
- Confirm whether a configuration is a reusable user preference, a per-run override, or both.

### 2.2 User configuration service
- Add typed request/response schemas.
- Add validation and explicit defaults only after the relevant rules are approved.
- Persist configuration snapshots associated with analysis runs.
- Expose versioned REST endpoints.

### 2.3 Data orchestration service
- Add a run coordinator with explicit stage states and failure handling.
- Start data retrieval and analysis only from an explicit Start Analysis request.
- Resolve only approved historical source locations.
- Verify manifests and file integrity before handing data to processing.
- Make retries idempotent and prevent partial runs from appearing successful.

### 2.4 Frontend configuration flow
- Add a configuration screen that consumes the API contract.
- Automatically display the nearest available expiry for the selected analysis date, with a manual override to another available expiry.
- Clearly identify automatic fallback when the nearest expiry is unavailable.
- Provide a review step and explicit Start Analysis action; changing date or expiry alone must not trigger data retrieval or analysis.
- Display validation errors and the resolved run configuration.
- Do not imply that analysis has run until the backend confirms completion.

### 2.5 Verification and closeout
- Unit and API tests for valid/invalid configuration.
- Tests for automatic expiry selection, unavailable-nearest-expiry fallback, manual override, and persistence of the actual expiry and selection mode.
- Tests proving that date/expiry selection alone does not start retrieval or analysis, and that the explicit Start Analysis action does.
- Tests for orchestration success, missing inputs, integrity failures, retries and partial failures.
- Database migration tests and frontend production build.
- Remote CI must pass before Phase 2 can be marked complete.

## 6. Acceptance criteria

Phase 2 is complete only when:
- A user can submit a valid analysis configuration through the API and frontend.
- The nearest available expiry is selected automatically for the chosen analysis date.
- If the nearest expiry is unavailable, the next available expiry is selected automatically and the fallback is disclosed.
- A user can manually select another available expiry.
- Each run records the actual selected expiry and `AUTO`/`MANUAL` selection mode.
- Selecting or changing date/expiry does not start data retrieval or analysis; only explicit Start Analysis does.
- Invalid or ambiguous configuration is rejected with actionable errors.
- The exact configuration snapshot is associated with each run.
- Every run has a stable identifier and auditable lifecycle status.
- Input manifests, source provenance and integrity results are recorded.
- Missing or corrupt inputs fail safely; no false-success state is possible.
- Retry behavior is tested and does not create duplicate logical runs.
- Tests and CI pass.
- Documentation describes configuration fields, API contracts, state transitions and operational boundaries.

## 7. Decisions still required before finalizing implementation

The following business rules remain to be confirmed before database schema and UI defaults are locked:

1. Analysis date: past-session-only, date range, or both?
2. Preferences: which options are user-adjustable, and which are fixed project rules?
3. Configuration scope: one user's saved defaults, per-run overrides, or named profiles?
4. Run execution: synchronous API request for the first version, or a background job with polling?
5. Historical inputs: exact required files for each analysis type, especially whether option-chain snapshots are required in addition to Bhavcopy, contract-master and index OHLC data?

The analysis cutoff-time setting is explicitly excluded. Expiry-selection behaviour and the explicit Start Analysis gate are confirmed requirements, not open decisions.

Until the remaining decisions are confirmed, implementation should favor typed contracts and testable service boundaries without hard-coding unsupported business assumptions.

## 8. Exit boundary

Phase 2 delivers configuration and orchestration foundations only. Data cleaning/normalization, 1/5/22-session feature engineering, analytical engines, scenarios, ML models, dashboard expansion and feedback learning remain later roadmap phases.
