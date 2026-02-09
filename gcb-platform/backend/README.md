# Great Commission Benchmark - Backend

FastAPI backend for the Great Commission Benchmark platform.

## Overview

The backend provides:
- RESTful API for all platform functionality
- Benchmark test execution engine
- LLM-as-Judge evaluation system
- Payment processing via Stripe
- Email notifications via Resend
- Moderation workflow management

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Virtual environment tool (venv)

### Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up database:**
   ```bash
   # Make sure PostgreSQL is running
   # Update DATABASE_URL in .env
   
   # Run migrations
   alembic upgrade head
   ```

5. **Run development server:**
   ```bash
   uvicorn main:app --reload --port 8001
   ```
   Or: `./run_dev.sh`

   The API will be available at `http://localhost:8001`

6. **Set up initial administrator account:**
   
   The platform uses Google OAuth for authentication. Users are automatically created when they first sign in, but they start with the default "user" role. To set up your initial admin account:
   
   a. **Sign in to the platform** using Google OAuth (this creates your user account)
   
   b. **Promote your account to admin** using the setup script:
      ```bash
      # Activate your virtual environment first
      source venv/bin/activate
      
      # Promote your email to admin
      python scripts/create_admin.py --email your-email@example.com
      
      # Or list all users to find your email
      python scripts/create_admin.py --list-users
      ```
   
   Once you have admin privileges, you can:
   - Access the admin dashboard at `/admin` in the frontend
   - Manage other users via the admin API endpoints
   - Create and manage question sets
   - View system metrics and statistics

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

### API Structure

```
/api
├── /health          # Health check
├── /public          # Public endpoints (leaderboard, models, stats)
├── /user            # Authenticated user endpoints
├── /tests           # Test creation and management
├── /submissions     # CLI submission handling
├── /runner          # Question delivery (API key auth)
├── /newsletter      # Newsletter subscription
├── /payments        # Stripe payment handling
├── /webhooks        # Webhook handlers (Stripe)
├── /moderator       # Moderation queue and reviews
└── /admin           # Admin management endpoints
```

### Authentication

- **Public endpoints**: No authentication required
- **User endpoints**: JWT Bearer token (NextAuth v5 with Google OAuth)
- **Runner endpoints**: User API key authentication (per-user keys stored in database)
- **Admin endpoints**: JWT with admin permission (`can_admin`)

### Rate Limiting

| Endpoint Type | Limit |
|---------------|-------|
| Public API | 100 req/min |
| Authenticated | 300 req/min |
| Questions API | 50 req/hour |

## Project Structure

```
backend/
├── alembic/                  # Database migrations
│   ├── versions/             # Migration files
│   └── env.py               # Alembic configuration
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/   # API route handlers
│   │       └── router.py    # API router
│   ├── core/
│   │   ├── auth.py          # Authentication utilities
│   │   ├── cache.py         # Caching utilities
│   │   ├── config.py        # Application settings
│   │   ├── security_headers.py  # Security middleware
│   │   └── validation.py    # Input validation
│   ├── db/
│   │   ├── base.py          # Database connection
│   │   └── models/          # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   └── services/            # Business logic
├── tests/                   # Test suite
├── main.py                  # FastAPI application
└── requirements.txt         # Python dependencies
```

## Database

### Models

| Model | Description |
|-------|-------------|
| `User` | Platform users with permission-based access control |
| `UserAPIKey` | User-generated API keys for Runner CLI access |
| `Model` | AI models available for testing |
| `ModelVersionStats` | Aggregated statistics per model version |
| `QuestionSet` | Benchmark question versions |
| `Question` | Individual test questions with metadata |
| `MethodologyVersion` | Methodology version tracking |
| `TestRun` | Test execution instances |
| `Result` | Individual question results with thought process |
| `ModerationLog` | Review history |
| `CommunitySubmission` | CLI-submitted results |
| `SponsorshipRequest` | Community sponsorship requests |
| `NewsletterSubscriber` | Newsletter subscription management |
| `BlogPost` | Blog posts for insights/articles |
| `BlogCategory` | Blog post categories |
| `VolunteerApplication` | Volunteer application submissions |
| `NotificationPreference` | User notification preferences |
| `StripeConfig` | Encrypted Stripe configuration storage |

### Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

View current revision:
```bash
alembic current
```

## Services

The backend includes the following service modules:

| Service | Description |
|---------|-------------|
| `aggregation` | Leaderboard and statistics aggregation |
| `cache_warmer` | Background cache warming and refresh |
| `email` | Transactional email sending via Resend |
| `judge` | LLM-as-judge evaluation logic |
| `model_sync` | OpenRouter model synchronization |
| `newsletter` | MailerLite newsletter integration |
| `openrouter` | OpenRouter API client |
| `payment` | Stripe payment processing |
| `pricing` | Test pricing calculations |
| `question_management` | Question import and version management |
| `scoring` | Benchmark scoring calculations |
| `storage` | S3-compatible file storage (Railway Storage) |
| `submission_processor` | CLI submission processing |
| `token_counting` | Token counting utilities |

## Testing

Run all tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_phase_e.py -v
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `CORS_ORIGINS_STR` | Allowed CORS origins (comma-separated) | `localhost` |
| `NEXTAUTH_SECRET` | NextAuth JWT signing secret | Required |
| `OPENROUTER_API_KEY` | OpenRouter API key | Required |
| `OPENROUTER_REFERER` | OpenRouter referer header | Required |
| `STRIPE_SECRET_KEY` | Stripe secret key | Optional |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | Optional |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | Optional |
| `PAYMENT_DEV_MODE` | Bypass payment processing (dev only) | `False` |
| `RESEND_API_KEY` | Resend email API key | Optional |
| `EMAIL_FROM` | Email sender address | Required if using email |
| `MAILERLITE_API_KEY` | MailerLite newsletter API key | Optional |
| `MAILERLITE_GROUP_ID` | MailerLite subscriber group ID | Optional |
| `S3_ACCESS_KEY_ID` | S3-compatible storage access key | Optional |
| `S3_SECRET_ACCESS_KEY` | S3-compatible storage secret | Optional |
| `S3_BUCKET` | Storage bucket name | Optional |
| `S3_ENDPOINT_URL` | Storage endpoint URL | Optional |
| `S3_REGION` | Storage region | `us-east-1` |
| `BACKEND_PUBLIC_URL` | Backend public URL for file proxy | Required if using storage |
| `RECAPTCHA_SECRET_KEY` | Google reCAPTCHA v3 secret key | Optional |
| `RECAPTCHA_ENABLED` | Enable/disable reCAPTCHA verification | `True` |

## Security

### Security Headers

The following security headers are added to all responses:
- `Content-Security-Policy`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security` (HTTPS only)

### Input Validation

- All endpoints use Pydantic schemas for validation
- SQL injection prevented via SQLAlchemy ORM
- Email validation on user inputs
- Length limits on text fields
- Google reCAPTCHA v3 spam protection on newsletter subscriptions

### Authentication

- JWT tokens validated via NextAuth v5 (HS256 algorithm)
- Permission-based access control (can_view_benchmark, can_edit_benchmark, can_moderate, can_manage_blog, can_admin)
- User API key authentication for runner endpoints (keys stored as hashed values)
- Google OAuth as identity provider

## Caching

The API includes in-memory caching for frequently accessed data:

| Data | TTL |
|------|-----|
| Leaderboard | 5 minutes |
| Model details | 5 minutes |
| Public stats | 5 minutes |
| Versions | 10 minutes |

Cache headers (`X-Cache: HIT/MISS`) indicate cache status.

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["/app/start.sh"]  # uses PORT (default 8080); for local dev run uvicorn --port 8001
```

### Railway

The backend auto-deploys from the `backend/` directory. Ensure all environment variables are configured in Railway's settings.

## Monitoring

### Health Check

```bash
curl http://localhost:8001/health
# {"status": "ok"}
```

### Logging

Application logs are output to stdout. In production, configure your hosting provider's log aggregation.

## Common Issues

### Database Connection Errors

- Verify `DATABASE_URL` is correct
- Ensure PostgreSQL is running
- Check network connectivity

### Authentication Failures

- Verify NextAuth configuration
- Check JWT token expiration
- Ensure token is valid and not expired

### Migration Errors

- Run `alembic upgrade head` after pulling changes
- Check for conflicting migration branches
- Verify database user has CREATE permissions

## API Examples

### Get Leaderboard

```bash
curl http://localhost:8001/api/public/leaderboard?limit=10
```

### Get Platform Stats

```bash
curl http://localhost:8001/api/public/stats
```

### Create Test (authenticated)

```bash
curl -X POST http://localhost:8001/api/tests \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model_id": "uuid", "version": "1.0"}'
```

### Upload CLI Submission (authenticated)

Upload test results exported from gcb-runner:

```bash
curl -X POST http://localhost:8001/api/submissions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "export_data": {
      "format_version": "1.0",
      "test_run": {
        "id": "local-1",
        "model": "gpt-4o",
        "backend": "openrouter",
        "benchmark_version": "1.0.0",
        "judge_model": "gpt-4o",
        "completed_at": "2024-01-01T00:00:00Z"
      },
      "summary": {
        "total_questions": 100,
        "score": 85.5,
        "scoring_weights": {
          "tier1": 0.70,
          "tier2": 0.20,
          "tier3": 0.10
        },
        "tier_scores": {
          "tier1": {"raw": 90.0, "weighted": 63.0, "questions": 50},
          "tier2": {"raw": 80.0, "weighted": 16.0, "questions": 30},
          "tier3": {"raw": 65.0, "weighted": 6.5, "questions": 20}
        },
        "verdict_counts": {
          "pass": 70,
          "partial": 20,
          "fail": 10
        }
      },
      "responses": [...],
      "metadata": {
        "cli_version": "1.0.0",
        "benchmark_version": "1.0.0",
        "benchmark_checksum": "sha256:...",
        "timestamp": "2024-01-01T00:00:00Z",
        "export_source": "cli_runner"
      }
    }
  }'
```

**Response:**
- If fee is waived: Submission created with `status: "pending"`
- If payment required: Submission created with `status: "pending_payment"` and `payment_intent_id` provided
- If validation fails: Returns `validation_errors` array with error messages

---

For more information, see the [main README](../README.md) or [API documentation](http://localhost:8001/docs).
