---
name: tga-sync
description: Sync training packages, units, qualifications, or skillsets from Training.gov.au via the admin API. Use when the user wants to refresh TGA data, process local XML files, or sync specific training package codes.
---

Guide the user through syncing TGA data step by step.

## Step 1 — Check Docker health
Run `docker-compose ps` from the project root. Confirm `backend` and `db` show as healthy. If not, run `docker-compose up -d` and wait.

## Step 2 — Confirm what to sync
Ask the user:
- (a) All training packages (slow, use sparingly)
- (b) Specific codes — e.g. `BSB, ICT` (comma-separated)
- (c) Process local XML files only (fastest, no TGA API call)

## Step 3 — Execute

**For (a) or (b)**: Remind user they need an admin JWT. Ask if they have one; if not, tell them to log in at http://localhost:8080 and retrieve the token from localStorage (`localStorage.getItem('access_token')`).

Then call the admin sync endpoint:
```
POST http://localhost:8000/api/admin/sync-training-packages
Authorization: Bearer <token>
Content-Type: application/json

{ "codes": ["BSB", "ICT"] }   # omit codes field to sync all
```

**For (c)**: Run:
```bash
cd backend && python scripts/tga_utils.py process-local
```

## Step 4 — Monitor task status
Poll `GET http://localhost:8000/api/admin/tasks` every 5 seconds until the task status is `completed` or `failed`. Report the result summary to the user.

## Step 5 — Verify
Query the DB to confirm records were created:
```sql
SELECT code, title, updated_at FROM training_packages ORDER BY updated_at DESC LIMIT 10;
```
(Use the postgres MCP server if available, otherwise ask user to check the admin UI at http://localhost:8080/admin)
