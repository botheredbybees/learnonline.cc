# LearnOnline.cc — Milestone March Roadmap Design

**Date:** 2026-05-17  
**Author:** Peter Shanks  
**Status:** Approved

---

## Context

LearnOnline.cc is a solo passion project — a gamified, student-facing vocational training platform built on Australian Quality Training Framework (AQTF) data. The author previously built a web-based assessment tool generator using AQTF data and wants a student-facing version.

The codebase has accumulated significant drift from exploratory AI sessions, abandoned approaches (Vue → jQuery, UUID → int IDs), and incomplete features. This document defines a four-milestone plan to recover clarity and ship something real.

---

## Architectural Direction

### Deployment Model

**Self-hosted per teacher.** The author does not want to host or profit from this project. The intended deployment is:

1. Teacher creates a free [Supabase](https://supabase.com) project (~500MB free tier, sufficient for a course's worth of units)
2. Teacher runs `docker-compose up` with their `DATABASE_URL` pointing at their Supabase Postgres instance
3. Admin UI lets them pull in specific training packages/units from TGA (Training.gov.au)
4. Students visit the teacher's self-hosted URL

**Technically:** Supabase is standard Postgres. FastAPI + SQLAlchemy requires zero changes — only `DATABASE_URL` in `.env` changes. No Supabase SDK, no Supabase Auth, no edge functions. One line of config.

### Visual Aesthetic

**CSS-based RPG style — no AI image dependency.**

The Studio Ghibli RPG aesthetic is the long-term visual goal, but AI image generation on a local 16GB GPU has not produced acceptable results and has been a project blocker. The interim approach:

- Tile-style card layouts using pure CSS
- Pixel-art or retro-RPG typography (free fonts: Press Start 2P, VT323)
- Warm earthy color palettes evoking the Ghibli mood without requiring illustration
- Simple SVG icons for unit/element/badge markers
- Real art assets can be dropped in later — the layout is designed to accept them

### Schema Management

Alembic is the single source of truth for the database schema. `schema.sql`, `schema_old.sql`, and the `schema_updates/` files are reference artifacts only. A fresh install runs `alembic upgrade head` — nothing else.

---

## M1 — Clean Slate

**Goal:** A teacher can clone the repo, fill in a `.env`, run `docker-compose up`, and have a working app in under 15 minutes.

**Duration:** ~1–2 weeks

### Delete

| Path | Reason |
|------|--------|
| `backend/models/tables_old.py` | UUID-era model, superseded by `tables.py` |
| `backend/models/favorites.py` | UUID-based Pydantic schemas, never wired up |
| `backend/models/user.py` | UUID-based Pydantic user schemas, superseded |
| `backend/db/` | Duplicate `database.py` module, unused |
| `streamlit/` | Empty shell (only Dockerfile + requirements.txt, no code) |
| `legacy_test_scripts/` | Dead exploratory scripts, replaced by pytest suite |
| `schema_old.sql` | Old backup, no longer needed |
| `debug_auth.py` (root) | One-off debug script |
| `backend/run_auth_tests.py` | Superseded by `run_tests.sh` |
| `backend/check_units.py` | One-off exploration script |
| `docs/ui_planning/quiz.html` | Exploratory prototype, superseded |

### Fix

- **`backend/main.py`**: Remove duplicate `/training-packages/` and `/units/` route definitions that exist outside the router system. These shadow the proper router endpoints.
- **`backend/database.py` vs `backend/db/database.py`**: Keep `backend/database.py` (used by `main.py`), delete `backend/db/`.
- **Schema**: Ensure Alembic migrations cover all tables currently in `schema.sql`. Add any missing migrations. `alembic upgrade head` must produce a working schema from scratch.
- **`DATABASE_URL` as primary config**: Ensure `backend/database.py` accepts `DATABASE_URL` as the primary env var (already partially done), removing the need for five separate DB_ vars when using Supabase.

### Prune Documentation

Collapse the 40+ markdown docs to:
- `README.md` — setup guide (10-minute path from clone to running app)
- `docs/concept.md` — vision and product overview (consolidate `learnonline_concept.md`)
- `docs/architecture.md` — technical decisions
- `docs/aqtf.md` — AQTF data model and TGA sync
- Keep `docs/assessment_gameplay/` — still relevant for M3

Everything else is archived in `docs/archive/` or deleted.

### Deliverable

`git clone` → `.env` with `DATABASE_URL` → `docker-compose up` → working app:
- Auth (register, login, JWT)
- Unit/qualification browsing from TGA-synced data
- XP tracking on page interactions
- Admin UI for TGA sync (select specific training packages to import)
- A clear README that a teacher unfamiliar with Docker can follow

---

## M2 — Quiz MVP

**Goal:** A student can log in, pick a unit, work through its elements as quizzes, earn XP, and see a completion badge.

**Duration:** ~2–3 weeks

### Data Model

AQTF unit structure maps directly to the quiz layer:

```
Unit
  └── Element (broad competency area)
        └── PerformanceCriteria (specific observable action)
              └── QuizQuestion (assesses one PC)
```

Knowledge Evidence items (from `unit_critical_aspects`) become the question source.

### Question Types (v1)

Three types only — enough to cover AQTF evidence requirements without over-engineering:

1. **Multiple choice** — one correct answer from 4 options
2. **Short answer** — free text, teacher-marked or keyword-matched
3. **Ordering** — arrange steps in correct sequence (maps well to procedural performance criteria)

### Scoring Model

- Pass/fail **per element** — mirrors the AQTF competency model (you are either competent or not)
- A student passes an element when all its performance criteria questions are answered correctly
- A student completes a unit when all elements are passed
- Partial progress is saved; students can return mid-unit
- Failed elements can be retried immediately

### Gamification

- XP awarded per element passed (configurable per unit, default 50 XP)
- Badge awarded on full unit completion
- Student dashboard: progress per unit with "X of Y elements complete" view

### Teacher Controls

- Admin UI: enable/disable individual questions per unit
- Admin UI: add custom questions for a unit (beyond auto-generated ones)
- Admin UI: view class progress — which students are on which elements

### Deliverable

Student flow: login → browse units → start unit → answer element questions → pass/fail → earn XP/badge → see progress on dashboard.

---

## M3 — Game Engine Alpha

**Goal:** A teacher assigns a unit; students play through it as a card game and achieve (or don't achieve) competency.

**Duration:** ~3–4 weeks

### Card Types

As defined in `docs/assessment_gameplay/`:

| Card Type | Source | Purpose |
|-----------|--------|---------|
| **Element Card** | `unit_elements` | Broad competency area — player's "hand" |
| **Performance Card** | `unit_performance_criteria` | Specific action — played to address scenarios |
| **Scenario Card** | `unit_critical_aspects` (Knowledge Evidence) | The challenge the student must respond to |

### Gameplay Flow

1. Student selects a unit → receives their hand of Element + Performance Cards
2. System deals a Scenario Card (Knowledge Evidence challenge)
3. Student selects which Performance Cards address the scenario
4. System validates: are the required PCs present in the played selection?
5. Pass → next scenario; Fail → retry (see adaptive routing in M4)
6. Unit complete when all Scenario Cards are cleared

### Pass Criteria

- Each Scenario Card is pass/fail — 100% required (no partial credit)
- This directly mirrors AQTF's competency model
- Failed attempts are recorded for M4's gap analysis

### UI

CSS-only RPG aesthetic:
- Card layout: tile-style with element/PC text, colored by competency area
- "Training map" showing unit progression as a simple node graph (CSS grid, no library)
- Warm RPG palette (forest greens, parchment tones, amber accents)
- Designed to accept real art assets in future — image slots exist but default to CSS fills

### Game State Persistence

- Game state stored in DB (`game_sessions` table): current scenario, played cards, attempt history
- Students can close the browser and resume mid-unit
- Teachers can view a student's card play history for a unit

### Deliverable

Full playable unit as a card game. A student can be assigned a unit, play through all scenarios, and achieve competency — or have their gaps recorded for M4.

---

## M4 — Adaptive Loop + SCORM Export

**Goal:** Weak areas are identified from game play and addressed automatically; units can be exported for use in other LMS systems.

**Duration:** ~3 weeks

### Adaptive Routing

When a student fails a Scenario Card, the system has precise information:

```
Failed Scenario → maps to → Knowledge Evidence item
                          → maps to → Performance Criteria
                          → maps to → Element
```

Three adaptive responses, tried in order:

1. **Knowledge Card** — a simplified single-PC micro-quiz targeting exactly the failed criteria. Lower stakes, no time pressure, more scaffolding.
2. **Prerequisite suggestion** — query the AQTF data for units that contain the same Element/PC. Surface them as "this might help first."
3. **Alternative question type** — if the student failed a scenario card using selection (Performance Cards), offer the same content as a short-answer question (and vice versa).

### Gap Map (Teacher Dashboard)

- Per-class view: heatmap of Elements vs Students — which competency areas are broadly weak
- Per-student view: timeline of attempts, showing which PCs have been retried most
- Exportable as CSV for RTO reporting

### SCORM Export

- Generate SCORM 1.2 packages (.zip) from any unit
- Package contains: quiz questions + scenario card game + xAPI communication layer
- Teacher downloads .zip, uploads to Moodle/Canvas/any SCORM-compliant LMS
- If the student is also registered on the LearnOnline instance, completion data syncs back and updates their XP/progress
- SCORM 1.2 chosen for maximum LMS compatibility (SCORM 2004 and xAPI are stretch goals)

### Deliverable

- Students who fail are automatically given a targeted recovery path
- Teachers see exactly where the class is struggling
- Any unit can be exported as a SCORM package and used in an existing RTO LMS

---

## Milestone Summary

| Milestone | Focus | Key Output |
|-----------|-------|------------|
| M1 — Clean Slate | Delete, fix, document | Deployable in 15 min, clean foundation |
| M2 — Quiz MVP | AQTF → quiz questions | Students complete units, earn XP/badges |
| M3 — Game Engine Alpha | Card-based competency game | Full playable unit as card game |
| M4 — Adaptive Loop + SCORM | Gap analysis + LMS integration | Adaptive paths + SCORM export |

Each milestone ships something real. M1 is the prerequisite for everything; M2–M4 each build on the previous without depending on unbuilt future work.

---

## Known Constraints

- **Solo project** — no collaborators, no timeline pressure, no external hosting obligations
- **AI image generation** — local GPU (16GB NVIDIA 5060) has not produced acceptable Studio Ghibli-style images. Visual design avoids this dependency until a better pipeline exists.
- **Supabase free tier** — 500MB storage, 2 active projects. Sufficient for per-teacher use; not suitable for hosting a full AQTF mirror.
- **AQTF data is public** — TGA SOAP API credentials are read-only public access. No licensing concern for syncing and displaying unit data.
