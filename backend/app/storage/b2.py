import os
from dataclasses import dataclass
from pathlib import Path

import boto3
from botocore.config import Config


@dataclass(frozen=True)
class B2Settings:
    endpoint_url: str
    region: str
    bucket_name: str
    application_key_id: str
    application_key: str


def get_b2_settings() -> B2Settings:
    values = {
        "B2_ENDPOINT_URL": os.getenv("B2_ENDPOINT_URL"),
        "B2_REGION": os.getenv("B2_REGION"),
        "B2_BUCKET_NAME": os.getenv("B2_BUCKET_NAME"),
        "B2_APPLICATION_KEY_ID": os.getenv("B2_APPLICATION_KEY_ID"),
        "B2_APPLICATION_KEY": os.getenv("B2_APPLICATION_KEY"),
    }
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError("Backblaze B2 configuration is incomplete: " + ", ".join(missing))
    if not values["B2_ENDPOINT_URL"].startswith("https://"):
        raise RuntimeError("B2_ENDPOINT_URL must use HTTPS.")
    return B2Settings(
        endpoint_url=values["B2_ENDPOINT_URL"],
        region=values["B2_REGION"],
        bucket_name=values["B2_BUCKET_NAME"],
        application_key_id=values["B2_APPLICATION_KEY_ID"],
        application_key=values["B2_APPLICATION_KEY"],
    )


def _get_client_and_settings():
    settings = get_b2_settings()
    client = boto3.client(
        "s3",
        endpoint_url=settings.endpoint_url,
        region_name=settings.region,
        aws_access_key_id=settings.application_key_id,
        aws_secret_access_key=settings.application_key,
        config=Config(signature_version="s3v4"),
    )
    return client, settings


def check_b2_connection() -> bool:
    client, settings = _get_client_and_settings()
    client.head_bucket(Bucket=settings.bucket_name)
    return True


def upload_file(file_path: str | Path, object_key: str) -> None:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    if not object_key.strip():
        raise ValueError("object_key must not be empty.")
    client, settings = _get_client_and_settings()
    client.upload_file(str(path), settings.bucket_name, object_key)


def download_file(object_key: str, destination_path: str | Path) -> None:
    if not object_key.strip():
        raise ValueError("object_key must not be empty.")
    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    client, settings = _get_client_and_settings()
    client.download_file(settings.bucket_name, object_key, str(destination))


def delete_file(object_key: str) -> None:
    if not object_key.strip():
        raise ValueError("object_key must not be empty.")
    client, settings = _get_client_and_settings()
    client.delete_object(Bucket=settings.bucket_name, Key=object_key)
