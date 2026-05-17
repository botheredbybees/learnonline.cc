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
