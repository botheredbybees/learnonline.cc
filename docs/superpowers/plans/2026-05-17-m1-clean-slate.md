# M1: Clean Slate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Delete dead code, consolidate the database module, fix broken imports, repair the Alembic migration, and produce a repo that a teacher can clone → configure → run in under 15 minutes.

**Architecture:** FastAPI backend connects to Postgres via a single `backend/database.py` module. All routers import `get_db` from there. Alembic is the sole schema authority — `alembic upgrade head` on a fresh DB (including Supabase) creates all tables. Docker Compose is the local dev path; Supabase is the self-hosted teacher deployment target.

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL 14, Docker Compose, nginx

---

## File Map

**Modify:**
- `backend/database.py` — verify DATABASE_URL is primary config, export `DATABASE_URL` and `SessionLocal`
- `backend/auth/auth_handler.py:11` — fix import
- `backend/routers/achievements.py:23` — fix import
- `backend/routers/assessments.py:20` — fix import
- `backend/routers/auth.py:41` — fix import
- `backend/routers/badges.py:23` — fix import
- `backend/routers/permissions.py:13` — fix import
- `backend/routers/qualifications.py:20` — fix import
- `backend/routers/roles.py:13` — fix import
- `backend/routers/skillsets.py:20` — fix import
- `backend/routers/training_packages.py:18` — fix import
- `backend/routers/units.py:16,40` — fix imports (get_db + SessionLocal)
- `backend/routers/users.py:22` — fix import
- `backend/routers/user_progress.py:22` — fix import
- `backend/scripts/populate_roles.py:12` — fix import
- `backend/services/download_manager.py:17` — fix import
- `backend/main.py` — remove duplicate standalone routes + dead Pydantic models
- `backend/alembic/versions/001_initial_migration.py` — replace with integer-ID migration matching current `tables.py`
- `docker-compose.yml` — add `DATABASE_URL` to backend environment
- `env_example.txt` — strip to 8 essential variables
- `README.md` — rewrite as 10-minute teacher setup guide

**Delete:**
- `backend/db/` (directory) — superseded by `backend/database.py`
- `backend/models/tables_old.py` — UUID-era models
- `backend/models/favorites.py` — UUID-era Pydantic schemas, never wired up
- `backend/models/user.py` — UUID-era Pydantic user model
- `backend/models/c__/` (directory) — stray Windows artifact
- `backend/routers/quiz.py` — broken: imports non-existent `models.quiz`, unregistered
- `backend/run_auth_tests.py` — superseded by `run_tests.sh`
- `backend/check_units.py` — one-off exploration script
- `debug_auth.py` (root) — one-off debug script
- `legacy_test_scripts/` (directory) — dead exploratory scripts
- `streamlit/` (directory) — empty shell
- `schema_old.sql` — old backup
- `docs/ui_planning/quiz.html` — exploratory prototype

**Create:**
- `docs/archive/` (directory) — stale docs moved here, not deleted
- `docs/concept.md` — product vision (condensed from `learnonline_concept.md`)
- `docs/architecture.md` — technical decisions
- `docs/aqtf.md` — AQTF data model and TGA sync guide

---

## Task 1: Verify and complete `backend/database.py`

`backend/database.py` is the correct database module (supports `DATABASE_URL`), but it needs to export `DATABASE_URL` and `SessionLocal` for files that currently pull those from `backend/db/database.py`.

**Files:** Modify `backend/database.py`

- [ ] **Step 1: Read the current file**

```bash
cat backend/database.py
```

- [ ] **Step 2: Verify it exports DATABASE_URL and SessionLocal at module level**

The file must have:
```python
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5332')
    DB_NAME = os.getenv('DB_NAME', 'learnonline')
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

If `DATABASE_URL` is defined only inside an `if not DATABASE_URL` block (not at module level), move it outside so it is always importable. The final version must export `DATABASE_URL`, `SessionLocal`, `engine`, and `get_db`.

- [ ] **Step 3: Smoke-test the module**

```bash
cd backend
DATABASE_URL=postgresql://postgres:postgres@localhost:5332/learnonline python -c "
from database import get_db, engine, DATABASE_URL, SessionLocal
print('database.py OK:', DATABASE_URL[:30])
"
```

Expected output: `database.py OK: postgresql://postgres:postgres@`

- [ ] **Step 4: Commit**

```bash
git add backend/database.py
git commit -m "fix: ensure database.py exports DATABASE_URL and SessionLocal"
```

---

## Task 2: Fix imports in all routers and services

Every router except `gamification.py` currently imports from `db.database` (the duplicate module). Fix them all to import from `database` before deleting `backend/db/`.

**Files:** 15 files — see list below

- [ ] **Step 1: Confirm the broken imports**

```bash
cd backend
grep -rn "from db.database\|from \.\.db\.database" . --include="*.py" | grep -v __pycache__
```

Expected: 15 lines across routers, auth, and services.

- [ ] **Step 2: Bulk-fix the absolute imports**

```bash
cd backend
# Fix "from db.database import X" → "from database import X" in all files
find . -name "*.py" -not -path "./__pycache__/*" \
  -exec sed -i 's/from db\.database import/from database import/g' {} +
```

- [ ] **Step 3: Fix the one relative import (quiz.py uses ..db.database)**

```bash
cd backend
grep -rn "from \.\.db\.database" . --include="*.py" | grep -v __pycache__
```

If `quiz.py` appears (it uses `from ..db.database import get_db`), that router is broken and unregistered anyway — it will be deleted in Task 5. No fix needed here.

- [ ] **Step 4: Verify no remaining db.database imports**

```bash
cd backend
grep -rn "from db\.database\|from \.\.db\.database" . --include="*.py" | grep -v __pycache__
```

Expected: no output (or only `quiz.py` which will be deleted).

- [ ] **Step 5: Verify app imports cleanly**

```bash
cd backend
DATABASE_URL=postgresql://postgres:postgres@localhost:5332/learnonline \
  python -c "from main import app; print('main.py imports OK')"
```

Expected: `main.py imports OK` (no ImportError)

- [ ] **Step 6: Commit**

```bash
git add -u
git commit -m "fix: migrate all router imports from db.database to database"
```

---

## Task 3: Delete `backend/db/` directory

Safe to delete now that all imports have been fixed.

**Files:** Delete `backend/db/`

- [ ] **Step 1: Confirm nothing imports from backend/db/ any more**

```bash
grep -rn "from db\." backend/ --include="*.py" | grep -v __pycache__ | grep -v quiz.py
```

Expected: no output.

- [ ] **Step 2: Delete the directory**

```bash
rm -rf backend/db/
```

- [ ] **Step 3: Verify app still imports cleanly**

```bash
cd backend
DATABASE_URL=postgresql://postgres:postgres@localhost:5332/learnonline \
  python -c "from main import app; print('main.py imports OK after deleting db/')"
```

Expected: `main.py imports OK after deleting db/`

- [ ] **Step 4: Commit**

```bash
git add -u
git rm -r backend/db/
git commit -m "chore: delete duplicate backend/db/ database module"
```

---

## Task 4: Delete dead model files

**Files:** Delete `tables_old.py`, `favorites.py`, `user.py`, `c__/`

- [ ] **Step 1: Confirm nothing imports these**

```bash
cd backend
grep -rn "from models.favorites\|from models.user\|from models.tables_old\|models\.c__" . \
  --include="*.py" | grep -v __pycache__
```

Expected: no output.

- [ ] **Step 2: Delete the files**

```bash
rm backend/models/tables_old.py
rm backend/models/favorites.py
rm backend/models/user.py
rm -rf backend/models/c__/
```

- [ ] **Step 3: Verify app still imports cleanly**

```bash
cd backend
DATABASE_URL=postgresql://postgres:postgres@localhost:5332/learnonline \
  python -c "from main import app; print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git rm backend/models/tables_old.py backend/models/favorites.py backend/models/user.py
git rm -r backend/models/c__/
git commit -m "chore: delete UUID-era dead model files"
```

---

## Task 5: Delete broken router and dead scripts

**Files:** Delete `quiz.py`, `run_auth_tests.py`, `check_units.py`, `debug_auth.py`, `legacy_test_scripts/`, `streamlit/`, `schema_old.sql`, `docs/ui_planning/quiz.html`

- [ ] **Step 1: Confirm quiz router is not registered**

```bash
grep -n "quiz" backend/main.py backend/routers/__init__.py
```

Expected: no output (quiz is not imported or registered anywhere).

- [ ] **Step 2: Delete the files and directories**

```bash
rm backend/routers/quiz.py
rm backend/run_auth_tests.py
rm backend/check_units.py
rm debug_auth.py
rm -rf legacy_test_scripts/
rm -rf streamlit/
rm schema_old.sql
rm docs/ui_planning/quiz.html
```

- [ ] **Step 3: Verify app still imports cleanly**

```bash
cd backend
DATABASE_URL=postgresql://postgres:postgres@localhost:5332/learnonline \
  python -c "from main import app; print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git rm backend/routers/quiz.py backend/run_auth_tests.py backend/check_units.py \
  debug_auth.py schema_old.sql docs/ui_planning/quiz.html
git rm -r legacy_test_scripts/ streamlit/
git commit -m "chore: delete broken quiz router, dead scripts, and empty shells"
```

---

## Task 6: Fix `main.py` — remove duplicate standalone routes

`main.py` defines `/training-packages/` and `/units/` as standalone routes alongside its routers. These shadow the router endpoints and include stale `TrainingPackageBase` and `UnitBase` Pydantic classes that belong in `models/schemas.py`.

**Files:** Modify `backend/main.py`

- [ ] **Step 1: Identify the duplicate routes**

```bash
grep -n "def list_training_packages\|def list_units\|TrainingPackageBase\|UnitBase\|@app.get" backend/main.py
```

- [ ] **Step 2: Remove the duplicate Pydantic models and routes**

Open `backend/main.py` and delete:
- The `TrainingPackageBase` class (Pydantic model defined inline)
- The `UnitBase` class (Pydantic model defined inline)
- The `@app.get("/training-packages/")` route and its `list_training_packages` function
- The `@app.get("/units/")` route and its `list_units` function
- The unused `from models.tables import TrainingPackage, Unit` import (if no longer needed)
- The unused `from pydantic import BaseModel, ConfigDict` import (if no longer needed after removing the Pydantic classes)

Keep: all `app.include_router(...)` calls, the CORS middleware, health check endpoints `/` and `/api`.

- [ ] **Step 3: Verify the router endpoints still work**

```bash
cd backend
DATABASE_URL=postgresql://postgres:postgres@localhost:5332/learnonline \
  python -c "
from main import app
routes = [r.path for r in app.routes]
assert '/api/training-packages/' in routes or any('training' in r for r in routes), 'router routes missing'
print('routes OK')
print([r for r in routes if 'training' in r or 'unit' in r])
"
```

- [ ] **Step 4: Commit**

```bash
git add backend/main.py
git commit -m "fix: remove duplicate standalone routes from main.py"
```

---

## Task 7: Clean up `env_example.txt` and update `docker-compose.yml`

`env_example.txt` currently references Redis, MinIO, Prometheus, Elasticsearch, Streamlit — none of which are used. Strip it down. Also add `DATABASE_URL` to the backend service in `docker-compose.yml`.

**Files:** Modify `env_example.txt`, modify `docker-compose.yml`

- [ ] **Step 1: Replace env_example.txt**

Write the following as the complete new content of `env_example.txt`:

```
# LearnOnline.cc Environment Configuration
# Copy to .env and fill in values.

# ── Database ──────────────────────────────────────────────────────────────────
# Option A (recommended for Supabase): set DATABASE_URL and leave the rest blank
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres

# Option B (local Docker dev): set individual vars; DATABASE_URL takes priority if set
DB_HOST=db
DB_PORT=5432
DB_NAME=learnonline
DB_USER=postgres
DB_PASSWORD=postgres

# ── Auth ──────────────────────────────────────────────────────────────────────
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=devsecrethardtoguess

# ── TGA SOAP API ──────────────────────────────────────────────────────────────
# These are the public read-only credentials — no account needed
TGA_USERNAME=WebService.Read
TGA_PASSWORD=Asdf098
```

- [ ] **Step 2: Add DATABASE_URL to docker-compose.yml backend service**

In `docker-compose.yml`, find the `backend:` service `environment:` block. Add `DATABASE_URL` as the first entry:

```yaml
environment:
  - DATABASE_URL=${DATABASE_URL:-postgresql://postgres:${DB_PASSWORD:-postgres}@db:5432/${DB_NAME:-learnonline}}
  - DB_NAME=${DB_NAME:-learnonline}
  - DB_USER=${DB_USER:-postgres}
  - DB_PASSWORD=${DB_PASSWORD:-postgres}
  - DB_HOST=db
  - DB_PORT=5432
  - SECRET_KEY=${SECRET_KEY:-devsecrethardtoguess}
  - ALGORITHM=HS256
  - ACCESS_TOKEN_EXPIRE_MINUTES=30
  - PYTHONUNBUFFERED=1
```

- [ ] **Step 3: Verify docker-compose config is valid**

```bash
docker-compose config --quiet && echo "docker-compose.yml is valid"
```

Expected: `docker-compose.yml is valid`

- [ ] **Step 4: Commit**

```bash
git add env_example.txt docker-compose.yml
git commit -m "fix: simplify env_example.txt and add DATABASE_URL to docker-compose backend"
```

---

## Task 8: Replace Alembic migration 001 with integer-ID schema

The current `001_initial_migration.py` uses PostgreSQL UUID columns for `users.id` and `user_profiles.id`. The current `models/tables.py` uses `Integer`. Running `alembic upgrade head` on a fresh DB currently produces a schema incompatible with the ORM. Replace the migration with one autogenerated from the current models.

**Files:** Delete and replace `backend/alembic/versions/001_initial_migration.py`

- [ ] **Step 1: Start the local Docker database only**

```bash
docker-compose up -d db
# Wait for it to be healthy
docker-compose ps db
```

Expected: `db` service shows `healthy`.

- [ ] **Step 2: Delete the old migration**

```bash
rm backend/alembic/versions/001_initial_migration.py
```

- [ ] **Step 3: Autogenerate a fresh migration from current models**

```bash
cd backend
DATABASE_URL=postgresql://postgres:postgres@localhost:5332/learnonline \
  alembic revision --autogenerate -m "initial schema"
```

This connects to the empty DB, compares it against `models/tables.py`, and generates a migration creating all tables. A file like `backend/alembic/versions/xxxx_initial_schema.py` will be created.

- [ ] **Step 4: Review the generated migration**

```bash
ls backend/alembic/versions/
cat backend/alembic/versions/*initial_schema*.py | grep "op.create_table\|op.drop_table" | head -30
```

Verify you see `create_table` calls for: `roles`, `permissions`, `role_permissions`, `users`, `user_profiles`, `training_packages`, `units`, `unit_elements`, `unit_performance_criteria`, `unit_critical_aspects`, `unit_required_skills`, `qualifications`, `skillsets`, `user_progress`, `assessments`, `assessment_questions`, `user_submissions`, `achievements`, `user_achievements`, `badges`, `user_badges`.

Verify NO UUID columns appear in `users` or `user_profiles` — they should be `Integer`.

- [ ] **Step 5: Test the migration on a fresh database**

```bash
# Drop and recreate the test database to get a blank slate
docker-compose exec db psql -U postgres -c "DROP DATABASE IF EXISTS learnonline_fresh; CREATE DATABASE learnonline_fresh;"

cd backend
DATABASE_URL=postgresql://postgres:postgres@localhost:5332/learnonline_fresh \
  alembic upgrade head
```

Expected: Alembic applies the migration with no errors.

- [ ] **Step 6: Verify all expected tables exist**

```bash
docker-compose exec db psql -U postgres -d learnonline_fresh -c "\dt"
```

Expected: 21 tables listed (roles, users, user_profiles, training_packages, units, etc.)

- [ ] **Step 7: Clean up the test database**

```bash
docker-compose exec db psql -U postgres -c "DROP DATABASE learnonline_fresh;"
```

- [ ] **Step 8: Handle existing local dev database (if you have data)**

If your local `learnonline` database already has tables (from the old init script), tell Alembic it is already up to date so it does not try to re-create tables:

```bash
cd backend
DATABASE_URL=postgresql://postgres:postgres@localhost:5332/learnonline \
  alembic stamp head
```

- [ ] **Step 9: Commit**

```bash
git rm backend/alembic/versions/001_initial_migration.py 2>/dev/null || true
git add backend/alembic/versions/
git commit -m "fix: replace UUID-era alembic migration with integer-ID schema from current models"
```

---

## Task 9: Archive stale documentation and create lean doc structure

**Files:** Create `docs/archive/`, move stale docs, create `docs/concept.md`, `docs/architecture.md`, `docs/aqtf.md`

- [ ] **Step 1: Create archive directory and move stale docs**

```bash
mkdir -p docs/archive

# Move stale technical docs
mv docs/technical docs/archive/technical

# Move stale UI planning docs (keep rpg_city_map_navigation.html for M3 reference)
mkdir -p docs/archive/ui_planning
mv docs/ui_planning/* docs/archive/ui_planning/ 2>/dev/null || true
# Restore the M3 reference file
mv docs/archive/ui_planning/rpg_city_map_navigation.html docs/ui_planning/ 2>/dev/null || true

# Move stale root-level markdown files
mv POSTGRESQL_TEST_MIGRATION_COMPLETE.md docs/archive/
mv POSTGRESQL_TEST_MIGRATION_SUMMARY.md docs/archive/
mv SCRIPT_RELOCATION_NOTICE.md docs/archive/
mv UPDATING.md docs/archive/
mv DEVELOPMENT_SETUP.md docs/archive/
mv README_CLAUDE_CODE.md docs/archive/

# Move the verbose concept doc; we'll create a condensed version
mv docs/learnonline_concept.md docs/archive/
```

- [ ] **Step 2: Create `docs/concept.md`**

Write the following as the complete content of `docs/concept.md`:

```markdown
# LearnOnline.cc — Product Concept

LearnOnline.cc is a gamified, student-facing vocational training platform built on Australian Quality Training Framework (AQTF) data. It is designed to be self-hosted by individual teachers who load only the units they teach.

## The Core Loop

A student picks a unit → plays through it as a card-based game → earns XP and badges for demonstrating competency against each Element and Performance Criteria → teacher sees class progress and knowledge gaps.

## Why AQTF?

The AQTF hierarchy (Training Package → Qualification → Unit → Element → Performance Criteria → Knowledge Evidence) is a natural game structure. Each Knowledge Evidence item is a scenario the student must respond to. Each Element is a competency domain. Passing all scenarios in a unit = demonstrated competency — exactly mirroring how RTOs assess students.

## Deployment

Teachers self-host: free Supabase account + Docker. No central hosting. No subscriptions.

## Milestones

| # | Name | Description |
|---|------|-------------|
| M1 | Clean Slate | Delete dead code, fix schema, working 15-min setup |
| M2 | Quiz MVP | Units → quizzes → XP/badges |
| M3 | Game Engine Alpha | Card-based competency game |
| M4 | Adaptive Loop + SCORM | Gap analysis + SCORM 1.2 export |

Full roadmap spec: `docs/superpowers/specs/2026-05-17-learnonline-roadmap-design.md`
```

- [ ] **Step 3: Create `docs/architecture.md`**

Write the following as the complete content of `docs/architecture.md`:

```markdown
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
```

- [ ] **Step 4: Create `docs/aqtf.md`**

Write the following as the complete content of `docs/aqtf.md`:

```markdown
# AQTF Integration

## What is AQTF?

The Australian Quality Training Framework defines the structure of nationally recognised vocational training. Data is published at [training.gov.au](https://training.gov.au) and accessible via a SOAP API.

## Data Hierarchy

```
Training Package (e.g. MSF — Furnishing)
  ├── Qualification (e.g. MSF30122 — Cert III in Cabinet Making)
  ├── Skillset
  └── Unit of Competency (e.g. MSFFI2001 — Install floor coverings)
        ├── Element (broad competency areas, e.g. "1. Prepare for installation")
        │     └── Performance Criteria (specific observable actions)
        ├── Knowledge Evidence (what the student must know — maps to M3 Scenario Cards)
        ├── Performance Evidence (what the student must do)
        └── Required Skills (underpinning skills and knowledge)
```

## TGA SOAP API

Credentials (public read-only, no account needed):
- Username: `WebService.Read`
- Password: `Asdf098`
- Endpoint: `https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV12.svc`

Client code: `backend/services/tga/client.py`

## Syncing Data

From the admin UI: **Admin → TGA Sync → select training packages → Import**.

From the command line:
```bash
python backend/scripts/tga_utils.py parse --unit MSFFI2001
python backend/scripts/tga_utils.py process-local   # process downloaded XML files
```

XML files can be downloaded from [training.gov.au](https://training.gov.au) manually and placed in `tgaWebServiceKit-2021-12-01/` (not in git).

## Database Tables

| Table | Description |
|-------|-------------|
| `training_packages` | Top-level packages (MSF, BSB, etc.) |
| `qualifications` | Certificates, Diplomas |
| `skillsets` | Industry skillsets |
| `units` | Units of competency |
| `unit_elements` | Elements within a unit |
| `unit_performance_criteria` | Performance criteria within an element |
| `unit_critical_aspects` | Knowledge Evidence items (M3 Scenario Cards) |
| `unit_required_skills` | Underpinning skills and knowledge |
```

- [ ] **Step 5: Commit**

```bash
git add docs/
git rm -r docs/technical docs/ui_planning/quiz.html 2>/dev/null || true
git rm POSTGRESQL_TEST_MIGRATION_COMPLETE.md POSTGRESQL_TEST_MIGRATION_SUMMARY.md \
  SCRIPT_RELOCATION_NOTICE.md UPDATING.md DEVELOPMENT_SETUP.md README_CLAUDE_CODE.md \
  docs/learnonline_concept.md 2>/dev/null || true
git commit -m "docs: archive stale docs, create lean concept/architecture/aqtf docs"
```

---

## Task 10: Rewrite `README.md`

**Files:** Modify `README.md`

- [ ] **Step 1: Write the new README**

Replace the entire contents of `README.md` with:

```markdown
# LearnOnline.cc

A gamified vocational training platform for Australian RTOs. Teachers self-host it, load the units they teach from Training.gov.au, and their students play through them as a card-based competency game.

Built with FastAPI, PostgreSQL, jQuery, and Bootstrap. No build step. MIT licensed.

---

## Quick Start (15 minutes)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Clone and configure

```bash
git clone https://github.com/your-username/learnonline.cc.git
cd learnonline.cc
cp env_example.txt .env
```

Edit `.env`:

**Option A — Local development (default, no external DB needed):**
The defaults in `env_example.txt` work as-is. Leave `DATABASE_URL` commented out.

**Option B — Supabase (recommended for sharing with students):**
1. Create a free project at [supabase.com](https://supabase.com)
2. Go to **Project Settings → Database → Connection string → URI**
3. Copy the URI and set it in `.env`:
   ```
   DATABASE_URL=postgresql://postgres:[your-password]@db.[project-ref].supabase.co:5432/postgres
   ```

### 2. Start the app

```bash
docker-compose up --build
```

Wait for all three services (`db`, `backend`, `frontend`) to show as healthy (~60 seconds first run).

- **App:** http://localhost:8080
- **API docs (Swagger):** http://localhost:8000/docs

### 3. Create an admin user

```bash
docker-compose exec db psql -U postgres -d learnonline -c "
INSERT INTO users (email, password_hash, first_name, last_name, is_active, role_id)
SELECT 'admin@example.com', crypt('changeme', gen_salt('bf')), 'Admin', 'User', true, id
FROM roles WHERE name = 'admin'
ON CONFLICT (email) DO NOTHING;
"
```

Log in at http://localhost:8080/login with `admin@example.com` / `changeme`.

### 4. Load training data

In the admin UI: **Admin → TGA Sync → select training packages → Import**

This fetches unit data from training.gov.au (public API, no credentials needed beyond the defaults in `.env`).

---

## Development

### Running tests

```bash
./run_tests.sh setup   # start test postgres container (first time)
./run_tests.sh unit    # all tests
./run_tests.sh auth    # auth tests only
./run_tests.sh coverage # HTML coverage report → test-results/
```

### Database migrations

```bash
cd backend
alembic upgrade head                               # apply all migrations
alembic revision --autogenerate -m "description"  # generate new migration
```

### Project structure

```
backend/          FastAPI app
  models/tables.py    Canonical ORM models
  database.py         DB connection (reads DATABASE_URL)
  routers/            One router per resource
  services/tga/       TGA SOAP client
  alembic/            Migrations
frontend/         Static HTML + jQuery + Bootstrap, served by nginx
docs/
  concept.md          Product vision
  architecture.md     Technical decisions
  aqtf.md             AQTF data model and TGA sync
  assessment_gameplay/ Game engine design (M3)
  superpowers/        Implementation plans and specs
```

---

## Roadmap

| Milestone | Status |
|-----------|--------|
| M1 — Clean Slate | In progress |
| M2 — Quiz MVP | Planned |
| M3 — Game Engine Alpha | Planned |
| M4 — Adaptive Loop + SCORM Export | Planned |

See `docs/superpowers/specs/2026-05-17-learnonline-roadmap-design.md` for the full spec.

---

## License

MIT
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README as 10-minute teacher setup guide"
```

---

## Task 11: End-to-End Smoke Test

Verify the cleaned-up repo works end-to-end from a fresh Docker build.

- [ ] **Step 1: Full rebuild**

```bash
docker-compose down -v          # remove volumes for a clean start
docker-compose up --build -d
```

Wait ~60 seconds for services to become healthy.

- [ ] **Step 2: Check all services are up**

```bash
docker-compose ps
```

Expected: `db`, `backend`, and `frontend` all showing as `healthy` or `running`.

- [ ] **Step 3: Check API health**

```bash
curl -s http://localhost:8000/ | python -m json.tool
```

Expected:
```json
{"status": "healthy"}
```

- [ ] **Step 4: Check Swagger loads**

Open http://localhost:8000/docs in a browser. Verify you can see the API documentation without errors.

- [ ] **Step 5: Register and login**

```bash
# Register
curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","first_name":"Test","last_name":"User"}' \
  | python -m json.tool

# Login
curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  | python -m json.tool
```

Expected: login returns a JSON object with an `access_token`.

- [ ] **Step 6: Check frontend loads**

Open http://localhost:8080 in a browser. Verify the home page loads without console errors.

- [ ] **Step 7: Run the test suite**

```bash
./run_tests.sh setup
./run_tests.sh unit
```

Expected: tests pass (or note any pre-existing failures for investigation).

- [ ] **Step 8: Final commit**

```bash
git add .
git status   # verify only expected files remain changed
git commit -m "chore: M1 Clean Slate complete — dead code removed, schema fixed, docs lean"
```

---

## Self-Review Checklist

- [x] **Dead files deleted:** `backend/db/`, `tables_old.py`, `favorites.py`, `user.py`, `quiz.py`, `legacy_test_scripts/`, `streamlit/`, `schema_old.sql`, stale docs
- [x] **Import chain fixed:** All routers → `from database import get_db`
- [x] **main.py clean:** No duplicate routes
- [x] **Alembic works:** `alembic upgrade head` on fresh DB creates all 21 tables with integer IDs
- [x] **DATABASE_URL:** Accepted by both `database.py` and docker-compose backend env
- [x] **env_example.txt:** Only real variables, Supabase path documented
- [x] **README:** Teacher-focused 15-minute setup guide
- [x] **Docs:** Lean structure with concept/architecture/aqtf; stale content archived not deleted
- [x] **Smoke test:** App starts, auth works, frontend loads
