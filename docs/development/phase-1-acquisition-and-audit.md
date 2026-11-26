# Phase 1 — Historical EOD Acquisition and Audit

## Purpose

Acquire and audit the historical NIFTY EOD source files required for the 22-session validation window. This document defines the intended workflow; it does not claim that the downloads or audit have already run.

## Scope

- NIFTY 50 index and NIFTY options only.
- Historical end-of-day data only; no live-market or intraday-chain reconstruction.
- Target: 22 exchange trading sessions anchored to the 19-Nov-2026 sample audit.
- Candidate dates: 21-Oct, 22-Oct, 23-Oct, 26-Oct, 27-Oct, 28-Oct, 29-Oct, 30-Oct; 02-Nov, 03-Nov, 04-Nov, 05-Nov, 06-Nov, 08-Nov (Sunday Muhurat session, verify actual FO report availability), 09-Nov, 11-Nov; 12-Nov, 13-Nov, 16-Nov, 17-Nov, 18-Nov, 19-Nov 2026.
- The candidate date list must be reconciled against the official exchange trading calendar and actual report availability before declaring 22 sessions complete. Do not silently drop a special session or substitute a date.

## Compliance gate — mandatory before acquisition

Before enabling any automated HTTP downloader or using acquired data in this application or ML pipeline, verify and document that the applicable NSE terms, data-use policy, subscription/license (if required), and permitted acquisition method allow:
1. downloading the selected historical/EOD reports by the proposed method;
2. temporary local storage and processing;
3. feature engineering and machine-learning analysis;
4. retaining derived metrics, audit metadata, and analysis outputs in the application.

Use only an approved official acquisition route. Do not bypass access controls, rate limits, authentication, or other restrictions. If the permission status or permitted route is unclear, keep the downloader disabled and obtain written clarification/permission from NSE or the relevant data provider.

## Intended GitHub Actions workflow

Run on a GitHub-hosted Ubuntu runner, manually or on an explicitly approved schedule.

1. Resolve the official report URLs for each required session (F&O UDiFF common bhavcopy and matching daily F&O-MII contract file; plus NIFTY 50 historical index OHLC from an approved source).
2. Execute a Python downloader only after the compliance gate is marked approved.
3. Download original ZIP/GZ/CSV files to a job-local temporary directory. Preserve original bytes and filenames during the run; do not commit raw files, upload them as Actions artifacts, cache them, or copy them to persistent object storage.
4. Generate a manifest containing at least: trading date, source name, official source URL, original filename, detected format, byte size, SHA-256, download timestamp (UTC), and acquisition status. Keep credentials and signed URLs out of the manifest and logs.
5. Extract/process copies only in temporary runner storage. Retain the original downloaded archives unchanged until validation completes.
6. Validate each session and produce a machine-readable audit summary plus a human-readable report.
7. Feed only validated normalized records/features into the approved analysis/ML pipeline. Persist only permitted derived results and non-sensitive audit metadata.
8. In an unconditional cleanup step, remove the temporary download directory, extracted files, intermediate datasets, and any temporary credentials. Do not publish raw files as workflow artifacts.
9. Set a job timeout of at most 360 minutes and run cleanup with an always/finally condition. GitHub-hosted runners are ephemeral; the runner is discarded after the job. The six-hour limit is a maximum retention target, not a guarantee that a timed-out process can execute its cleanup command; runner disposal provides the final isolation boundary.

## Persistent versus temporary data

### Temporary on the Ubuntu runner only
- Original NSE ZIP/GZ/CSV downloads.
- Extracted CSVs and transformed/intermediate datasets.
- Temporary credentials, cookies, or authorization headers (prefer GitHub Actions secrets and never write them to logs).
- Any temporary model input files.

### May be retained, subject to the compliance gate
- Manifest metadata: source URL, filename, date, byte size, SHA-256, acquisition status, parser version.
- Validation counts and exceptions, without reproducing source rows or raw market data.
- Derived features, model outputs, SellerPoints zones (S1/S2/R1/R2), and reports only to the extent permitted by the applicable data-use terms.

Raw market-data archives must never be committed to Git or uploaded to GitHub Actions artifacts/cache.

## 22-session audit checklist

For every session, record pass/fail/not-applicable and evidence for:

- Bhavcopy and matching daily contract-master file availability.
- NIFTY CE and PE contract coverage.
- Unique instrument identifiers and duplicate detection.
- Instrument ID to contract-master join coverage.
- Strike, expiry, option type, and relevant contract attributes consistency.
- Correct format-specific scaling and expiry conversion; do not apply legacy MII conversions to a different file format without detection and validation.
- Zero-volume contracts retained and distinguished from missing records.
- Listed-versus-traded contract coverage and unmatched records.
- NIFTY 50 index OHLC availability and date alignment.
- File integrity: non-zero size, readable archive, SHA-256 recorded, and repeat-download checksum comparison where appropriate.
- Special-session verification for 08-Nov-2026; verify official FO report existence before treating it as a completed session.

A session is complete only when all required source files are present and its validation report is generated. Missing files or failed checks must be marked explicitly; never fabricate or infer missing source rows.

## Completion criteria

Phase 1 acquisition/audit is complete only when:
- the compliance gate is documented as approved;
- all 22 valid sessions have source manifests and verified downloads;
- all per-session audit checks have explicit outcomes;
- unresolved mismatches and missing dates are documented;
- the consolidated audit report is reproducible from the manifest and parser version;
- temporary raw and intermediate files have been removed;
- no raw archives appear in Git history, Actions artifacts, caches, logs, or persistent storage.

## Current status

**Specification only — not executed.** No 22-session bulk download, checksum manifest, or consolidated audit is claimed by this document. Automated acquisition remains disabled pending confirmation of permitted data use and acquisition method.
