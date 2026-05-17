# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LearnOnline.cc is a solo passion project: a gamified, student-facing vocational training platform built on Australian Quality Training Framework (AQTF) data. It is designed to be **self-hosted by individual teachers** — each teacher provisions their own free Supabase account (or local Postgres), runs the app via Docker, and loads only the units they teach via the admin UI.

The active roadmap is a four-milestone plan. See the full spec at:
`docs/superpowers/specs/2026-05-17-learnonline-roadmap-design.md`

| Milestone | Focus | Status |
|-----------|-------|--------|
| M1 — Clean Slate | Delete dead code, fix schema, write setup guide | **Plan written — ready to execute** |
| M2 — Quiz MVP | Wire AQTF units → quizzes → XP/badges | Planned |
| M3 — Game Engine Alpha | Card-based competency game | Planned |
| M4 — Adaptive Loop + SCORM | Gap analysis + SCORM 1.2 export | Planned |

**M1 implementation plan:** `docs/superpowers/plans/2026-05-17-m1-clean-slate.md`

To execute M1 in a fresh context window, say:
> "Execute the M1 Clean Slate plan at docs/superpowers/plans/2026-05-17-m1-clean-slate.md"

## Architecture

```
learnonline.cc/
├── backend/              # FastAPI (Python) REST API
│   ├── main.py           # App entry point, router registration
│   ├── database.py       # SQLAlchemy engine + get_db() — PRIMARY database module
│   ├── models/
│   │   ├── tables.py     # CANONICAL ORM models (all tables defined here)
│   │   ├── base.py       # Base + TimestampMixin
│   │   └── schemas.py    # Pydantic request/response schemas
│   ├── routers/          # One file per resource (auth, units, gamification, etc.)
│   ├── services/         # Business logic; tga/ subpackage for TGA SOAP client
│   ├── auth/             # JWT bearer + handler (sign_jwt, get_password_hash)
│   ├── game_engine/      # Card-based learning engine (M3 — not yet implemented)
│   ├── alembic/          # DB migrations — single source of schema truth
│   └── tests/            # pytest suite (requires running Postgres)
├── frontend/             # Static HTML + vanilla JS/jQuery, served via nginx
│   ├── *.html            # One file per page (index, dashboard, admin, etc.)
│   ├── js/api.js         # Shared API client
│   ├── static/           # css/, images/, js/
│   └── nginx.conf        # Reverse proxy: /api → FastAPI backend
├── docs/
│   ├── superpowers/specs/  # Design specs (start here for context)
│   └── assessment_gameplay/ # Game engine design docs (relevant for M3)
├── schema.sql            # Reference snapshot only — do not use for migrations
├── docker-compose.yml    # Dev stack (frontend :8080, backend :8000, db :5332)
└── docker-compose.test.yml  # Test stack (postgres-test on :5433)
```

### Key Architecture Decisions

- **Frontend**: Vanilla HTML + jQuery 3.7.1 + Bootstrap 5.3.2. No build step. Nginx serves static files and proxies `/api` to FastAPI.
- **Auth**: JWT tokens in `localStorage`. `auth/auth_handler.py` signs tokens with roles baked in. Role-based access enforced per-router via `Depends()`.
- **Database**: PostgreSQL with SQLAlchemy ORM. `models/tables.py` is the only place table definitions live. `backend/database.py` is the only database module — `backend/db/` is dead code scheduled for deletion in M1.
- **Schema management**: Alembic is the single source of truth. `alembic upgrade head` creates the full schema from scratch. `schema.sql` and `schema_updates/` are reference artifacts only.
- **Deployment target**: Supabase free-tier Postgres. `DATABASE_URL` is the primary connection config — no need for separate `DB_USER`, `DB_HOST` etc. when pointing at Supabase.
- **TGA Integration**: SOAP client in `services/tga/client.py` fetches XML from training.gov.au. XML parsed with BeautifulSoup; hierarchy is training packages → qualifications → units → elements → performance criteria.
- **Testing**: Tests run against a real PostgreSQL instance (not mocked). `ENVIRONMENT=test` suppresses `create_all()` in `main.py`; conftest handles schema setup.

### Dead Code (M1 cleanup targets)

These files exist but should not be referenced — they are scheduled for deletion in M1:

| Path | Why it's dead |
|------|--------------|
| `backend/models/tables_old.py` | UUID-era models, superseded by `tables.py` |
| `backend/models/favorites.py` | UUID-based Pydantic schemas, never wired up |
| `backend/models/user.py` | UUID-based Pydantic user model, superseded |
| `backend/db/` | Duplicate `database.py`, unused |
| `streamlit/` | Empty shell |
| `legacy_test_scripts/` | Dead exploratory scripts |
| `schema_old.sql` | Old backup |
| `debug_auth.py` (root) | One-off debug script |

## Development Commands

### Start Dev Environment (Docker)
```bash
docker-compose up --build        # First time or after dependency changes
docker-compose up                # Subsequent starts
```
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000/docs (Swagger)
- DB: localhost:5332

### Supabase Deployment
Set a single env var in `.env`:
```
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```
Then `docker-compose up` — no local Postgres container needed (comment out the `db` service).

### Backend (without Docker)
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations
```bash
cd backend
alembic upgrade head                              # Apply all migrations (fresh install)
alembic revision --autogenerate -m "description" # Generate new migration
```

### Running Tests
```bash
./run_tests.sh setup       # Start postgres-test container
./run_tests.sh unit        # All unit tests
./run_tests.sh auth        # Authentication tests
./run_tests.sh tga         # TGA integration tests
./run_tests.sh coverage    # HTML coverage report

# Single test file
cd backend
DATABASE_URL=postgresql://test_user:test_password@localhost:5433/learnonline_test \
  ENVIRONMENT=test pytest tests/test_auth.py -v
```

### TGA XML Utilities
```bash
python backend/scripts/tga_utils.py parse --unit PUAAMS101   # Parse a unit
python backend/scripts/tga_utils.py process-local            # Process local XML files
```

## Environment Configuration

Copy `env_example.txt` to `.env`. Minimum required:
```
DATABASE_URL=postgresql://...    # Primary — use this for Supabase
SECRET_KEY=...                   # JWT signing key
TGA_USERNAME=WebService.Read     # TGA SOAP credentials (public read-only)
TGA_PASSWORD=Asdf098
```

Legacy individual `DB_NAME` / `DB_USER` / etc. vars still work as fallback but are not needed when `DATABASE_URL` is set.

## Admin Access

```bash
docker-compose exec db psql -U postgres -d learnonline -c "
INSERT INTO users (email, username, password_hash, first_name, last_name, is_active)
VALUES ('admin@example.com', 'admin', crypt('adminpassword', gen_salt('bf')), 'Admin', 'User', true);
"
```
Then assign the admin role. Admin UI: http://localhost:8080/admin.

## Gamification System

XP, levels, achievements, and badges:
- `backend/routers/gamification.py`, `achievements.py`, `badges.py`, `user_progress.py`
- `backend/models/tables.py` — `UserProfile`, `Achievement`, `Badge`, `UserAchievement`

## TGA Integration Notes

- TGA WebServiceKit XML files → `tgaWebServiceKit-2021-12-01/` in project root (not in git).
- SOAP credentials in `env_example.txt` are public read-only — no account needed.
- XML hierarchy: training packages → qualifications/skillsets → units → elements → performance criteria → knowledge evidence.
