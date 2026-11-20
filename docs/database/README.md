# Database foundation

The application uses PostgreSQL through SQLAlchemy 2 and Psycopg 3. Alembic manages schema migrations.

## Configuration

Set `DATABASE_URL` in the runtime environment. The value must use the SQLAlchemy Psycopg URL format:

```text
postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

For local development, put the real value in an untracked `.env` file and never commit credentials. The current application configuration reads `DATABASE_URL` from the process environment; loading `.env` automatically is not currently configured. Export the variable in the shell or configure it in the execution environment.

## Migrations

Run from the `backend` directory:

```bash
alembic upgrade head
```

The initial revision is intentionally an empty baseline. Domain tables will be added only after the NIFTY analysis data model is agreed and documented; this avoids prematurely locking in an incomplete schema.

## Health checks

- `GET /health` reports API process health and does not require PostgreSQL.
- `GET /health/database` executes `SELECT 1` and returns HTTP 503 if PostgreSQL is unavailable.

GitHub Actions provisions a temporary PostgreSQL service for validation. It is destroyed when the workflow runner ends; it is not a persistent application database.
