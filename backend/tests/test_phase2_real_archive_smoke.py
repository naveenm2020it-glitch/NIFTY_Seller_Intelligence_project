"""Opt-in end-to-end smoke test against the verified Phase 1 archive and PostgreSQL.

Enabled only in the dedicated CI smoke job; ordinary unit tests remain isolated.
"""
import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app


pytestmark = pytest.mark.skipif(
    os.getenv("PHASE2_REAL_ARCHIVE_SMOKE") != "1",
    reason="real Phase 1 archive smoke test is opt-in",
)


def test_real_phase1_archive_and_postgres_persist_analysis_runs():
    with TestClient(app) as client:
        dates_response = client.get("/api/v1/configuration/analysis-dates")
        assert dates_response.status_code == 200, dates_response.text
        dates = dates_response.json()
        assert len(dates) == 22
        assert dates[0] == "2026-10-21"
        assert dates[-1] == "2026-11-19"

        # 17-Nov exercises the audited previous-session MII reconciliation path.
        # 19-Nov confirms the latest selected session is also usable end-to-end.
        for analysis_date in ("2026-11-17", "2026-11-19"):
            preview = client.get(
                "/api/v1/configuration/resolve",
                params={"analysis_date": analysis_date},
            )
            assert preview.status_code == 200, preview.text
            preview_data = preview.json()
            assert preview_data["selected_expiry"] in preview_data["available_expiries"]
            assert preview_data["expiry_selection_mode"] == "AUTO"

            idempotency_key = f"real-archive-{analysis_date}-{uuid4().hex}"
            created = client.post(
                "/api/v1/analysis-runs",
                json={
                    "analysis_date": analysis_date,
                    "idempotency_key": idempotency_key,
                },
            )
            assert created.status_code == 201, created.text
            run = created.json()
            assert run["status"] == "READY_FOR_PROCESSING"
            assert run["analysis_date"] == analysis_date
            assert run["selected_expiry"] == preview_data["selected_expiry"]
            assert run["expiry_selection_mode"] == "AUTO"
            assert run["source_provenance"]["coverage"]["complete"] is True
            assert run["source_provenance"]["manifest_validation"]["status"] == "VERIFIED"
            assert run["source_provenance"]["manifest_validation"]["verified_file_count"] >= 3
            assert run["source_provenance"]["content_checks"]["underlying_close_reconciled"] is True
            assert run["source_provenance"]["content_checks"]["nifty_option_rows"] > 0
            assert run["stage_results"][-1]["details"]["analytics_executed"] is False

            persisted = client.get(f"/api/v1/analysis-runs/{run['id']}")
            assert persisted.status_code == 200, persisted.text
            assert persisted.json()["id"] == run["id"]
            assert persisted.json()["status"] == "READY_FOR_PROCESSING"
            assert persisted.json()["source_provenance"] == run["source_provenance"]

            if analysis_date == "2026-11-17":
                assert any(
                    source["kind"] == "previous_session_mii_contract"
                    for source in run["source_provenance"]["sources"]
                )
