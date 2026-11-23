# Phase 2 — User Configuration & Data Orchestration

**Status: STARTED — 23 November 2026**  
**Working branch:** `phase-2-user-config-orchestration`  
**Base:** `phase-0-foundation`

## 1. Objective

Implement the application boundary that accepts an analysis request, validates and persists its configuration, and coordinates the permitted historical-data workflow in a reproducible way.

Phase 2 is limited to user configuration and orchestration. It does not implement the eight analytical engines, eight-scenario decision logic, four ML models, production dashboard, feedback learning, live-market analysis or automated trading.

## 2. Requirements confirmed by the project architecture

The `user_config` module owns:
- Analysis date.
- Intended cutoff time.
- Expiry selection.
- User preferences.

The application must preserve reproducibility by recording analysis inputs, cutoff, expiry, source provenance and software/model versions.

The architecture is a React + Vite frontend with a Python + FastAPI modular monolith, PostgreSQL persistence and optional Backblaze B2 object storage. Initial execution is local. No production deployment is authorized.

## 3. Orchestration responsibility

The orchestration layer will coordinate discrete stages and record their state. The intended high-level sequence is:

1. Accept an analysis request and its configuration.
2. Validate the request against approved configuration rules.
3. Resolve the selected historical input set and record its provenance.
4. Check source-file presence and integrity before processing.
5. Hand validated inputs to the data-processing layer.
6. Persist run status, timestamps, configuration snapshot and stage outcomes.
7. Return a traceable run identifier and a clear status/error result.

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
- Define configuration fields, types, allowed values, timezone semantics and validation rules.
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
- Resolve only approved historical source locations.
- Verify manifests and file integrity before handing data to processing.
- Make retries idempotent and prevent partial runs from appearing successful.

### 2.4 Frontend configuration flow
- Add a configuration screen that consumes the API contract.
- Display validation errors and the resolved run configuration.
- Do not imply that analysis has run until the backend confirms completion.

### 2.5 Verification and closeout
- Unit and API tests for valid/invalid configuration.
- Tests for orchestration success, missing inputs, integrity failures, retries and partial failures.
- Database migration tests and frontend production build.
- Remote CI must pass before Phase 2 can be marked complete.

## 6. Acceptance criteria

Phase 2 is complete only when:
- A user can submit a valid analysis configuration through the API and frontend.
- Invalid or ambiguous configuration is rejected with actionable errors.
- The exact configuration snapshot is associated with each run.
- Every run has a stable identifier and auditable lifecycle status.
- Input manifests, source provenance and integrity results are recorded.
- Missing or corrupt inputs fail safely; no false-success state is possible.
- Retry behavior is tested and does not create duplicate logical runs.
- Tests and CI pass.
- Documentation describes configuration fields, API contracts, state transitions and operational boundaries.

## 7. Decisions required before finalizing implementation

The architecture establishes the configuration categories but does not yet specify their complete business rules. These must be confirmed before database schema and UI defaults are locked:

1. Analysis date: past-session-only, date range, or both?
2. Cutoff time: exchange-local timezone and permitted cutoff values?
3. Expiry selection: nearest expiry, a specific expiry date, or multiple expiries?
4. Preferences: which options are user-adjustable, and which are fixed project rules?
5. Configuration scope: one user's saved defaults, per-run overrides, or named profiles?
6. Run execution: synchronous API request for the first version, or a background job with polling?
7. Historical inputs: exact required files for each analysis type, especially whether option-chain snapshots are required in addition to Bhavcopy, contract-master and index OHLC data?

Until these are confirmed, implementation should favor typed contracts and testable service boundaries without hard-coding unsupported business assumptions.

## 8. Exit boundary

Phase 2 delivers configuration and orchestration foundations only. Data cleaning/normalization, 1/5/22-session feature engineering, analytical engines, scenarios, ML models, dashboard expansion and feedback learning remain later roadmap phases.
