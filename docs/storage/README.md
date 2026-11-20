# Backblaze B2 object storage

The backend uses Backblaze B2 through its S3-compatible API and the AWS SDK for Python (Boto3). The integration is configured entirely through environment variables; credentials are never stored in source control.

## Required configuration

Set these values in the local untracked `.env` file or the deployment environment:

| Variable | Purpose |
|---|---|
| `B2_ENDPOINT_URL` | S3-compatible endpoint for the bucket's region, for example `https://s3.us-west-004.backblazeb2.com` |
| `B2_REGION` | Region identifier for the bucket |
| `B2_BUCKET_NAME` | Existing B2 bucket name |
| `B2_APPLICATION_KEY_ID` | Application key ID |
| `B2_APPLICATION_KEY` | Application key secret |

Create the bucket in Backblaze before configuring the application. Use a bucket-restricted application key and grant only the capabilities needed by the application. The Phase 0 connection check uses `HeadBucket`; file operations use the S3-compatible upload, download and delete APIs.

## Backend interface

- `check_b2_connection()`: verifies that the configured bucket is reachable.
- `upload_file(file_path, object_key)`: uploads a local file.
- `download_file(object_key, destination_path)`: downloads an object and creates the destination directory if needed.
- `delete_file(object_key)`: deletes an object.

The `GET /health/storage` endpoint reports whether the configured bucket is reachable. It returns HTTP 503 when B2 is not configured or cannot be reached. It does not expose credentials or provider error details.

## Verification boundary

Automated tests use a mocked S3-compatible client. They verify configuration handling, endpoint selection, bucket selection, and the upload/download/delete calls without requiring real credentials or creating billable resources.

A live connection has not been verified until the owner configures a real bucket and application key in a trusted runtime. Do not paste application keys into chat or commit them to GitHub. B2 usage may incur storage and transaction charges according to the account's current pricing; no bucket or paid resource is created by this repository.

Raw NSE report collection, retention policy, and ingestion workflows are intentionally outside Phase 0.
