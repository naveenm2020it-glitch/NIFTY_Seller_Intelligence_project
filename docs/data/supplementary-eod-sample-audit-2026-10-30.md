# NSE Supplementary EOD Sample Audit — 30 October 2026

**Audit executed:** 23 November 2026  
**Repository branch:** `phase-2-supplementary-report-sample-audit`  
**Scope:** One-session download, schema inspection and comparison to the Phase 1 F&O Bhavcopy for 30-Oct-2026. This is a source-quality/usefulness check, not a backtest or authorization for recurring automated collection.

## Executive decision

Use the direct NSE archive URLs on `nsearchives.nseindia.com` for this controlled historical sample retrieval. Do **not** use the guessed `/api/reports` request route: it returned 404/JSON for all candidates in the failed probe. The direct archive route returned valid original report files with HTTP 200.

Keep the Phase 1 three-source core unchanged. No supplementary file is approved as a mandatory analytical input from this one-day check.

| Report | 30-Oct sample | Assessment | Recommended treatment |
|---|---:|---|---|
| Participant-wise Open Interest | 973 bytes; SHA-256 `ed9c4a6584a9c441b0dd202c4699c19118679c3cda676268ec1d652ba9cd32a7` | Aggregate Equity Derivatives participant classes; not NIFTY-specific | Optional broad-market context; validate multi-day stability first |
| Participant-wise Trading Volumes | 983 bytes; SHA-256 `427757490c6889aaf9a04da7ba27e239b783d34ab4c3d690ef8b90b0ee15f474` | Aggregate participant activity, not closing positions or NIFTY-specific | Lower-priority optional context; never use as contract-level NIFTY volume |
| Market Activity Report ZIP | 501,824 bytes; SHA-256 `b8c3cd52f56bf95fec5b6d10e9534ac94ed42dcdcc506f3feb02d5f273340c0a` | Useful contract and segment summaries; substantially overlaps Bhavcopy | Optional reconciliation/summary source; do not replace Bhavcopy |
| Daily Settlement Prices | 70,920 bytes; SHA-256 `5bbce6da9fd0b520b97ecd387310e853c0b0aa9bd3649fc073472e850f809df8` | Contract settlement references for futures; NIFTY OPTIDX row is an underlying-level value | Reconciliation only |
| Daily Volatility | 40,752 bytes; SHA-256 `448a1870aab3849c80ab537f16f2dc9f64620a08a2e61f23d18bf81e7818d7de` | Exchange underlying/futures EWMA volatility, not option implied volatility | Optional volatility-regime reference, not option IV |

## 1. Retrieval method

The successful probe used the NSE archive host and these date-specific routes:

- Participant OI: `https://nsearchives.nseindia.com/content/nsccl/fao_participant_oi_30102026.csv`
- Participant volume: `https://nsearchives.nseindia.com/content/nsccl/fao_participant_vol_30102026.csv`
- Market Activity: `https://nsearchives.nseindia.com/archives/fo/mkt/fo30102026.zip`
- Settlement: `https://nsearchives.nseindia.com/archives/nsccl/sett/FOSett_prce_30102026.csv`
- Volatility: `https://nsearchives.nseindia.com/archives/nsccl/volt/FOVOLT_30102026.csv`

Each returned HTTP 200 with a plausible content type and payload (CSV or ZIP). Original files were retained unchanged in the workflow artifact. The NSE `/api/reports` approach was not reliable in this test and is not the recommended route.

Workflow evidence:
- Run: [45143286870](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/actions/runs/45143286870)
- Artifact: `14803585520`, `nse-api-route-probe-2026-10-30`
- Artifact SHA-256: `0023958a67781a44550ac004aed97401a3c55e7bcc38c434830ae68a66ef934c`
- Artifact contents include the downloaded originals and route manifest.
- The original Phase 1 Bhavcopy ZIP was used from the verified Phase 1 archive, not re-downloaded.

## 2. Participant-wise Open Interest

The current file parses after skipping the first report-title row. It has 5 data rows (Client, DII, FII, Pro, TOTAL) and 14 named measures:

- Client Type
- Future Index Long / Future Index Short
- Future Stock Long / Future Stock Short
- Option Index Call Long / Option Index Put Long
- Option Index Call Short / Option Index Put Short
- Option Stock Call Long / Option Stock Put Long
- Option Stock Call Short / Option Stock Put Short
- Total Long Contracts / Total Short Contracts

The title identifies the report as Equity Derivatives. It contains no symbol, expiry, strike or contract identifier. These index-option aggregates therefore must not be attributed to NIFTY alone and cannot identify who wrote or bought a particular NIFTY option.

**Decision:** Potentially useful as broad participant-category context across the equity-derivatives segment. A single date cannot establish signal value. Use date-over-date changes only after a multi-session audit and preserve the aggregate scope in all labels.

## 3. Participant-wise Trading Volumes

The file has the same participant categories and index/stock futures and options long/short dimensions as the OI report, but the measure is trading volume.

Volume records activity, not closing positions or net open interest. It is also not NIFTY-specific and must not replace the contract-level volume in Bhavcopy.

**Decision:** Optional and lower priority than participant OI. Only add if multi-day testing demonstrates incremental explanatory value beyond Bhavcopy-derived features.

## 4. Market Activity ZIP

The ZIP contains 11 files:

| Member | Bytes | NSE help-file description |
|---|---:|---|
| `fo_30102026.csv` | 487 | Total volume summary by product type |
| `fo30102026.csv` | 108,791 | Contract-wise futures volume summary |
| `op30102026.csv` | 2,519,661 | Contract-wise options volume summary |
| `futidx30102026.csv` | 735 | Symbol-wise index futures volume summary |
| `futivx30102026.csv` | 210 | Volatility futures volume summary |
| `futstk30102026.csv` | 13,072 | Symbol-wise stock futures volume summary |
| `optidx30102026.csv` | 2,211 | Symbol-wise index options volume summary |
| `optstk30102026.csv` | 12,970 | Symbol-wise stock options volume summary |
| `ttfut30102026.csv` | 1,374 | Top 20 stock futures contracts |
| `ttopt30102026.csv` | 2,525 | Top 20 stock options contracts |
| `fohelp.txt` | 845 | Report member descriptions |

### NIFTY option contract reconciliation

The contract-wise options member `op30102026.csv` contains 1,056 NIFTY OPTIDX contract rows for this date. The Phase 1 Bhavcopy contains 1,694 NIFTY IDO rows, of which 638 have zero traded volume.

For the 1,056 common active contracts, matching by expiry, strike and CE/PE:

- 1,056/1,056 have identical open, high, low and close prices.
- `NO_OF_CONT` equals Bhavcopy `TtlTradgVol` for 1,056/1,056 contracts.
- Market Activity `TRD_QTY` equals `NO_OF_CONT × 65` for all 1,056 rows; this is traded quantity in units, whereas `NO_OF_CONT` is the contract count for this sample's lot size.
- Market Activity has no additional NIFTY option contracts beyond the Bhavcopy. It omits the 638 zero-volume Bhavcopy rows, which is why Bhavcopy remains the more complete historical source.
- Closing open interest matches exactly for 855/1,056 contracts; 201 differ. Every observed difference is a multiple of 65, but the reason for the difference was not established by this one-day sample. The Market Activity help file notes OI as available in the trading system at the end of trading hours.

The OI discrepancy must be treated as a reconciliation issue, not silently overwritten or interpreted as a signal. Investigate it across several dates and clarify the reporting snapshot and units before using this member as an OI validator.

**Decision:** Valuable for optional integrity checks and market-wide summaries. The exact OHLC and volume reconciliation is strong for this sample. It is redundant for primary NIFTY contract data and incomplete for zero-volume contracts. Keep Bhavcopy authoritative.

## 5. Daily Settlement Prices

The CSV has 1,571 rows and these five columns: DATE, INSTRUMENT, UNDERLYING, EXPIRY DATE, MTM SETTLEMENT PRICE.

It has four NIFTY rows:
- Three FUTIDX settlements for 23-Nov-2026, 29-Dec-2026 and 25-Jan-2027.
- One OPTIDX row with no expiry and settlement value 23,053.10, which is an underlying-level NIFTY reference rather than a strike/contract option premium.

The three NIFTY futures settlements are 23,098.90, 23,235.80 and 23,352.60. The report does not provide a per-strike NIFTY option settlement surface.

**Decision:** Use for independent settlement reconciliation only. It should not be a separate signal feature when Bhavcopy already supplies contract settlement prices.

## 6. Daily Volatility

The CSV has 229 rows and 16 columns. It supplies underlying and futures closes, previous closes, log returns, previous/current daily volatility and annualised volatility. The current daily volatility is calculated with the stated EWMA-like expression:

`sqrt(0.995 × previous_daily_volatility² + 0.005 × log_return²)`

For NIFTY on 30-Oct-2026:
- Underlying close: 23,053.10
- Underlying annualised volatility: 0.16024860 (16.024860%)
- Futures close: 23,098.90
- Futures annualised volatility: 0.16094555 (16.094555%)
- Applicable annualised volatility: 0.16094555 (16.094555%)

This is underlying/futures volatility. It is not option implied volatility, does not describe a strike-wise IV surface and must not be relabelled as option IV.

**Decision:** Optional reference for a volatility-regime cross-check against a volatility feature calculated from the core historical price series. Do not make it mandatory.

## 7. Recommended decision for the project

1. **Keep mandatory core unchanged:** F&O UDiFF Bhavcopy Final, F&O MII Contract File and NIFTY 50 All Indices daily-close CSV.
2. **First supplementary candidate:** Participant-wise OI, strictly labelled broad Equity Derivatives participant aggregates; require multi-session testing and no NIFTY-specific attribution.
3. **Optional candidate:** Daily Volatility as a futures/underlying volatility reference; validate its methodology and history against independently calculated volatility.
4. **Optional reconciliation only:** Market Activity contract summaries and Daily Settlement Prices. Neither should supersede Bhavcopy.
5. **Lower priority:** Participant-wise Trading Volumes, pending proof of incremental signal beyond participant OI and Bhavcopy volume.
6. **Still deferred:** FII derivatives XLS, NCL OI, combined OI, combined delta-equivalent OI and other reports not inspected here.

A single day establishes that the files can be retrieved and parsed; it does not prove predictive value, publication consistency, or that the same schema and availability hold historically. Before recurring collection, review NSE's applicable terms and confirm the permitted acquisition method. Do not introduce these reports into production signals based solely on this sample.

## 8. Reproducibility references

- Phase 1 source archive: `phase1-nse-fo-index-download-and-diagnostics`, including the 30-Oct-2026 original Bhavcopy.
- Supplementary raw sample artifact: [GitHub Actions run 45143286870](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/actions/runs/45143286870), artifact `14803585520`.
- Download implementation: `tools/probe_nse_reports_api.py` on `phase-2-supplementary-report-sample-audit`.

