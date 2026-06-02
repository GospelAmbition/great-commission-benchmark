---
name: refresh-local-gcb-db
description: Overwrite local gcb-platform Postgres database with a fresh copy from Railway
---

# Refresh Local Great Commission Benchmark Database

Use this skill when the user asks to "refresh the local great commission benchmark database" (or similar wording).

## What this does

- Uses `RAILWAY_DATABASE_URL` from `gcb-platform/backend/.env` as source.
- Overwrites the local `gcb-platform` Postgres database (`gcb`) running in Docker.
- Creates a local SQL backup in `/tmp` before restore.

## Required checks

1. Ensure `gcb-platform/backend/.env` exists.
2. Ensure `RAILWAY_DATABASE_URL` is present and non-empty.
3. Ensure Docker is running and `gcb-platform/docker-compose.yml` postgres service is up.
4. Ask for confirmation before destructive overwrite.

## Execute

Run:

```bash
./gcb-platform/scripts/refresh_local_db_from_railway.sh
```

## After refresh

1. Re-run migrations to align schema:
   ```bash
   cd gcb-platform/backend
   venv/bin/alembic upgrade head
   ```
2. Verify backend health:
   ```bash
   cd gcb-platform/backend
   venv/bin/uvicorn main:app --port 8001
   ```
   Then check `http://localhost:8001/health`.
