# Phase 1 — Historical EOD Acquisition and Audit

## Purpose

Acquire and audit only the core historical NIFTY EOD data sources required for the 22-session validation window. This document defines the intended workflow; it does not claim that the downloads or audit have already run.

## Scope

- NIFTY 50 index and NIFTY options only.
- Historical end-of-day data only; no live-market or intraday-chain reconstruction.
- Use exactly these three core data sources:
  1. NSE F&O — UDiFF Common Bhavcopy Final (ZIP).
  2. NSE F&O — MII NSE Exclusive Contract File (GZ), matching each session.
  3. NIFTY 50 historical index OHLC (CSV), matching each session/date from the official NIFTY Indices historical-data source.
- Do not acquire optional/secondary reports for Phase 1, including Daily Settlement Prices, Participant-wise Open Interest, Participant-wise Trading Volumes, FII derivatives statistics, Daily Volatility, Spd Contract File, or other indices' reports.
- Target: 22 exchange trading sessions anchored to the 19-Nov-2026 sample audit.
- Candidate dates: 21-Oct, 22-Oct, 23-Oct, 26-Oct, 27-Oct, 28-Oct, 29-Oct, 30-Oct; 02-Nov, 03-Nov, 04-Nov, 05-Nov, 06-Nov, 08-Nov (Sunday Muhurat session, verify actual FO report availability), 09-Nov, 11-Nov; 12-Nov, 13-Nov, 16-Nov, 17-Nov, 18-Nov, 19-Nov 2026.
- The candidate date list must be reconciled against the official exchange trading calendar and actual report availability before declaring 22 sessions complete. Do not silently drop a special session or substitute a date.

## Compliance gate — mandatory before acquisition

Before enabling any automated HTTP downloader or using acquired data in this application or ML pipeline, verify and document that the applicable NSE terms, data-use policy, subscription/license (if required), and permitted acquisition method allow:
1. downloading the selected historical/EOD reports by the proposed method;
2. temporary or persistent storage as intended;
3. feature engineering and machine-learning analysis;
4. retaining derived metrics, audit metadata, and analysis outputs in the application.

The current intended acquisition method is manual download from official report pages followed by transfer to the Ubuntu server. Do not use automated HTTP requests, scraping, or scripted website collection unless NSE has expressly authorized that method in writing. Use only an approved official acquisition route. Do not bypass access controls, rate limits, authentication, or other restrictions. If the permission status or permitted route is unclear, pause acquisition and obtain written clarification/permission from NSE or the relevant data provider.

## Intended manual acquisition and Ubuntu workflow

1. Open the official NSE Derivatives All Reports page and locate the F&O UDiFF Common Bhavcopy Final ZIP for the exact trading date.
2. Download the matching daily F&O-MII NSE Exclusive Contract File GZ from the official reports page.
3. Obtain the matching NIFTY 50 historical OHLC record/file from the official NIFTY Indices historical-data source.
4. Verify the trading date and source report identity before transferring files.
5. Transfer the original ZIP/GZ/CSV files to the Ubuntu server using an authenticated secure file-transfer method such as SCP.
6. Store original files unchanged in a date-scoped raw directory. Do not rename, modify, or extract the only original copy.
7. Generate a manifest containing at least: trading date, source name, official source URL/page, original filename, detected format, byte size, SHA-256, acquisition timestamp, and acquisition status. Keep credentials and signed URLs out of the manifest and logs.
8. Test archive integrity (for example, `unzip -t` and `gzip -t`) without modifying the original archive.
9. Extract/process working copies only after the original files and checksums have been recorded.
10. Validate each session and produce a machine-readable audit summary plus a human-readable report.
11. Feed only validated normalized records/features into the approved analysis/ML pipeline.

Raw archives must never be committed to Git or uploaded to GitHub Actions artifacts/cache. Any retention/deletion policy must be consistent with the applicable data-use permission. The original-file preservation requirement and the earlier six-hour temporary-file cleanup requirement must be reconciled before production operation: preserve the original archive only for the period and in the storage location explicitly permitted.

## Persistent versus temporary data

### Original source files
- Preserve the original ZIP/GZ/CSV bytes unchanged in the approved Ubuntu storage location, subject to the applicable license/retention terms.
- Do not commit raw archives to Git, publish them as Actions artifacts, or place them in caches.
- Do not silently apply a six-hour deletion policy to originals if the approved workflow requires longer preservation; resolve retention terms first.

### Derived audit metadata and outputs
Subject to the compliance gate, retain:
- Manifest metadata: source URL/page, filename, date, byte size, SHA-256, acquisition status, parser version.
- Validation counts and exceptions, without reproducing source rows or raw market data.
- Derived features, model outputs, SellerPoints zones (S1/S2/R1/R2), and reports only to the extent permitted by the applicable data-use terms.

## 22-session audit checklist

For every session, record pass/fail/not-applicable and evidence for:

- All three core source inputs are available and date-aligned.
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

A session is complete only when all three core source inputs are present and its validation report is generated. Missing files or failed checks must be marked explicitly; never fabricate or infer missing source rows.

## Completion criteria

Phase 1 acquisition/audit is complete only when:
- the compliance gate is documented as approved;
- all 22 valid sessions have manifests and verified copies of the three core source inputs;
- all per-session audit checks have explicit outcomes;
- unresolved mismatches and missing dates are documented;
- the consolidated audit report is reproducible from the manifest and parser version;
- raw-file retention and cleanup behavior match the approved data-use terms;
- no raw archives appear in Git history, Actions artifacts, caches, or logs.

## Current status

**Specification only — not executed.** No 22-session bulk download, checksum manifest, or consolidated audit is claimed by this document. Automated acquisition remains disabled unless and until the proposed automated method is expressly authorized. Current planned acquisition is manual download and secure transfer, subject to applicable data-use permission.
