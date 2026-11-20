# Database foundation

The application uses PostgreSQL through SQLAlchemy 2 and Psycopg 3. Alembic manages schema migrations.

## Configuration

Set `DATABASE_URL` in the runtime environment. The value must use the SQLAlchemy Psycopg URL format:

```text
postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

Do not commit real credentials. Keep local values in an untracked `.env` file or configure secrets in the deployment environment.

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
