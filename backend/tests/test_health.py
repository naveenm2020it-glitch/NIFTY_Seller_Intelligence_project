from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "application": "nifty-seller-intelligence",
    }


def test_database_health_check_without_configuration_returns_503(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    response = client.get("/health/database")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database connection unavailable."}
