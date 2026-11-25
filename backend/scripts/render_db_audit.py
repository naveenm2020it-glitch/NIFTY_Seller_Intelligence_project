import json
import os
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import create_engine, text


def json_default(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


def database_url():
    value = os.environ.get("DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("DATABASE_URL is not configured.")
    if value.startswith("postgres://"):
        return "postgresql+psycopg://" + value[len("postgres://"):]
    if value.startswith("postgresql://"):
        return "postgresql+psycopg://" + value[len("postgresql://"):]
    return value


def main():
    engine = create_engine(database_url(), pool_pre_ping=True, connect_args={"connect_timeout": 15})
    report = {"audit": "nifty-seller-intelligence-read-only-db-audit", "read_only": True}
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SET TRANSACTION READ ONLY")
            identity = connection.execute(text("""
                SELECT current_database() AS database_name,
                       current_user AS database_user,
                       current_setting('transaction_read_only') AS transaction_read_only,
                       current_setting('server_version') AS server_version
            """)).mappings().one()
            report["database"] = dict(identity)

            tables = connection.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)).scalars().all()
            expected = ["analysis_runs", "eod_ingestion_batches", "nifty50_eod_bars", "nifty_option_eod_bars"]
            report["expected_tables"] = {name: name in tables for name in expected}
            report["missing_tables"] = [name for name in expected if name not in tables]

            if not report["missing_tables"]:
                columns = connection.execute(text("""
                    SELECT table_name, column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = ANY(:names)
                    ORDER BY table_name, ordinal_position
                """), {"names": expected}).mappings().all()
                report["columns"] = [dict(row) for row in columns]

                report["spot"] = dict(connection.execute(text("""
                    SELECT COUNT(*) AS rows, MIN(trade_date) AS first_date, MAX(trade_date) AS last_date
                    FROM nifty50_eod_bars
                """)).mappings().one())

                report["option_coverage_latest_22_dates"] = [
                    dict(row) for row in connection.execute(text("""
                        SELECT trade_date, COUNT(*) AS option_rows,
                               COUNT(*) FILTER (WHERE option_type = 'CE') AS ce_rows,
                               COUNT(*) FILTER (WHERE option_type = 'PE') AS pe_rows,
                               COUNT(DISTINCT expiry) AS expiry_count,
                               MIN(expiry) AS first_expiry, MAX(expiry) AS last_expiry,
                               COALESCE(SUM(volume), 0) AS total_volume,
                               COALESCE(SUM(open_interest), 0) AS total_open_interest,
                               COUNT(*) FILTER (WHERE volume = 0) AS zero_volume_rows,
                               COUNT(*) FILTER (WHERE open_interest = 0) AS zero_oi_rows
                        FROM nifty_option_eod_bars
                        GROUP BY trade_date
                        ORDER BY trade_date DESC
                        LIMIT 22
                    """)).mappings().all()
                ]

                latest_run = connection.execute(text("""
                    SELECT id, analysis_date, selected_expiry, status, created_at
                    FROM analysis_runs ORDER BY created_at DESC LIMIT 1
                """)).mappings().first()
                report["latest_analysis_run"] = dict(latest_run) if latest_run else None

                if latest_run and latest_run["selected_expiry"]:
                    report["latest_run_selected_expiry_coverage"] = [
                        dict(row) for row in connection.execute(text("""
                            SELECT trade_date, expiry,
                                   COUNT(*) AS option_rows,
                                   COUNT(*) FILTER (WHERE option_type = 'CE') AS ce_rows,
                                   COUNT(*) FILTER (WHERE option_type = 'PE') AS pe_rows,
                                   COALESCE(SUM(volume), 0) AS total_volume,
                                   COALESCE(SUM(open_interest), 0) AS total_open_interest,
                                   COUNT(*) FILTER (WHERE volume = 0) AS zero_volume_rows,
                                   COUNT(*) FILTER (WHERE open_interest = 0) AS zero_oi_rows
                            FROM nifty_option_eod_bars
                            WHERE expiry = :expiry
                            GROUP BY trade_date, expiry
                            ORDER BY trade_date DESC
                            LIMIT 22
                        """), {"expiry": latest_run["selected_expiry"]}).mappings().all()
                    ]

                report["ingestion_batches"] = [
                    dict(row) for row in connection.execute(text("""
                        SELECT trade_date, selected_expiry, status, row_counts, created_at, completed_at
                        FROM eod_ingestion_batches
                        ORDER BY trade_date DESC
                        LIMIT 22
                    """)).mappings().all()
                ]
            report["result"] = "schema_ready_for_coverage_review" if not report["missing_tables"] else "schema_incomplete"
    finally:
        engine.dispose()

    print(json.dumps(report, default=json_default, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
