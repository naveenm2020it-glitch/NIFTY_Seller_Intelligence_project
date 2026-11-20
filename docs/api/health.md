# System health API

All endpoints are read-only checks. They do not modify application or market data.

| Method | Path | Success response | Failure response |
|---|---|---|---|
| GET | `/health` | HTTP 200 with API process status | Not applicable |
| GET | `/health/database` | HTTP 200 when PostgreSQL answers `SELECT 1` | HTTP 503 when the database is unavailable or not configured |
| GET | `/health/storage` | HTTP 200 when the configured B2 bucket is reachable | HTTP 503 when B2 is not configured or unavailable |

The storage health endpoint checks connectivity only. It does not upload, download or delete objects. The database health endpoint does not create or migrate tables; Alembic migrations are run separately.
