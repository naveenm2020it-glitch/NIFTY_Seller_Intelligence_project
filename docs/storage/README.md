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

## Automated live connectivity verification

The Phase 0 GitHub Actions workflow supports an optional, read-only live bucket check. Add the following five repository Actions secrets under **Settings → Secrets and variables → Actions**:

- `B2_ENDPOINT_URL`
- `B2_REGION`
- `B2_BUCKET_NAME`
- `B2_APPLICATION_KEY_ID`
- `B2_APPLICATION_KEY`

Use a bucket-restricted application key. The workflow runs `HeadBucket` only; it does not upload, download, delete, create a bucket or change bucket contents. If no B2 values are configured, the live check is skipped and the mocked integration tests still run. If only some values are configured, the check fails so incomplete configuration is not mistaken for success.

Do not paste application keys into chat or commit them to GitHub. Enter them directly into GitHub Actions secrets. B2 usage may incur storage and transaction charges according to the account's current pricing; no bucket or paid resource is created by this repository.

## Verification boundary

Automated tests use a mocked S3-compatible client. They verify configuration handling, endpoint selection, bucket selection, and the upload/download/delete calls without requiring real credentials or creating billable resources.

**Live connectivity status: verified.** GitHub Actions run [#15 — Phase 0 Foundation CI](https://github.com/naveenm2020it-glitch/NIFTY_Seller_Intelligence_project/actions/runs/44709767148) completed successfully on 20 November 2026, including the workflow step **Verify live Backblaze B2 connectivity when credentials are configured**. That step verifies bucket reachability with `HeadBucket`; it does not verify file upload/download/delete behavior against the live bucket.

Raw NSE report collection, retention policy, and ingestion workflows are intentionally outside Phase 0.
