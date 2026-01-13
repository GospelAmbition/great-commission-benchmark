# Great Commission Benchmark — Deployment Procedures

This document defines the deployment procedures, environments, and release workflows for the Great Commission Benchmark platform and CLI Runner.

**Last Updated:** December 17, 2025

---

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Environment Architecture](#environment-architecture)
3. [Platform Deployment](#platform-deployment)
4. [CLI Tool Distribution](#cli-tool-distribution)
5. [Database Migrations](#database-migrations)
6. [Release Workflow](#release-workflow)
7. [Rollback Procedures](#rollback-procedures)
8. [Environment Variables](#environment-variables)
9. [Monitoring & Verification](#monitoring--verification)
10. [Emergency Procedures](#emergency-procedures)
11. [Deployment Checklist](#deployment-checklist)

---

## Deployment Overview

### System Components

| Component | Hosting | Deployment Method |
|-----------|---------|-------------------|
| **Frontend** | Railway | Git push to `main` |
| **Backend API** | Railway | Git push to `main` |
| **Database** | Railway PostgreSQL | Managed service |
| **Storage** | Railway Simple Storage | S3-compatible bucket |
| **CLI Runner** | PyPI | Manual release |

### Deployment Philosophy

| Principle | Implementation |
|-----------|----------------|
| **Continuous Deployment** | Platform deploys automatically on merge to `main` |
| **Staged Releases** | All changes go through staging before production |
| **Zero-Downtime** | Rolling deployments with health checks |
| **Quick Rollback** | One-click rollback to previous deployment |
| **Immutable Builds** | Each deployment is a fresh container build |

---

## Environment Architecture

### Environments

| Environment | Purpose | URL | Branch |
|-------------|---------|-----|--------|
| **Local** | Development | localhost:3000 / :8000 | Any |
| **Staging** | Pre-production testing | staging.gcbenchmark.org | `staging` |
| **Production** | Live service | gcbenchmark.org | `main` |

### Railway Project Structure

```
GCB Platform (Railway Project)
├── Production Environment
│   ├── next-frontend (Next.js)
│   ├── fastapi-backend (FastAPI)
│   └── postgres (PostgreSQL)
│
└── Staging Environment
    ├── next-frontend-staging
    ├── fastapi-backend-staging
    └── postgres-staging
```

### Environment Promotion Flow

```
Local Development
      │
      ▼ (PR merged to staging)
   Staging
      │
      ▼ (Verified, PR merged to main)
  Production
```

---

## Platform Deployment

### Automatic Deployment (CI/CD)

Merging to `main` triggers automatic deployment:

```yaml
# Simplified workflow - Railway handles most of this
# .github/workflows/deploy.yml

name: Deploy

on:
  push:
    branches: [main, staging]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Railway deployment is automatic via GitHub integration
      # This workflow handles additional steps
      
      - name: Run pre-deployment checks
        run: |
          # Verify build succeeds
          cd gcb-platform/frontend && pnpm build
          cd ../backend && pip install -e . && pytest
      
      - name: Notify deployment start
        run: echo "Deployment started for ${{ github.ref }}"
```

### Railway Configuration

#### Frontend Service (`next-frontend`)

```toml
# railway.toml (frontend)
[build]
builder = "nixpacks"
buildCommand = "pnpm install && pnpm build"

[deploy]
startCommand = "pnpm start"
healthcheckPath = "/"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
```

#### Backend Service (`fastapi-backend`)

```toml
# railway.toml (backend)
[build]
builder = "nixpacks"
buildCommand = "pip install -e ."

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
```

### Manual Deployment

For emergency deployments or when CI/CD is unavailable:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy specific service
railway up --service next-frontend
railway up --service fastapi-backend

# Or deploy all services
railway up
```

### Deployment Verification

After each deployment:

1. **Health Check:** Verify `/health` endpoint returns 200
2. **Smoke Test:** Visit homepage, verify leaderboard loads
3. **API Check:** Verify `/api/leaderboard` returns data
4. **Logs:** Check Railway logs for errors

```bash
# View logs
railway logs --service next-frontend
railway logs --service fastapi-backend
```

---

## CLI Tool Distribution

### PyPI Release Process

The CLI Runner (`gcb-runner`) is distributed via PyPI.

#### Pre-Release Checklist

- [ ] All tests pass
- [ ] Version number updated in `pyproject.toml`
- [ ] CHANGELOG updated
- [ ] Documentation updated
- [ ] Embedded benchmark version updated (for runner)

#### Release Steps

```bash
# 1. Update version in pyproject.toml
# version = "1.3.0"

# 2. Clean previous builds
rm -rf dist/ build/ *.egg-info

# 3. Build distribution
python -m build

# 4. Test with TestPyPI first
python -m twine upload --repository testpypi dist/*

# 5. Verify installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ gcb-runner

# 6. Upload to PyPI
python -m twine upload dist/*

# 7. Verify installation from PyPI
pip install gcb-runner
gcb-runner --version
```

#### GitHub Release

```bash
# Create and push tag
git tag -a v1.3.0 -m "Release v1.3.0"
git push origin v1.3.0

# Create GitHub release (via CLI or web UI)
gh release create v1.3.0 \
  --title "GCB Runner v1.3.0" \
  --notes "## Changes\n- Feature 1\n- Bug fix 2"
```

### Version Numbering

| Component | Format | Example |
|-----------|--------|---------|
| **CLI Tools** | SemVer | `1.3.0` |
| **Platform** | Git SHA + deploy timestamp | `abc123-20251217` |
| **Benchmark Version** | Major.Minor | `2.1` |

---

## Database Migrations

### Migration Strategy

| Principle | Implementation |
|-----------|----------------|
| **Backward Compatible** | New migrations must work with old code |
| **Forward Only** | Prefer new migrations over editing existing |
| **Tested** | Run migrations in staging first |
| **Reviewed** | Migrations require PR review |

### Running Migrations

#### Staging

```bash
# Connect to staging environment
railway run --service fastapi-backend-staging -- alembic upgrade head
```

#### Production

```bash
# Connect to production environment
railway run --service fastapi-backend -- alembic upgrade head
```

### Creating New Migrations

```bash
# After making model changes
cd gcb-platform/backend
source venv/bin/activate

# Generate migration
alembic revision --autogenerate -m "Add user preferences table"

# Review the generated migration file
# Edit if necessary (especially for data migrations)

# Test locally
alembic upgrade head
alembic downgrade -1
alembic upgrade head

# Commit migration file
git add alembic/versions/
git commit -m "chore(db): add user preferences migration"
```

### Data Migrations

For migrations that modify data (not just schema):

```python
# Example: Data migration with safety checks
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 1. Add new column (nullable initially)
    op.add_column('users', sa.Column('display_name', sa.String(255), nullable=True))
    
    # 2. Migrate data
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE users SET display_name = name WHERE display_name IS NULL")
    )
    
    # 3. Make column non-nullable (optional)
    op.alter_column('users', 'display_name', nullable=False)

def downgrade():
    op.drop_column('users', 'display_name')
```

### Migration Rollback

```bash
# Rollback one migration
railway run --service fastapi-backend -- alembic downgrade -1

# Rollback to specific revision
railway run --service fastapi-backend -- alembic downgrade abc123

# Rollback all
railway run --service fastapi-backend -- alembic downgrade base
```

---

## Release Workflow

### Standard Release Flow

```
1. Feature Development
   └── Develop on feature branch
   └── Create PR to `staging`

2. Staging Deployment
   └── PR merged to `staging`
   └── Auto-deploy to staging environment
   └── QA testing on staging

3. Production Release
   └── Create PR from `staging` to `main`
   └── PR reviewed and approved
   └── Merge triggers production deployment

4. Post-Deployment
   └── Verify production health
   └── Monitor for errors
   └── Notify stakeholders
```

### Release Schedule

| Type | Frequency | Description |
|------|-----------|-------------|
| **Regular Releases** | As needed | Feature updates, bug fixes |
| **Hotfixes** | Immediate | Critical bug fixes |
| **Benchmark Updates** | Quarterly | New benchmark versions |

### Hotfix Procedure

For critical production issues:

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug-fix

# 2. Make fix, commit
git add .
git commit -m "fix: critical bug description"

# 3. Push and create PR directly to main
git push -u origin hotfix/critical-bug-fix
gh pr create --base main --title "Hotfix: Critical bug fix"

# 4. Get expedited review and merge
# 5. Cherry-pick to staging if needed
git checkout staging
git cherry-pick <commit-sha>
git push origin staging
```

---

## Rollback Procedures

### Platform Rollback

#### Railway Dashboard (Preferred)

1. Go to Railway Dashboard
2. Select the service (frontend or backend)
3. Navigate to "Deployments" tab
4. Find the last known good deployment
5. Click "Rollback to this deployment"

#### Railway CLI

```bash
# List recent deployments
railway deployments list --service next-frontend

# Rollback to specific deployment
railway rollback <deployment-id> --service next-frontend
```

### Database Rollback

**Warning:** Database rollbacks can cause data loss. Only roll back schema changes, not data migrations.

```bash
# Rollback one migration
railway run --service fastapi-backend -- alembic downgrade -1

# If data was modified, consider:
# 1. Restore from backup
# 2. Manual data fixes
# 3. Forward-fix with new migration
```

### CLI Rollback

Users can install specific versions:

```bash
# Rollback to previous CLI version
pip install gcb-runner==1.2.0
```

---

## Environment Variables

### Production Environment Variables

| Category | Variables | Management |
|----------|-----------|------------|
| **Database** | `DATABASE_URL` | Railway auto-injected |
| **Auth** | `NEXTAUTH_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Railway variables |
| **Payments** | `STRIPE_*` | Railway variables |
| **LLM** | `OPENROUTER_API_KEY`, `OPENROUTER_REFERER` | Railway variables |
| **Email** | `RESEND_API_KEY`, `EMAIL_FROM` | Railway variables |
| **Newsletter** | `MAILERLITE_API_KEY`, `MAILERLITE_GROUP_ID` | Railway variables |
| **Storage** | `S3_*`, `BACKEND_PUBLIC_URL` | Railway variables |
| **Analytics** | `NEXT_PUBLIC_UMAMI_*` | Railway variables (frontend only) |

### Setting Environment Variables

#### Railway Dashboard

1. Select service
2. Go to "Variables" tab
3. Add/edit variables
4. Redeploy to apply

#### Railway CLI

```bash
# Set variable
railway variables set STRIPE_SECRET_KEY=sk_live_xxx

# List variables
railway variables list

# Remove variable
railway variables remove OLD_VARIABLE
```

### Secret Rotation

| Secret | Rotation Frequency | Procedure |
|--------|-------------------|-----------|
| **API Keys** | Quarterly | Generate new key, update Railway, verify, revoke old |
| **Database** | As needed | Railway manages credentials |
| **NextAuth Secret** | Annually | Generate new secret, update Railway (frontend + backend), users will need to re-authenticate |
| **Google OAuth** | As needed | Rotate in Google Cloud Console, update Railway |

---

## Monitoring & Verification

### Health Checks

| Endpoint | Expected | Frequency |
|----------|----------|-----------|
| `/` | 200 OK | Continuous |
| `/health` | `{"status": "healthy"}` | Every 30s |
| `/api/leaderboard` | JSON data | Every 5min |

### Post-Deployment Verification

```bash
# 1. Check service health
curl https://gcbenchmark.org/health

# 2. Check API response
curl https://gcbenchmark.org/api/leaderboard | jq '.results | length'

# 3. Check logs for errors
railway logs --service next-frontend --since 10m
railway logs --service fastapi-backend --since 10m
```

### Monitoring Tools

| Tool | Purpose | Access |
|------|---------|--------|
| **Railway Metrics** | Resource usage, latency | Railway Dashboard |
| **Sentry** | Error tracking | sentry.io |
| **Umami** | User analytics | Self-hosted |

### Alerts

Configure alerts for:

| Condition | Alert Method | Response |
|-----------|--------------|----------|
| **Service Down** | Email + Discord | Immediate investigation |
| **Error Spike** | Sentry notification | Check logs, potential rollback |
| **High Latency** | Railway alert | Performance investigation |
| **Database Issues** | Railway alert | Check connections, queries |

---

## Emergency Procedures

### Service Outage

```
1. ASSESS
   └── Check Railway status page
   └── Review recent deployments
   └── Check error logs

2. COMMUNICATE
   └── Post status update
   └── Notify stakeholders

3. MITIGATE
   └── Rollback if recent deployment
   └── Scale resources if capacity issue
   └── Contact Railway support if infrastructure

4. RESOLVE
   └── Fix root cause
   └── Deploy fix (hotfix procedure)
   └── Verify restoration

5. POST-MORTEM
   └── Document incident
   └── Identify improvements
   └── Update procedures
```

### Data Breach Response

1. **Contain:** Immediately disable affected services
2. **Assess:** Determine scope of breach
3. **Notify:** Alert security contact and stakeholders
4. **Remediate:** Fix vulnerability, rotate credentials
5. **Communicate:** Notify affected users within 72 hours
6. **Document:** Full incident report and learnings

### Database Recovery

```bash
# 1. List available backups
railway backups list --service postgres

# 2. Restore from backup
railway backups restore <backup-id> --service postgres

# 3. Verify data integrity
railway run --service fastapi-backend -- python -c "from app.db import verify_integrity; verify_integrity()"
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests pass in CI
- [ ] Code reviewed and approved
- [ ] No blocking security vulnerabilities
- [ ] Environment variables configured
- [ ] Database migrations tested in staging
- [ ] Documentation updated

### Deployment

- [ ] Merge to staging branch
- [ ] Verify staging deployment
- [ ] Run smoke tests on staging
- [ ] Merge to main branch
- [ ] Monitor deployment progress
- [ ] Verify production health check

### Post-Deployment

- [ ] Verify homepage loads correctly
- [ ] Verify API endpoints respond
- [ ] Check error tracking (Sentry)
- [ ] Monitor resource usage
- [ ] Notify stakeholders of release

### CLI Release

- [ ] Version number updated
- [ ] Tests pass
- [ ] CHANGELOG updated
- [ ] Build succeeds locally
- [ ] TestPyPI upload successful
- [ ] Production PyPI upload successful
- [ ] Installation verified
- [ ] GitHub release created
- [ ] Announcement posted

---

## Reference

### Useful Commands

```bash
# Railway CLI
railway login                    # Authenticate
railway link                     # Link to project
railway up                       # Deploy
railway logs                     # View logs
railway run -- <command>         # Run command in service
railway variables list           # List env vars
railway deployments list         # List deployments
railway rollback <id>            # Rollback

# Database
alembic upgrade head             # Run migrations
alembic downgrade -1             # Rollback one
alembic history                  # View history
alembic current                  # Current revision

# PyPI
python -m build                  # Build package
twine upload dist/*              # Upload to PyPI
pip install gcb-runner==x.y.z    # Install specific version
```

### Emergency Contacts

| Role | Contact | When to Use |
|------|---------|-------------|
| **Project Lead** | [Contact info] | Service outages, critical issues |
| **Railway Support** | support@railway.app | Infrastructure issues |
| **Stripe Support** | Dashboard | Payment issues |
| **Google Cloud Support** | Dashboard | OAuth/authentication issues |

---

## Related Documents

- [Local Development Setup](./Local-Development-Setup.md) — Development environment
- [Testing Strategies](./Testing-Strategies.md) — Testing requirements
- [Security Practices](./Security-Practices.md) — Security procedures
- [Technical Decisions](./Technical-Decisions.md) — Architecture decisions

---

*This document should be updated as deployment procedures evolve. Last review: December 2025.*
