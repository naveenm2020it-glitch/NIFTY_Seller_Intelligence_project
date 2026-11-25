"""Opt-in end-to-end Phase 3 processing against the retained Phase 1 source artifact."""
import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.skipif(
    os.getenv("PHASE3_REAL_ARCHIVE_SMOKE") != "1",
    reason="full 22-session Phase 3 archive smoke test is opt-in",
)


def test_process_and_read_all_22_audited_sessions_from_postgres():
    with TestClient(app) as client:
        dates_response = client.get("/api/v1/configuration/analysis-dates")
        assert dates_response.status_code == 200, dates_response.text
        dates = dates_response.json()
        assert len(dates) == 22
        assert dates[0] == "2026-10-21"
        assert dates[-1] == "2026-11-19"

        processed_sessions = []
        total_option_rows = 0

        for analysis_date in dates:
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
                    "idempotency_key": f"phase3-22-session-{analysis_date}-{uuid4().hex}",
                },
            )
            assert created.status_code == 201, f"{analysis_date}: {created.text}"
            run = created.json()
            assert run["status"] == "READY_FOR_PROCESSING"
            assert run["selected_expiry"] == selected_expiry

            processed = client.post(f"/api/v1/analysis-runs/{run['id']}/process")
            assert processed.status_code == 200, f"{analysis_date}: {processed.text}"
            batch = processed.json()
            assert batch["status"] == "COMPLETED"
            assert batch["row_counts"]["index_rows"] == 1
            assert batch["row_counts"]["option_rows"] > 0
            assert len(batch["source_manifest"]) >= 3

            persisted = client.get(f"/api/v1/analysis-runs/{run['id']}/processed-data")
            assert persisted.status_code == 200, f"{analysis_date}: {persisted.text}"
            data = persisted.json()
            assert data["trade_date"] == analysis_date
            assert data["selected_expiry"] == selected_expiry
            assert data["index_bar"]["trade_date"] == analysis_date
            assert len(data["option_rows"]) == batch["row_counts"]["option_rows"]
            assert {row["option_type"] for row in data["option_rows"]} <= {"CE", "PE"}
            assert all(row["expiry"] == selected_expiry for row in data["option_rows"])
            assert all(
                abs(float(row["underlying_close"]) - float(data["index_bar"]["close"])) <= 1e-8
                for row in data["option_rows"]
            )

            processed_sessions.append(analysis_date)
            total_option_rows += len(data["option_rows"])

        assert len(processed_sessions) == 22
        assert len(set(processed_sessions)) == 22
        assert total_option_rows > 0
        print(
            {
                "processed_sessions": len(processed_sessions),
                "first_date": processed_sessions[0],
                "last_date": processed_sessions[-1],
                "persisted_option_rows": total_option_rows,
            }
        )
