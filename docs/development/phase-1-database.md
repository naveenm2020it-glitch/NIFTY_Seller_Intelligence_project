# Database integration milestone

- PostgreSQL connectivity through SQLAlchemy 2 and Psycopg 3.
- Alembic migration framework and an intentionally empty baseline revision.
- Separate API liveness and database readiness endpoints.
- CI uses a temporary PostgreSQL 16 service container.
- No database credentials, hosted database, or paid infrastructure are committed or required.

The next schema milestone depends on confirming the approved entities and relationships for source archives, contract-master snapshots, analysis runs, features, scenarios, reports, and feedback records.
