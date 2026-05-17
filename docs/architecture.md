# LearnOnline.cc — Architecture

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Static HTML + jQuery 3.7.1 + Bootstrap 5.3.2 (no build step) |
| Backend | FastAPI (Python 3.11) |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Database | PostgreSQL 14 |
| Auth | JWT (python-jose) stored in localStorage |
| Dev environment | Docker Compose |
| Production target | Teacher's own Supabase (free tier) |

## Key Decisions

**Single database module:** All routers import `get_db` from `backend/database.py`. The module reads `DATABASE_URL` first, then falls back to individual `DB_*` vars. This makes Supabase deployment a one-line config change.

**Alembic is the schema authority:** `alembic upgrade head` creates all tables from scratch. `schema.sql` is a reference snapshot only. Do not use `schema_updates/*.sql` to set up a new database.

**Canonical models:** `backend/models/tables.py` is the only place ORM table definitions live. `models/schemas.py` holds Pydantic request/response models.

**Frontend:** Served by nginx. All API calls go to `/api` which nginx proxies to the FastAPI backend on port 8000. No build step — edit HTML/JS and refresh.

**Auth flow:** `POST /api/auth/login` returns a JWT. Client stores it in `localStorage` and passes it as `Authorization: Bearer <token>` on subsequent requests. Roles and permissions are baked into the token.

## Data Hierarchy

```
TrainingPackage
  └── Qualification / Skillset
        └── Unit
              └── UnitElement
                    └── UnitPerformanceCriteria
              └── UnitCriticalAspect  (Knowledge Evidence — M3 scenario source)
              └── UnitRequiredSkill
```

## Ports (local dev)

| Service | Host port |
|---------|-----------|
| Frontend (nginx) | 8080 |
| Backend (FastAPI) | 8000 |
| PostgreSQL | 5332 |
| PostgreSQL test | 5433 |
