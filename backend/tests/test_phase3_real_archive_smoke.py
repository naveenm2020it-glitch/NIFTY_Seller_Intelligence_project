"""Opt-in Phase 3 integration against the immutable, checksum-verified Phase 1 archive.

This exercises every audited trading date through the real API and a temporary PostgreSQL database.
"""
import math
import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import AnalysisRun, EodIngestionBatch, Nifty50EodBar, NiftyOptionEodBar
from app.database.session import get_engine
from app.main import app

pytestmark = pytest.mark.skipif(
    os.getenv("PHASE3_REAL_ARCHIVE_SMOKE") != "1",
    reason="real Phase 1 archive Phase 3 smoke test is opt-in",
)


def test_phase3_processes_all_22_verified_sessions_into_postgres():
    expected_dates = [
        "2026-10-21", "2026-10-22", "2026-10-23",
        "2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29", "2026-10-30",
        "2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
        "2026-11-08", "2026-11-09", "2026-11-11", "2026-11-12", "2026-11-13",
        "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19",
    ]
    total_options = 0
    processed_runs = []

    with TestClient(app) as client:
        dates_response = client.get("/api/v1/configuration/analysis-dates")
        assert dates_response.status_code == 200, dates_response.text
        assert dates_response.json() == expected_dates

        for analysis_date in expected_dates:
            preview = client.get(
                "/api/v1/configuration/resolve",
                params={"analysis_date": analysis_date},
            )
            assert preview.status_code == 200, f"{analysis_date}: {preview.text}"
            selected_expiry = preview.json()["selected_expiry"]
            assert selected_expiry in preview.json()["available_expiries"]

            created = client.post(
                "/api/v1/analysis-runs",
                json={
                    "analysis_date": analysis_date,
                    "idempotency_key": f"phase3-real-archive-{analysis_date}-{uuid4().hex}",
                },
            )
            assert created.status_code == 201, f"{analysis_date}: {created.text}"
            run = created.json()
            assert run["status"] == "READY_FOR_PROCESSING"
            assert run["selected_expiry"] == selected_expiry
            assert run["source_provenance"]["manifest_validation"]["status"] == "VERIFIED"

            processed = client.post(f"/api/v1/analysis-runs/{run['id']}/process")
            assert processed.status_code == 200, f"{analysis_date}: {processed.text}"
            batch = processed.json()
            assert batch["status"] == "COMPLETED"
            assert batch["row_counts"]["index_rows"] == 1
            assert batch["row_counts"]["option_rows"] > 0
            total_options += batch["row_counts"]["option_rows"]

            data = client.get(f"/api/v1/analysis-runs/{run['id']}/processed-data")
            assert data.status_code == 200, f"{analysis_date}: {data.text}"
            payload = data.json()
            assert str(payload["trade_date"]) == analysis_date
            assert str(payload["selected_expiry"]) == selected_expiry
            assert payload["index_bar"]["close"] > 0
            assert payload["option_rows"]
            assert all(str(row["expiry"]) == selected_expiry for row in payload["option_rows"])
            assert {row["option_type"] for row in payload["option_rows"]} == {"CE", "PE"}
            assert all(math.isclose(row["underlying_close"], payload["index_bar"]["close"], rel_tol=0, abs_tol=1e-8) for row in payload["option_rows"])
            processed_runs.append(run["id"])

        assert len(processed_runs) == 22
        assert total_options > 0

    engine = get_engine()
    try:
        with Session(engine) as db:
            assert db.scalar(select(func.count()).select_from(AnalysisRun)) == 22
            assert db.scalar(select(func.count()).select_from(EodIngestionBatch)) == 22
            assert db.scalar(select(func.count()).select_from(Nifty50EodBar)) == 22
            assert db.scalar(select(func.count()).select_from(NiftyOptionEodBar)) == total_options
            assert db.scalar(
                select(func.count()).select_from(EodIngestionBatch).where(EodIngestionBatch.status == "COMPLETED")
            ) == 22
            assert db.scalar(
                select(func.count()).select_from(AnalysisRun).where(AnalysisRun.status == "PROCESSED")
            ) == 22
            stored_dates = list(db.scalars(select(Nifty50EodBar.trade_date).order_by(Nifty50EodBar.trade_date)))
            assert [value.isoformat() for value in stored_dates] == expected_dates
    finally:
        engine.dispose()
