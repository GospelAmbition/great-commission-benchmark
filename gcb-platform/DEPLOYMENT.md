# Great Commission Benchmark - Deployment Guide

This guide covers deploying the GCB platform to production.

## Current Test Deployment (Railway)

| Service | URL |
|---------|-----|
| Backend | https://backend-production-ba51.up.railway.app |
| Frontend | https://frontend-production-8b79.up.railway.app |
| Health Check | https://backend-production-ba51.up.railway.app/health |

These are temporary Railway URLs for testing. Production domain (greatcommissionbenchmark.ai) will be configured later.

## Prerequisites

Before deploying, ensure you have:
- [ ] Railway account (or alternative hosting)
- [ ] Google OAuth credentials configured
- [ ] Stripe live account (with webhook configured)
- [ ] PostgreSQL database provisioned
- [ ] Railway Storage Bucket for blog images
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

### 4. Set Up Storage Bucket (for Blog Images)

1. In Railway project dashboard, click **New Service** → **Bucket**
2. Name your bucket (e.g., `gcb-storage`)
3. Once created, note the following from the bucket settings:
   - **Bucket Name**
   - **Endpoint URL** (e.g., `https://your-bucket.storage.railway.app`)
   - **Access Key ID**
   - **Secret Access Key**
4. Configure CORS for browser uploads (if needed):
   ```bash
   AWS_ACCESS_KEY_ID=your_access_key_id \
   AWS_SECRET_ACCESS_KEY=your_secret_access_key \
   aws s3api put-bucket-cors \
     --bucket your_bucket_name \
     --endpoint-url https://your-bucket.storage.railway.app \
     --cors-configuration '{
       "CORSRules": [
         {
           "AllowedHeaders": ["*"],
           "AllowedMethods": ["PUT", "POST", "GET"],
           "AllowedOrigins": ["https://greatcommissionbenchmark.ai", "https://frontend-production-8b79.up.railway.app"],
           "MaxAgeSeconds": 3000
         }
       ]
     }'
   ```

### 5. Configure Custom Domain

1. In Railway settings, add custom domain
2. Update DNS records as instructed
3. Wait for SSL certificate provisioning

## Environment Variables

### Backend (Production)

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# CORS
CORS_ORIGINS_STR=https://greatcommissionbenchmark.ai,https://www.greatcommissionbenchmark.ai

# OpenRouter
OPENROUTER_API_KEY=sk-or-xxxxxxxx
OPENROUTER_REFERER=https://greatcommissionbenchmark.ai

# Runner API
RUNNER_API_KEY=your-secure-runner-key

# Stripe (Live)
STRIPE_SECRET_KEY=sk_live_xxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxx

# Email
RESEND_API_KEY=re_xxxxxxxx
EMAIL_FROM=Great Commission Benchmark <noreply@greatcommissionbenchmark.ai>

# Storage (Railway Simple Storage)
S3_ACCESS_KEY_ID=your-railway-access-key
S3_SECRET_ACCESS_KEY=your-railway-secret-key
S3_BUCKET=your-bucket-name
S3_ENDPOINT_URL=https://your-bucket.storage.railway.app
S3_REGION=us-east-1
S3_PUBLIC_URL_BASE=https://your-bucket.storage.railway.app
```

### Frontend (Production)

```env
# NextAuth
AUTH_URL=https://greatcommissionbenchmark.ai
NEXTAUTH_SECRET=your-32-byte-secret

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# API
NEXT_PUBLIC_API_URL=https://api.greatcommissionbenchmark.ai

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxx

# Analytics (optional)
NEXT_PUBLIC_UMAMI_SCRIPT_URL=https://analytics.greatcommissionbenchmark.ai/umami.js
NEXT_PUBLIC_UMAMI_WEBSITE_ID=your-website-id
```

### Railway Test Environment Variables

For the current Railway test deployment:

**Backend:**
```env
CORS_ORIGINS_STR=http://localhost:3000,https://frontend-production-8b79.up.railway.app

# Storage (Railway Simple Storage) - get these from your Railway bucket
S3_ACCESS_KEY_ID=your-railway-access-key
S3_SECRET_ACCESS_KEY=your-railway-secret-key
S3_BUCKET=your-bucket-name
S3_ENDPOINT_URL=https://your-bucket.storage.railway.app
S3_REGION=us-east-1
S3_PUBLIC_URL_BASE=https://your-bucket.storage.railway.app
```

**Frontend:**
```env
NEXT_PUBLIC_API_URL=https://backend-production-ba51.up.railway.app
AUTH_URL=https://frontend-production-8b79.up.railway.app
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
NEXTAUTH_SECRET=your-32-byte-secret
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
2. Add endpoint: `https://api.greatcommissionbenchmark.ai/api/webhooks/stripe`
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.refunded`
4. Copy webhook signing secret to `STRIPE_WEBHOOK_SECRET`

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **OAuth client ID**
   - Application type: **Web application**
   - Authorized redirect URIs: `https://greatcommissionbenchmark.ai/api/auth/callback`
   - For Railway test: `https://frontend-production-8b79.up.railway.app/api/auth/callback`
5. Copy the Client ID and Client Secret to your environment variables
6. Generate `NEXTAUTH_SECRET`:
   ```bash
   openssl rand -base64 32
   ```

## SSL/TLS

Railway provides automatic SSL. Ensure:
- [ ] All traffic uses HTTPS
- [ ] HSTS headers are enabled (already configured)
- [ ] No mixed content warnings

## Monitoring

### Health Checks

- Backend: `https://api.greatcommissionbenchmark.ai/health`
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
- [ ] Google OAuth configured correctly
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

### Authentication Issues

1. Verify `AUTH_URL` matches your frontend domain exactly
2. Check Google OAuth callback URLs match
3. Ensure `NEXTAUTH_SECRET` is set and valid
4. Verify Google OAuth credentials are correct
5. Check NextAuth logs for errors

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
- [ ] Google OAuth configured
- [ ] Railway Storage Bucket configured
- [ ] DNS configured
- [ ] SSL working
- [ ] Health checks passing
- [ ] Test user flow end-to-end
- [ ] Test payment flow (small amount)
- [ ] Test blog image upload
- [ ] Monitoring configured
- [ ] Team notified
- [ ] Launch announcement ready
