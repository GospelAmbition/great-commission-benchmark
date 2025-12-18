# Great Commission Benchmark Platform

A comprehensive platform for evaluating Large Language Models (LLMs) on their ability to support Great Commission Christians through accurate biblical knowledge, sound theological understanding, and alignment with Christian worldview values.

## Project Structure

```
gcb-platform/
├── backend/          # FastAPI application (Python 3.11+)
├── frontend/         # Next.js application (Node.js 18+)
├── docker-compose.yml
└── README.md
```

## Features

- **Benchmark Testing**: Run comprehensive tests on any AI model via OpenRouter
- **Public Leaderboard**: Browse and compare model performance
- **User Dashboard**: Track your tests, view results, manage submissions
- **Moderator Interface**: Review test results for quality assurance
- **Admin Panel**: Manage users, questions, and benchmark versions
- **Payment Integration**: Stripe-powered test payments with transparent pricing
- **API Access**: RESTful API for programmatic access

## Quick Start

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- PostgreSQL 15+ (or Docker)
- Auth0 account (for authentication)
- Stripe account (for payments, optional for development)

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
   uvicorn main:app --reload
   ```

   Backend will be available at `http://localhost:8000`
   - API docs (Swagger): `http://localhost:8000/docs`
   - API docs (ReDoc): `http://localhost:8000/redoc`
   - Health check: `http://localhost:8000/health`

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

   Frontend will be available at `http://localhost:3000`

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
| `AUTH0_DOMAIN` | Auth0 tenant domain | Yes |
| `AUTH0_CLIENT_ID` | Auth0 client ID | Yes |
| `AUTH0_CLIENT_SECRET` | Auth0 client secret | Yes |
| `AUTH0_AUDIENCE` | Auth0 API audience | Yes |
| `OPENROUTER_API_KEY` | OpenRouter API key for model access | Yes |
| `STRIPE_SECRET_KEY` | Stripe secret key | Production |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | Production |
| `RESEND_API_KEY` | Email service API key | Production |

### Frontend (.env.local)

| Variable | Description | Required |
|----------|-------------|----------|
| `AUTH0_SECRET` | Session encryption secret | Yes |
| `AUTH0_BASE_URL` | Base URL of your app | Yes |
| `AUTH0_ISSUER_BASE_URL` | Auth0 tenant URL | Yes |
| `AUTH0_CLIENT_ID` | Auth0 client ID | Yes |
| `AUTH0_CLIENT_SECRET` | Auth0 client secret | Yes |
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | Production |

## API Documentation

The backend provides comprehensive API documentation via:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

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
- **Authentication**: Auth0 JWT validation
- **Payments**: Stripe integration

### Frontend (Next.js)
- **Framework**: Next.js 14 with App Router
- **UI Components**: shadcn/ui + Tailwind CSS
- **Authentication**: Auth0 Next.js SDK
- **Charts**: Chart.js with react-chartjs-2

### Security Features
- JWT token validation with JWKS
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
