# Production Database Migration Guide

**Purpose:** Step-by-step guide for migrating production database from an older schema to the latest version after a major refactoring.

**Last Updated:** January 2025

---

## Overview

After a major refactoring in the local development environment (which reset the database), your production environment is running an older database schema. This guide will help you safely migrate production to match your local development environment.

### Migration Chain

Your project has **14 migrations** (001 through 014):

```
<base> -> 001: Initial schema
001 -> 002: Add tester agreement acceptance
002 -> 003: Add user API keys table
003 -> 004: Add fee waiver fields to users table
004 -> 005: Add fee waiver and payment fields to community_submissions table
005 -> 006: Add metadata column to questions table
006 -> 007: Add CASCADE delete to question_set foreign keys
007 -> 008: Add new fields to sponsorship_requests table
008 -> 009: Add is_locked and notes columns to questions table
009 -> 010: Make judge_prompt nullable
010 -> 011: Clean up unused fields from question_metadata JSONB
011 -> 012: Add target_question_count to question_sets table
012 -> 013: Add blog tables for Action CMS
013 -> 014: Add is_publicly_visible to question_sets (HEAD)
```

---

## Prerequisites

1. **Railway CLI installed and authenticated:**
   ```bash
   npm install -g @railway/cli
   railway login
   railway link  # Link to your project
   ```

2. **Access to production environment** (Railway project)

3. **Backup of production database** (recommended before migration)

---

## Step 1: Check Current Migration State

First, determine what migration version production is currently on:

```bash
# Check current migration version in production
railway run --service fastapi-backend -- alembic current
```

**Expected output examples:**
- If on an older version: `001` or `005` or `010` (shows the revision ID)
- If already up to date: `014 (head)`
- If no migrations run: `(empty)` or error

**Note:** If you see an error or empty output, the database may not have the `alembic_version` table yet, meaning it's on the base schema (before migration 001).

---

## Step 2: Review Migration History

View the full migration chain to understand what will be applied:

```bash
# View migration history
railway run --service fastapi-backend -- alembic history
```

This shows all migrations from base to head, helping you understand what changes will be applied.

---

## Step 3: Create Database Backup (Recommended)

**⚠️ IMPORTANT:** Before running migrations, create a backup of your production database.

### Option A: Railway Dashboard Backup

1. Go to Railway Dashboard
2. Select your PostgreSQL service
3. Navigate to "Backups" tab
4. Click "Create Backup" or use existing backup

### Option B: Railway CLI Backup

```bash
# List available backups
railway backups list --service postgres

# Create a new backup (if Railway supports this via CLI)
# Note: Check Railway documentation for backup creation commands
```

### Option C: Manual SQL Dump (if needed)

```bash
# Connect to production database and create dump
railway run --service postgres -- pg_dump -Fc database_name > backup_$(date +%Y%m%d_%H%M%S).dump
```

---

## Step 4: Test Migration in Staging (If Available)

If you have a staging environment, test the migration there first:

```bash
# Check staging migration state
railway run --service fastapi-backend-staging -- alembic current

# Run migrations in staging
railway run --service fastapi-backend-staging -- alembic upgrade head

# Verify staging works correctly
# Test API endpoints, check logs, etc.
```

---

## Step 5: Run Production Migration

Once you've verified the current state and (optionally) tested in staging:

```bash
# Run all pending migrations to bring production to HEAD
railway run --service fastapi-backend -- alembic upgrade head
```

**What this does:**
- Alembic will automatically detect which migrations are missing
- It will apply them in order (001 → 002 → 003 → ... → 014)
- Each migration runs in a transaction (if supported by your database)

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, Add tester agreement acceptance
INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, Add user API keys table
...
INFO  [alembic.runtime.migration] Running upgrade 013 -> 014, Add is_publicly_visible to question_sets
```

---

## Step 6: Verify Migration Success

### 6.1 Check Migration Status

```bash
# Verify production is now at HEAD
railway run --service fastapi-backend -- alembic current
```

**Expected output:** `014 (head)`

### 6.2 Verify Database Schema

```bash
# Check that tables exist (example)
railway run --service fastapi-backend -- python -c "
from app.db.base import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print('Tables:', tables)
"
```

### 6.3 Test Application

1. **Health Check:**
   ```bash
   curl https://gcbenchmark.org/health
   ```

2. **API Endpoints:**
   ```bash
   curl https://gcbenchmark.org/api/public/leaderboard
   ```

3. **Check Logs:**
   ```bash
   railway logs --service fastapi-backend --since 5m
   ```

4. **Verify Critical Features:**
   - User authentication works
   - Database queries succeed
   - No migration-related errors in logs

---

## Step 7: Deploy Updated Application Code

**Important:** After migrating the database, ensure your production application code matches the new schema.

1. **Verify code is deployed:**
   ```bash
   # Check if latest code is deployed
   railway deployments list --service fastapi-backend
   ```

2. **If code needs deployment:**
   - Push to `main` branch (triggers auto-deployment)
   - Or manually deploy:
     ```bash
     railway up --service fastapi-backend
     ```

3. **Verify application starts correctly:**
   ```bash
   railway logs --service fastapi-backend --since 2m
   ```

---

## Troubleshooting

### Issue: Migration Fails Mid-Way

If a migration fails partway through:

1. **Check the error:**
   ```bash
   railway logs --service fastapi-backend --since 10m
   ```

2. **Check current state:**
   ```bash
   railway run --service fastapi-backend -- alembic current
   ```

3. **Common issues:**
   - **Data conflicts:** Some migrations modify existing data. Check migration files for data transformations.
   - **Missing dependencies:** Ensure all required columns/tables exist.
   - **Constraint violations:** Check for foreign key or unique constraint issues.

4. **Fix and retry:**
   - Fix the underlying issue (data, schema, etc.)
   - Re-run: `railway run --service fastapi-backend -- alembic upgrade head`
   - Alembic will skip already-applied migrations

### Issue: Need to Rollback

If you need to rollback a migration:

```bash
# Rollback one migration
railway run --service fastapi-backend -- alembic downgrade -1

# Rollback to specific revision
railway run --service fastapi-backend -- alembic downgrade 010

# Rollback all migrations (⚠️ DANGEROUS)
railway run --service fastapi-backend -- alembic downgrade base
```

**⚠️ Warning:** Rolling back data migrations can cause data loss. Only rollback schema changes, not data migrations.

### Issue: Migration Already Applied But Code Doesn't Match

If migrations are applied but application code is outdated:

1. Deploy the latest code to production
2. Verify application works with migrated schema
3. If issues persist, check for code that references old schema

### Issue: "Can't locate revision identified by 'XXX'"

This means Alembic can't find a migration file. Ensure:

1. All migration files are committed to git
2. Latest code is deployed to Railway
3. Migration files exist in `alembic/versions/` directory

---

## Migration Safety Checklist

Before running production migration:

- [ ] **Backup created** - Database backup exists and is accessible
- [ ] **Current state known** - Checked `alembic current` in production
- [ ] **Migration history reviewed** - Understand what changes will be applied
- [ ] **Staging tested** - (If available) Migrations tested in staging
- [ ] **Code deployed** - Latest application code is ready for new schema
- [ ] **Maintenance window** - (If needed) Schedule during low-traffic period
- [ ] **Rollback plan** - Know how to rollback if needed
- [ ] **Monitoring ready** - Can watch logs and metrics during migration

---

## Post-Migration Verification

After successful migration:

- [ ] Migration status shows `014 (head)`
- [ ] Health check endpoint returns 200
- [ ] API endpoints respond correctly
- [ ] No errors in application logs
- [ ] Critical user flows work (login, submissions, etc.)
- [ ] Database queries succeed
- [ ] Application performance is normal

---

## Quick Reference Commands

```bash
# Check current migration version
railway run --service fastapi-backend -- alembic current

# View migration history
railway run --service fastapi-backend -- alembic history

# Run migrations to HEAD
railway run --service fastapi-backend -- alembic upgrade head

# Rollback one migration
railway run --service fastapi-backend -- alembic downgrade -1

# View logs
railway logs --service fastapi-backend --since 10m

# Check health
curl https://gcbenchmark.org/health
```

---

## Additional Resources

- [Deployment Procedures](./Deployment-Procedures.md) - Full deployment documentation
- [Backend README](../gcb-platform/backend/README.md) - Backend setup and migration info
- [Alembic Documentation](https://alembic.sqlalchemy.org/) - Official Alembic docs

---

## Support

If you encounter issues during migration:

1. Check Railway logs for detailed error messages
2. Review migration files in `gcb-platform/backend/alembic/versions/`
3. Verify database connection and permissions
4. Consult [Deployment Procedures](./Deployment-Procedures.md) for rollback procedures

---

*This guide should be updated as migration procedures evolve.*
