# Claude Code Setup for LearnOnline.cc

This document describes the Claude Code automations configured for this project and the recommended workflow for using them effectively.

---

## What's Installed

### MCP Servers (`.mcp.json`)

| Server | Purpose |
|--------|---------|
| **postgres** | Live queries against the dev database — Claude can inspect actual table data, validate migrations, and write accurate SQL |
| **context7** | Pulls live, version-accurate docs for FastAPI, SQLAlchemy 2.0, Alembic, and zeep — prevents hallucinated deprecated API patterns |

> **Prerequisite**: Node.js must be installed (`node --version`). Both servers are fetched via `npx` on first use.
>
> The postgres server connects to the dev DB at `localhost:5332` — Docker must be running (`docker-compose up -d db`).

### Hooks (`.claude/settings.json`)

| Hook | Trigger | What it does |
|------|---------|--------------|
| **Python formatter** | After any `.py` file edit | Runs `black` + `isort` automatically if they're on PATH |
| **`.env` guard** | Before any file write/edit | Blocks edits to `.env` — redirects to `env_example.txt` |

> The Python formatter requires `black` and `isort` to be installed in your active environment.  
> If working without Docker: `pip install black isort` in your `backend/venv`.  
> If working with Docker: the formatter only runs on host — run `docker-compose exec backend black <file>` for in-container formatting.

### Skills (`.claude/skills/`)

Invoked with `/skill-name` in the Claude Code prompt, or Claude invokes them automatically when the context matches.

| Skill | Command | When to use |
|-------|---------|-------------|
| **tga-sync** | `/tga-sync` | Refreshing training data from Training.gov.au or processing local XML files |
| **new-migration** | `/new-migration` | Adding or modifying database tables/columns |

### Subagent (`.claude/agents/`)

| Agent | When to use |
|-------|------------|
| **schema-drift-detector** | Before any database-touching PR, or after merging changes that touched `schema.sql`, `tables.py`, or migrations |

---

## Recommended Workflow

### Starting a Session

1. Start Docker: `docker-compose up -d`
2. Open Claude Code in the project root — the MCP servers and hooks activate automatically
3. Check that postgres MCP is connected: ask Claude *"how many training packages are in the database?"* — if it can answer without you providing data, the MCP is live

### Sprint Workflow

This project uses focused, single-layer sprints (see `docs/prompts.md`). The recommended pattern:

**1. Frame the sprint with `/feature-dev`**
```
/feature-dev add gamification XP award when a user completes a quiz
```
This runs the explore → architect → implement sequence and keeps scope tight. Avoid asking Claude to touch DB + API + frontend in one shot — pick one layer per sprint.

**2. Use context7 for library-specific work**
Append `use context7` to any prompt involving FastAPI, SQLAlchemy, or Alembic:
```
add a composite index on (user_id, unit_id) to user_progress, use context7
```
This ensures Claude pulls the SQLAlchemy 2.0 docs rather than relying on training data that may include 1.x patterns.

**3. Database changes always go through `/new-migration`**
```
/new-migration add points_multiplier column to user_profile
```
Never hand-edit `schema.sql` alone — always generate a migration so the Alembic history stays accurate.

**4. After any schema work — run the drift detector**
```
Ask Claude: "run the schema-drift-detector agent on this project"
```
Or just ask: *"check for schema drift"* — Claude will invoke the agent automatically.

**5. Commit with `/commit`**
```
/commit
```
Generates a structured commit message from the diff. Much better than `git commit -m "updated"`.

### TGA Data Sync Workflow

When you need to refresh training data:
```
/tga-sync
```
Claude will walk you through: checking Docker health → choosing what to sync → executing the API call → monitoring the background task → verifying results in the DB.

For quick local XML processing (no TGA API call needed):
```
/tga-sync process local files
```

### Code Review Before PR

```
/review
```
Or for a thorough multi-agent review:
```
/review-pr
```

The `security-review` skill is worth running specifically before any changes touching `backend/auth/` or the TGA credential handling in `services/tga/client.py`:
```
/security-review
```

---

## Querying the Database Directly

With the postgres MCP active, you can ask Claude natural-language questions about live data:

- *"How many units are linked to training package BSB?"*
- *"Show me the last 5 user_progress records for any user"*
- *"What columns does the user_profile table actually have?"* (useful when you suspect schema drift)

Claude will write and run the SQL, returning real results. This replaces the need to shell into the Docker container for most investigative queries.

---

## When Things Go Wrong

### MCP server not connecting
```bash
# Verify Node is available
node --version
npx --version

# Test the postgres MCP manually
npx -y @modelcontextprotocol/server-postgres postgresql://postgres:postgres@localhost:5332/learnonline
```
If Docker isn't running, the postgres MCP will fail silently — Claude falls back to reading schema files instead.

### Python formatter not running
The hook requires `black` and `isort` to be on your `PATH`. Check:
```bash
which black && which isort
```
If missing: `pip install black isort` (or activate your `backend/venv` first).

### `.env` guard blocking something intentional
The hook blocks any edit to files matching `/.env$`. If you genuinely need to update `.env` (e.g., adding a new variable), do it manually in your text editor outside Claude Code, then update `env_example.txt` with the placeholder version.

### Alembic migration failed on apply
The most common cause is a NOT NULL column added to an existing table without a `server_default`. Use `/new-migration` — step 4 in that skill explicitly checks for this.

---

## Project-Specific Conventions Claude Follows

From `CLAUDE.md` and project history:

- **Single-layer sprints**: DB changes, API changes, and frontend changes should be separate tasks — don't ask Claude to do all three in one prompt
- **No mock databases in tests**: tests always hit a real PostgreSQL instance (the test container at port 5433)
- **ORM-first**: schema changes go through `tables.py` + Alembic, not raw SQL edits to `schema.sql`
- **jQuery + vanilla JS only**: the frontend has no build step — no importing npm packages into frontend code
- **CORS is open in dev** (`allow_origins: ["*"]` in `main.py`) — this is intentional for local development, not a bug to fix

---

## File Locations

```
learnonline.cc/
├── .mcp.json                          # MCP server definitions (postgres, context7)
├── .claude/
│   ├── settings.json                  # Project hooks (.env guard, Python formatter)
│   ├── skills/
│   │   ├── tga-sync/SKILL.md          # /tga-sync skill
│   │   └── new-migration/SKILL.md     # /new-migration skill
│   └── agents/
│       └── schema-drift-detector.md   # Schema drift detection subagent
├── CLAUDE.md                          # Architecture guide for Claude
└── README_CLAUDE_CODE.md              # This file
```
