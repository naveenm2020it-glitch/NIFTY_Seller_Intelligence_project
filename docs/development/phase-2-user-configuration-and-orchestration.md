# Phase 2 — User Configuration & Data Orchestration

**Status: COMPLETED — 23 November 2026**  
**Working branch:** `phase-2-user-config-orchestration`  
**Base:** `phase-0-foundation`

## 1. Objective

Implement the application boundary that accepts an analysis request, validates and persists its configuration, and coordinates the permitted historical-data workflow in a reproducible way.

Phase 2 is limited to user configuration and orchestration. It does not implement the eight analytical engines, eight-scenario decision logic, four ML models, production dashboard, feedback learning, live-market analysis or automated trading.

## 2. Confirmed configuration requirements

The `user_config` module owns:
- Analysis date.
- Expiry selection.
- User preferences limited to approved presentation/display settings.

**There is no analysis cutoff-time setting.** Do not add a cutoff-time field to the configuration UI, API contract or database schema.

The application must preserve reproducibility by recording the analysis date, actual selected expiry, expiry-selection mode, source provenance and software/model versions.

### 2.1 Analysis date

- One completed NSE trading session per analysis run.
- Reject dates that are not completed trading sessions or for which the required historical data is unavailable.
- The 1-, 5- and 22-session analysis windows are calculated relative to the selected analysis date by later processing/feature-engineering stages.
- Date-range batch analysis is outside the first version; it can be considered as a future enhancement.

### 2.2 Expiry selection

- When the user selects an analysis date, the system automatically selects the nearest available expiry applicable to that date.
- If that nearest expiry is unavailable, the system automatically moves to the next available expiry.
- The user may override the automatic choice and select another available expiry manually.
- Record both the actual selected expiry and the selection mode (`AUTO` or `MANUAL`) in every analysis run.
- When the system moves to a later expiry because the nearest one is unavailable, clearly disclose that it was an automatic fallback in the review screen and run details.

### 2.3 User preferences

- Project-wide analytical rules remain fixed and are not user-editable through preferences. This includes core analytical logic, scenario definitions and validation rules.
- User-adjustable preferences are limited initially to presentation choices, such as dashboard display and report format, once those options are defined.
- Do not expose analytical thresholds or model parameters as user preferences without a separately reviewed and approved requirement.

### 2.4 Configuration scope

- The first version uses per-run configuration only.
- Each run stores an immutable snapshot of the analysis date, selected expiry, expiry selection mode, and any supported presentation preferences.
- Saved defaults and named configuration profiles are deferred until there is a demonstrated need.

### 2.5 Explicit user action before data retrieval and analysis

Selecting or changing the analysis date or expiry must not start a download, data retrieval or analysis automatically.

The frontend must show the resolved configuration for review. Data retrieval/download, validation and analysis orchestration may begin only after the user explicitly activates the **Start Analysis** action.

The action submits the reviewed configuration to the backend. The backend creates/starts the run and reports its lifecycle status; the frontend must not imply that processing has started or completed before the backend confirms it.

## 3. Run execution approach

- Implement the first version as a synchronous orchestration request, consistent with the current architecture, which defers background-job infrastructure.
- Keep run stages and status transitions explicit and persisted so the execution mechanism can be moved to a background worker later if measured processing time or reliability requires it.
- Do not add a queue, worker service or external job infrastructure in this phase without a separate scope decision.

## 4. Historical input data contract

For the first historical EOD version, use the approved Phase 1 archive datasets as the initial input contract:

- **F&O Bhavcopy:** primary source for available contract-level option/futures prices, volume and open-interest fields.
- **MII Contract Master:** contract identity and instrument metadata, including expiry, strike and option type where supplied.
- **NIFTY 50 Index OHLC:** underlying index price context.

Separate option-chain snapshots are not a mandatory Phase 2 input. Before any later analytical engine relies on a field, verify that the approved source actually supplies it. If a required field is absent, report a data gap and do not fabricate or silently infer the value.

The Start Analysis action may retrieve/download files only from approved historical archive locations. It must not trigger automated NSE collection until applicable NSE terms and permitted collection methods have been reviewed.

The application must verify dataset coverage, file presence, schema/required fields and integrity before processing. A run must fail clearly if required inputs are missing or invalid.

## 5. Architecture and operating constraints

The architecture is a React + Vite frontend with a Python + FastAPI modular monolith, PostgreSQL persistence and optional Backblaze B2 object storage. Initial execution is local. No production deployment is authorized.

- Historical EOD processing only; no live-market analysis.
- No order placement, trade execution or broker integration.
- Preserve original NSE source files unchanged.
- Never store credentials in configuration records or logs.
- Keep B2 optional; report unavailable storage clearly rather than silently claiming archival success.
- No persistent cloud database, hosted service or production deployment in this phase without separate approval.
- Do not create domain tables until entities, relationships and retention rules are documented and approved.

## 6. Orchestration responsibility

The orchestration layer coordinates discrete stages and records their state. The intended high-level sequence is:

1. Accept the user's explicit Start Analysis request and reviewed configuration.
2. Validate the selected completed trading date and configuration.
3. Resolve and record the actual expiry and whether it was selected automatically or manually, including any automatic fallback.
4. Resolve the approved historical input set and record its provenance.
5. Check source-file presence, coverage, required fields and integrity.
6. Hand validated inputs to the data-processing layer.
7. Persist run status, timestamps, configuration snapshot and stage outcomes.
8. Return a traceable run identifier and a clear status/error result.

This layer coordinates work; it must not contain analytics, scenario rules or model logic.

## 7. Implementation sequence

### 2.1 Requirements and data contract
- Define configuration fields, types, allowed values and validation rules using the confirmed decisions above.
- Define the analysis-run lifecycle and status transitions.
- Define source-dataset manifest and provenance contract.

### 2.2 User configuration service
- Add typed request/response schemas.
- Add validation and approved defaults.
- Persist immutable per-run configuration snapshots.
- Expose versioned REST endpoints.

### 2.3 Data orchestration service
- Add a run coordinator with explicit stage states and failure handling.
- Start data retrieval and analysis only from an explicit Start Analysis request.
- Resolve only approved historical archive locations.
- Verify manifests, coverage, required fields and file integrity before handing data to processing.
- Make retries idempotent and prevent partial runs from appearing successful.

### 2.4 Frontend configuration flow
- Add a configuration screen that consumes the API contract.
- Accept one completed historical trading date.
- Automatically display the nearest available expiry for the selected date, with a manual override to another available expiry.
- Clearly identify automatic fallback when the nearest expiry is unavailable.
- Provide a review step and explicit Start Analysis action; changing date or expiry alone must not trigger data retrieval or analysis.
- Display validation errors and the resolved run configuration.
- Do not imply that analysis has run until the backend confirms completion.

### 2.5 Verification and closeout
- Unit and API tests for valid/invalid configuration, including non-trading dates.
- Tests for automatic expiry selection, unavailable-nearest-expiry fallback, manual override, and persistence of the actual expiry and selection mode.
- Tests proving that date/expiry selection alone does not start retrieval or analysis, and that the explicit Start Analysis action does.
- Tests for source coverage/required-field failures, orchestration success, integrity failures, retries and partial failures.
- Database migration tests and frontend production build.
- Remote CI must pass before Phase 2 can be marked complete.

## 8. Acceptance criteria

Phase 2 is complete only when:
- A user can submit a valid single-date analysis configuration through the API and frontend.
- Non-trading dates and dates without required historical inputs are rejected with actionable errors.
- The nearest available expiry is selected automatically for the chosen analysis date.
- If the nearest expiry is unavailable, the next available expiry is selected automatically and the fallback is disclosed.
- A user can manually select another available expiry.
- Each run records the actual selected expiry and `AUTO`/`MANUAL` selection mode.
- Selecting or changing date/expiry does not start data retrieval or analysis; only explicit Start Analysis does.
- Project analytical rules cannot be changed through user preferences.
- Each run stores an immutable configuration snapshot.
- Every run has a stable identifier and auditable lifecycle status.
- Input manifests, source provenance, coverage, required-field checks and integrity results are recorded.
- Missing or corrupt inputs fail safely; no false-success state is possible.
- Retry behavior is tested and does not create duplicate logical runs.
- Tests and CI pass.
- Documentation describes configuration fields, API contracts, state transitions and operational boundaries.

## 9. Decisions status

The Phase 2 business decisions are now set as follows:

| Decision | First-version rule |
|---|---|
| Analysis date | One completed NSE trading session per run |
| Cutoff time | Excluded |
| Expiry | Nearest available automatically; next available fallback; manual override |
| Preferences | Presentation/display preferences only; analytical rules fixed |
| Configuration scope | Per-run snapshots; no saved profiles initially |
| Execution | Synchronous first version; persisted stages/statuses allow future background execution |
| Historical inputs | F&O Bhavcopy, MII Contract Master and NIFTY 50 Index OHLC; validate required fields; no mandatory separate option-chain snapshot in Phase 2 |

These decisions establish the first-version scope. Any change requires an explicit requirements update before implementation.

## 10. Exit boundary

Phase 2 delivers configuration and orchestration foundations only. Data cleaning/normalization, 1/5/22-session feature engineering, analytical engines, scenarios, ML models, dashboard expansion and feedback learning remain later roadmap phases.


## 11. Implementation note — 23 November 2026

The first implementation slice is on the Phase 2 branch. The persistence model is limited to one table, analysis_runs; its fields, no-user-relationship boundary and no-automatic-deletion retention rule are documented in phase-2-data-contract.md. No other domain tables have been introduced.

The API and frontend implement read-only configuration preview, automatic/manual expiry selection, explicit Start Analysis, idempotent run creation, source provenance and validation outcomes. READY_FOR_PROCESSING is only a validated-input handoff state. Analytical processing remains deferred to later phases.

The implementation reads an extracted local copy of the Phase 1 archive. It does not automatically materialize the B2 archive or download from NSE.

**Final verification — 23 November 2026:** CI run [45150719524](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/actions/runs/45150719524) passed with the verified Phase 1 artifact staged into the documented archive layout. PostgreSQL 16 migrations passed; the real-archive API smoke test enumerated all 22 audited dates, created and re-read persisted runs for 17-Nov and 19-Nov, and exercised previous-session MII reconciliation on 17-Nov. Backend suite: 20 passed. Frontend production build passed. Configured B2 bucket connectivity passed. See [Phase 2 closeout](phase-2-closeout.md) for evidence and retained boundaries.
