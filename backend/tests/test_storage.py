from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import b2

client = TestClient(app)


def _set_b2_environment(monkeypatch) -> None:
    monkeypatch.setenv("B2_ENDPOINT_URL", "https://s3.us-west-004.backblazeb2.com")
    monkeypatch.setenv("B2_REGION", "us-west-004")
    monkeypatch.setenv("B2_BUCKET_NAME", "nifty-test-bucket")
    monkeypatch.setenv("B2_APPLICATION_KEY_ID", "test-key-id")
    monkeypatch.setenv("B2_APPLICATION_KEY", "test-application-key")


def test_b2_connection_requires_all_configuration(monkeypatch) -> None:
    for name in ("B2_ENDPOINT_URL", "B2_REGION", "B2_BUCKET_NAME", "B2_APPLICATION_KEY_ID", "B2_APPLICATION_KEY"):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(RuntimeError, match="Backblaze B2 configuration is incomplete"):
        b2.get_b2_settings()


def test_b2_connection_uses_s3_compatible_endpoint(monkeypatch) -> None:
    _set_b2_environment(monkeypatch)
    calls = {}

    class FakeClient:
        def head_bucket(self, **kwargs):
            calls["head_bucket"] = kwargs

    def fake_client(service_name, **kwargs):
        calls["service_name"] = service_name
        calls["client_options"] = kwargs
        return FakeClient()

    monkeypatch.setattr(b2.boto3, "client", fake_client)

    assert b2.check_b2_connection() is True
    assert calls["service_name"] == "s3"
    assert calls["client_options"]["endpoint_url"] == "https://s3.us-west-004.backblazeb2.com"
    assert calls["client_options"]["region_name"] == "us-west-004"
    assert calls["head_bucket"] == {"Bucket": "nifty-test-bucket"}


def test_b2_file_operations_use_configured_bucket(monkeypatch, tmp_path: Path) -> None:
    _set_b2_environment(monkeypatch)
    calls = []

    class FakeClient:
        def upload_file(self, filename, bucket, key):
            calls.append(("upload", filename, bucket, key))

        def download_file(self, bucket, key, filename):
            calls.append(("download", bucket, key, filename))

        def delete_object(self, **kwargs):
            calls.append(("delete", kwargs))

    monkeypatch.setattr(b2.boto3, "client", lambda *args, **kwargs: FakeClient())
    source = tmp_path / "source.csv"
    source.write_text("date,close\n2026-11-20,26000\n", encoding="utf-8")
    destination = tmp_path / "downloads" / "source.csv"

    b2.upload_file(source, "raw/source.csv")
    b2.download_file("raw/source.csv", destination)
    b2.delete_file("raw/source.csv")

    assert calls == [
        ("upload", str(source), "nifty-test-bucket", "raw/source.csv"),
        ("download", "nifty-test-bucket", "raw/source.csv", str(destination)),
        ("delete", {"Bucket": "nifty-test-bucket", "Key": "raw/source.csv"}),
    ]
    assert destination.parent.is_dir()


def test_storage_health_returns_503_when_b2_is_not_configured(monkeypatch) -> None:
    for name in ("B2_ENDPOINT_URL", "B2_REGION", "B2_BUCKET_NAME", "B2_APPLICATION_KEY_ID", "B2_APPLICATION_KEY"):
        monkeypatch.delenv(name, raising=False)

    response = client.get("/health/storage")

    assert response.status_code == 503
    assert response.json() == {"detail": "Object storage connection unavailable."}


def test_storage_health_returns_ok_when_b2_is_available(monkeypatch) -> None:
    monkeypatch.setattr("app.main.check_b2_connection", lambda: True)

    response = client.get("/health/storage")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "storage": "connected"}
