# Database foundation

The application uses PostgreSQL through SQLAlchemy 2 and Psycopg 3. Alembic manages schema migrations.

## Configuration

Set `DATABASE_URL` in the repository-root `.env` file or runtime environment. The value must use the SQLAlchemy Psycopg URL format:

```text
postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

The backend loads the root `.env` file automatically when configuration is imported. Existing process environment variables take precedence. Never commit credentials.

## Migrations

Run from the `backend` directory:

```bash
alembic upgrade head
```

The initial revision is intentionally an empty baseline. Domain tables will be added only after the NIFTY analysis data model is agreed and documented; this avoids prematurely locking in an incomplete schema.

## Health checks

- `GET /health` reports API process health and does not require PostgreSQL.
- `GET /health/database` executes `SELECT 1` and returns HTTP 503 if PostgreSQL is unavailable.
- `GET /health/storage` checks the configured Backblaze B2 bucket and returns HTTP 503 if storage is unavailable or not configured.

GitHub Actions provisions a temporary PostgreSQL service for validation. It is destroyed when the workflow runner ends; it is not a persistent application database.
