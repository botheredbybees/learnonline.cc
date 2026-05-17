---
name: new-migration
description: Generate a new Alembic migration for schema changes. Use when the user wants to add or modify tables, columns, indexes, or constraints in the database.
---

Generate a safe Alembic migration for this project. Follow these steps exactly.

## Step 1 — Understand current state
Read these files before touching anything:
- `backend/models/tables.py` — all SQLAlchemy ORM models
- The most recent file in `backend/alembic/versions/` — for style conventions
- `schema.sql` in the project root — for the reference schema

## Step 2 — Make the model change
Edit `backend/models/tables.py` to add or modify the model. Follow existing column patterns:
- UUIDs: `Column(postgresql.UUID(as_uuid=True), ...)`
- Timestamps: `Column(DateTime, server_default=func.now())`
- Foreign keys: use integer IDs consistent with existing relationships

## Step 3 — Generate the migration
```bash
cd backend
alembic revision --autogenerate -m "<short description of change>"
```

## Step 4 — Review the generated file (critical)
Open the new file in `backend/alembic/versions/` and check for:
- **NOT NULL columns on existing tables**: must have a `server_default` or the migration will fail on non-empty tables
- **UUID columns**: autogenerate sometimes misses the PostgreSQL-specific type; ensure `postgresql.UUID` not generic `String`
- **Missing imports**: add `from sqlalchemy.dialects import postgresql` if using UUID
- **Data migrations**: if renaming a column, write explicit up/down logic — autogenerate won't detect renames

## Step 5 — Apply
```bash
alembic upgrade head
```
If Docker is used: `docker-compose exec backend alembic upgrade head`

## Step 6 — Update schema.sql
If this is a structural change (new table, significant column addition), update `schema.sql` in the project root to reflect the new state. This file is the human-readable reference snapshot.
