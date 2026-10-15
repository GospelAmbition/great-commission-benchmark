# Great Commission Benchmark Platform

A comprehensive platform for evaluating Large Language Models (LLMs) on their ability to support Great Commission Christians through accurate biblical knowledge, sound theological understanding, and alignment with Christian worldview values.

## Project Structure

```
gcb-platform/
├── backend/          # FastAPI application (Python 3.11+)
├── frontend/         # Next.js application (Node.js 20.9+)
├── docker-compose.yml
└── README.md
```

## Features

- **Benchmark Testing**: Run comprehensive tests on any AI model via OpenRouter
- **Public Leaderboard**: Browse and compare model performance
- **User Dashboard**: Track your tests, view results, manage submissions
- **CLI Submission Upload**: Upload test results from gcb-runner via web dashboard
- **Moderator Interface**: Review test results for quality assurance
- **Admin Panel**: Manage users, questions, and benchmark versions
- **Blog System**: Publish insights and articles with image uploads
- **Newsletter**: MailerLite integration for subscriber management
- **Payment Integration**: Stripe-powered test payments with transparent pricing
- **API Access**: RESTful API for programmatic access
- **User API Keys**: Per-user API keys for Runner CLI authentication

## Quick Start

### Repository root commands

Run these from the Git repository root (one directory above `gcb-platform`):

```bash
./launch --check   # Read-only prerequisite/context/port check
./launch          # Same as ./launch start; wait for readiness, then return
./launch status
./launch close    # ./launch stop is an alias
./sync --help
./sync            # Prompts: type overwrite local gcb
```

Requires macOS or Linux, Python 3.11+ for the backend, `python3` for the launcher,
Node.js 20.9+, npm, and Docker Compose. On macOS, the commands open Docker Desktop
if its daemon is stopped and wait for readiness. On Linux, start the Docker daemon
first. Only local Docker Unix-socket contexts are accepted; remote contexts are
refused. No host PostgreSQL or Redis installation is needed.

`./launch` starts the existing Compose PostgreSQL 17 service, installs backend
requirements in an existing `backend/.venv` or `backend/venv` (or creates `.venv`),
and runs `npm ci` when dependency manifests change or dependencies are missing.
It applies Alembic migrations to the local database, starts Uvicorn on port 8001
and Next.js on port 3001, and waits for HTTP readiness. Repeated calls reuse the
running launcher; use `./launch close` then `./launch` to restart. An unrelated
process using either web port causes an error. If either managed server fails,
the launcher stops both servers. Docker PostgreSQL remains running after close.

The launcher pins the database to `127.0.0.1:5433/gcb` with the Compose development
credentials (`postgres` / `postgres`); PostgreSQL is published only on loopback. Set `POSTGRES_PORT` in the invoking shell to
use another local database port; the same value is passed to Compose and Alembic.
It pins API/site/auth/CORS URLs to localhost, disables Redis and the newsletter
sync worker, and generates a shared local NextAuth secret. Existing
`backend/.env` and `frontend/.env.local` files remain available for optional
integration settings; they are not rewritten. Google sign-in requires
`GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `frontend/.env.local`, with the
OAuth redirect URI `http://localhost:3001/api/auth/callback/google` allowed.
Outbound Resend, MailerLite, Stripe, S3 and OpenRouter credentials are cleared in
the local process. The separate local auth secret also prevents decryption of
copied production Stripe credentials. No copied database records are rewritten
for this isolation. Public pages can run without OAuth or paid service credentials. Launch does not
populate an empty database with benchmark results; use sync separately if needed.

Private logs, dependency stamps, and the local auth secret live in ignored
`.local-run/` at the repository root:

```bash
tail -f .local-run/launch.log .local-run/backend.log .local-run/frontend.log
```

`./sync` uses `RAILWAY_DATABASE_URL` from the invoking process or
`gcb-platform/backend/.env` (process value wins). Use Railway's externally
reachable PostgreSQL connection URL, not a `railway.internal` hostname. Stop
managed web servers with `./launch close` first. After typed confirmation, sync
starts local PostgreSQL, saves a private local SQL backup, reads Railway with a
PostgreSQL 17 dump client in read-only mode, and replaces the local application
schema in one transaction. A dump failure leaves local data intact; a restore
failure rolls back. The script refuses concurrent launch/sync and remote Docker
targets. It never writes to the Railway database, and launch never calls sync.

Sync prints the private backup/dump paths. Keep the backup and prepared recovery file until you have verified
the refreshed database, then delete it when no longer needed. To recover a saved
backup with web servers stopped (replace `/path/to/local-recovery.sql` with the
printed prepared-recovery path). Use the same local Docker context;
`./launch --check` verifies it without changing data:

```bash
docker compose -p gcb-platform -f gcb-platform/docker-compose.yml exec -T postgres \
  psql -X -h 127.0.0.1 -U postgres -d gcb --single-transaction -v ON_ERROR_STOP=1 \
  < /path/to/local-recovery.sql
```

The database is a point-in-time snapshot. PostgreSQL 17, UTF8 and `en_US.utf8`
match the verified production database. Compose uses a separate `postgres17_data`
volume; any older PostgreSQL 15 volume is retained rather than opened by a newer
server. Application schema/data are restored; source role ownership and grants
are intentionally omitted for the local `postgres` role. Unsupported additional
schemas or server major versions fail before restore.

Run `./launch` after sync or recovery to apply any newer local migrations; those
migrations can intentionally advance the local schema beyond the snapshot.
These commands do not configure or deploy Railway services.

### Prerequisites

- Node.js 20.9+ (for frontend)
- Python 3.11+ (for backend)
- PostgreSQL 15+ (or Docker)
- Google Cloud account (for OAuth, required for authentication)
- Stripe account (for payments, optional for development)
- Resend account (for transactional emails, optional for development)
- MailerLite account (for newsletter, optional for development)
- Railway account (for storage bucket, optional for development)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start PostgreSQL (using Docker):**
   ```bash
   cd ..
   docker-compose up -d postgres
   ```

6. **Run migrations:**
   ```bash
   cd backend
   alembic upgrade head
   ```

7. **Start development server:**
   ```bash
   uvicorn main:app --reload --port 8001
   ```
   Or from backend: `./run_dev.sh`

   Backend will be available at `http://localhost:8001`
   - API docs (Swagger): `http://localhost:8001/docs`
   - API docs (ReDoc): `http://localhost:8001/redoc`
   - Health check: `http://localhost:8001/health`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:3001`

## Development

### Running Tests

**Backend:**
```bash
cd backend
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest --cov=app --cov-report=html  # With coverage report
```

**Frontend:**
```bash
cd frontend
npm test                        # Run tests
npm run test:watch             # Watch mode
```

### Database Migrations

Create a new migration:
```bash
cd backend
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

### Linting and Formatting

**Frontend:**
```bash
npm run lint                   # Run ESLint
npm run lint:fix              # Fix auto-fixable issues
```

## Environment Variables

### Backend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `NEXTAUTH_SECRET` | NextAuth JWT signing secret (same for frontend and backend) | Yes |
| `OPENROUTER_API_KEY` | OpenRouter API key for model access | Yes |
| `OPENROUTER_REFERER` | OpenRouter referer header | Yes |
| `STRIPE_SECRET_KEY` | Stripe secret key | Production |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | Production |
| `RESEND_API_KEY` | Resend email service API key | Production |
| `EMAIL_FROM` | Email sender address | Production |
| `MAILERLITE_API_KEY` | MailerLite newsletter API key | Optional |
| `S3_ACCESS_KEY_ID` | S3-compatible storage access key | Optional |
| `S3_SECRET_ACCESS_KEY` | S3-compatible storage secret | Optional |
| `S3_BUCKET` | Storage bucket name | Optional |
| `S3_ENDPOINT_URL` | Storage endpoint URL | Optional |
| `BACKEND_PUBLIC_URL` | Backend public URL for file proxy | Optional |

### Frontend (.env.local)

| Variable | Description | Required |
|----------|-------------|----------|
| `AUTH_URL` | Base URL of your app (e.g., `http://localhost:3001`) | Yes |
| `NEXTAUTH_SECRET` | Session encryption secret (same as backend, generate with `openssl rand -base64 32`) | Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Yes |
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | Production |
| `NEXT_PUBLIC_UMAMI_SCRIPT_URL` | Umami analytics script URL | Optional |
| `NEXT_PUBLIC_UMAMI_WEBSITE_ID` | Umami website ID | Optional |

## API Documentation

The backend provides comprehensive API documentation via:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/public/leaderboard` | GET | Public leaderboard |
| `/api/public/models` | GET | List tested models |
| `/api/public/stats` | GET | Platform statistics |
| `/api/user/profile` | GET/PUT | User profile management |
| `/api/tests` | POST | Create new test |
| `/api/tests/{id}/start` | POST | Start test execution |

## Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Pydantic for validation
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: NextAuth JWT validation
- **Payments**: Stripe integration

### Frontend (Next.js)
- **Framework**: Next.js 14 with App Router
- **UI Components**: shadcn/ui + Tailwind CSS
- **Authentication**: NextAuth v5 with Google OAuth
- **Charts**: Chart.js with react-chartjs-2

### Security Features
- JWT token validation via NextAuth
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- Rate limiting on API endpoints
- Input validation and sanitization
- CORS configuration

## Deployment

### Railway (Recommended)

1. **Create Railway project**
2. **Add PostgreSQL service**
3. **Deploy backend** (auto-detects Dockerfile)
4. **Deploy frontend** (auto-detects Next.js)
5. **Configure environment variables**
6. **Set up custom domains**

### Environment Configuration

Ensure all production environment variables are set:
- Use strong secrets (generate with `openssl rand -hex 32`)
- Enable HTTPS only
- Configure proper CORS origins
- Set up Stripe live keys

## Build Status

| Phase | Status | Description |
|-------|--------|-------------|
| A | ✅ Complete | Foundation (Auth, DB, Infrastructure) |
| B | ✅ Complete | Core Backend (API, Benchmark Engine) |
| C | ✅ Complete | Frontend (UI, Charts, Dashboard) |
| D | ✅ Complete | Payments & Moderation |
| E | ✅ Complete | Launch Preparation |

See [BUILD-TASKS.md](../BUILD-TASKS.md) for detailed progress tracking.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documentation

- [Build Tasks](../BUILD-TASKS.md) - Detailed build checklist
- [Backend README](./backend/README.md) - Backend documentation
- [Frontend README](./frontend/README.md) - Frontend documentation
- [Specifications](../benchmark/) - Technical specifications

## Legal

- [Terms of Service](/terms)
- [Privacy Policy](/privacy)
- [Tester Agreement](/tester-agreement)

## License

See main repository LICENSE file.

---

**Great Commission Benchmark** - Evaluating AI models for biblical accuracy and Christian worldview alignment.
