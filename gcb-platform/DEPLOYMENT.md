# Great Commission Benchmark - Deployment Guide

This guide covers deploying the GCB platform to production.

## Prerequisites

Before deploying, ensure you have:
- [ ] Railway account (or alternative hosting)
- [ ] Auth0 production tenant configured
- [ ] Stripe live account (with webhook configured)
- [ ] PostgreSQL database provisioned
- [ ] Domain name configured
- [ ] SSL certificate (usually automatic with Railway)

## Railway Deployment

### 1. Create Railway Project

1. Go to [Railway](https://railway.app)
2. Create a new project
3. Add PostgreSQL service
4. Note the database connection string

### 2. Deploy Backend

1. Connect GitHub repository
2. Select `gcb-platform/backend` as root directory
3. Configure environment variables (see below)
4. Deploy

### 3. Deploy Frontend

1. Add another service to the project
2. Select `gcb-platform/frontend` as root directory
3. Configure environment variables (see below)
4. Deploy

### 4. Configure Custom Domain

1. In Railway settings, add custom domain
2. Update DNS records as instructed
3. Wait for SSL certificate provisioning

## Environment Variables

### Backend (Production)

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Auth0
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_AUDIENCE=https://api.gcb.app

# CORS
CORS_ORIGINS_STR=https://gcb.app,https://www.gcb.app

# OpenRouter
OPENROUTER_API_KEY=sk-or-xxxxxxxx
OPENROUTER_REFERER=https://gcb.app

# Runner API
RUNNER_API_KEY=your-secure-runner-key

# Stripe (Live)
STRIPE_SECRET_KEY=sk_live_xxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxx

# Email
RESEND_API_KEY=re_xxxxxxxx
EMAIL_FROM=Great Commission Benchmark <noreply@gcb.app>
```

### Frontend (Production)

```env
# Auth0
AUTH0_SECRET=your-32-byte-secret
AUTH0_BASE_URL=https://gcb.app
AUTH0_ISSUER_BASE_URL=https://your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret

# API
NEXT_PUBLIC_API_URL=https://api.gcb.app

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxx

# Analytics (optional)
NEXT_PUBLIC_UMAMI_SCRIPT_URL=https://analytics.gcb.app/umami.js
NEXT_PUBLIC_UMAMI_WEBSITE_ID=your-website-id
```

## Database Migration

After deploying the backend, run migrations:

```bash
# Via Railway CLI
railway run alembic upgrade head

# Or via Railway shell
# 1. Go to backend service in Railway
# 2. Open shell
# 3. Run: alembic upgrade head
```

## Stripe Webhook Setup

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://api.gcb.app/api/webhooks/stripe`
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.refunded`
4. Copy webhook signing secret to `STRIPE_WEBHOOK_SECRET`

## Auth0 Production Setup

1. Create production tenant (or use existing)
2. Create "Regular Web Application"
3. Configure URLs:
   - **Allowed Callback URLs**: `https://gcb.app/api/auth/callback`
   - **Allowed Logout URLs**: `https://gcb.app`
   - **Allowed Web Origins**: `https://gcb.app`
4. Create API:
   - **Identifier**: `https://api.gcb.app`
   - **Signing Algorithm**: RS256
5. Set up roles in Auth0:
   - `user` (default)
   - `moderator`
   - `admin`
6. Create Rule/Action to add role to token

## SSL/TLS

Railway provides automatic SSL. Ensure:
- [ ] All traffic uses HTTPS
- [ ] HSTS headers are enabled (already configured)
- [ ] No mixed content warnings

## Monitoring

### Health Checks

- Backend: `https://api.gcb.app/health`
- Frontend: Check Railway metrics

### Logging

Railway provides built-in logging:
1. Go to service in Railway
2. View Deployments → Logs

For advanced monitoring, consider:
- Sentry for error tracking
- DataDog for APM
- Prometheus + Grafana for metrics

### Alerts

Set up Railway alerts for:
- Deployment failures
- High error rates
- Resource utilization

## Backup Strategy

### Database Backups

Railway PostgreSQL includes automatic daily backups.

For additional protection:
1. Enable point-in-time recovery
2. Configure backup retention (default: 7 days)
3. Test restoration periodically

### Manual Backup

```bash
# Create backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore backup
psql $DATABASE_URL < backup_20250101.sql
```

## Scaling

### Horizontal Scaling

In Railway:
1. Go to service settings
2. Increase replica count
3. Configure load balancing (automatic)

### Vertical Scaling

Adjust Railway resources:
- CPU (vCPU)
- Memory (GB)

### Database Scaling

For high traffic:
1. Upgrade PostgreSQL plan
2. Consider read replicas
3. Implement connection pooling (PgBouncer)

## Security Checklist

Before going live:

- [ ] All secrets are in environment variables (not code)
- [ ] HTTPS enforced everywhere
- [ ] Auth0 configured correctly
- [ ] Stripe webhook secret configured
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] CORS origins restricted to production domains
- [ ] Database access restricted to app only
- [ ] Dependency vulnerabilities checked

## Troubleshooting

### Deployment Failures

1. Check build logs in Railway
2. Verify environment variables are set
3. Check Dockerfile syntax
4. Ensure port matches (8000 for backend, 3000 for frontend)

### Database Connection Issues

1. Verify DATABASE_URL format
2. Check PostgreSQL service is running
3. Ensure connection limit not exceeded
4. Check network rules

### Auth0 Issues

1. Verify all URLs match exactly
2. Check token audience matches
3. Ensure secrets are current
4. Review Auth0 logs for errors

### Payment Failures

1. Check Stripe dashboard for details
2. Verify webhook is receiving events
3. Check webhook signature verification
4. Review payment intent status

## Rollback Procedure

If a deployment causes issues:

1. Go to Railway deployments
2. Select previous successful deployment
3. Click "Rollback"
4. Verify service is healthy

For database rollbacks:
```bash
# View migrations
alembic history

# Rollback one step
alembic downgrade -1

# Rollback to specific revision
alembic downgrade revision_id
```

## Maintenance Mode

To put the site in maintenance mode:

1. Create maintenance page in frontend
2. Configure Railway to serve maintenance page
3. Or use Cloudflare's maintenance mode

## Go-Live Checklist

- [ ] All environment variables set
- [ ] Database migrated
- [ ] Stripe webhook configured
- [ ] Auth0 URLs updated
- [ ] DNS configured
- [ ] SSL working
- [ ] Health checks passing
- [ ] Test user flow end-to-end
- [ ] Test payment flow (small amount)
- [ ] Monitoring configured
- [ ] Team notified
- [ ] Launch announcement ready
