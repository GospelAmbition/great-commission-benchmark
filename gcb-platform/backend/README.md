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
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

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
- **User endpoints**: JWT Bearer token (Auth0)
- **Runner endpoints**: API key authentication
- **Admin endpoints**: JWT with admin role

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
| `User` | Platform users |
| `Model` | AI models available for testing |
| `QuestionSet` | Benchmark question versions |
| `Question` | Individual test questions |
| `TestRun` | Test execution instances |
| `Result` | Individual question results |
| `ModerationLog` | Review history |
| `CommunitySubmission` | CLI-submitted results |

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
| `AUTH0_DOMAIN` | Auth0 tenant domain | Required |
| `AUTH0_CLIENT_ID` | Auth0 client ID | Required |
| `AUTH0_CLIENT_SECRET` | Auth0 client secret | Required |
| `AUTH0_AUDIENCE` | Auth0 API audience | Required |
| `CORS_ORIGINS_STR` | Allowed CORS origins | `localhost` |
| `OPENROUTER_API_KEY` | OpenRouter API key | Required |
| `RUNNER_API_KEY` | API key for runner access | Required |
| `STRIPE_SECRET_KEY` | Stripe secret key | Optional |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | Optional |
| `RESEND_API_KEY` | Resend email API key | Optional |

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

### Authentication

- JWT tokens validated against Auth0 JWKS
- Role-based access control (user, moderator, admin)
- API key authentication for runner endpoints

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
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Railway

The backend auto-deploys from the `backend/` directory. Ensure all environment variables are configured in Railway's settings.

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
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

- Verify Auth0 configuration
- Check JWT token expiration
- Ensure audience matches

### Migration Errors

- Run `alembic upgrade head` after pulling changes
- Check for conflicting migration branches
- Verify database user has CREATE permissions

## API Examples

### Get Leaderboard

```bash
curl http://localhost:8000/api/public/leaderboard?limit=10
```

### Get Platform Stats

```bash
curl http://localhost:8000/api/public/stats
```

### Create Test (authenticated)

```bash
curl -X POST http://localhost:8000/api/tests \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model_id": "uuid", "version": "1.0"}'
```

---

For more information, see the [main README](../README.md) or [API documentation](http://localhost:8000/docs).
