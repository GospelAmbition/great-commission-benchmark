# Great Commission Benchmark Platform

Monorepo for the Great Commission Benchmark platform.

## Project Structure

```
gcb-platform/
├── backend/          # FastAPI application
├── frontend/         # Next.js application
├── shared/           # Shared types/utilities (future)
└── docker-compose.yml
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 15+ (or Docker)
- Auth0 account (for authentication)

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Start PostgreSQL (using Docker):
   ```bash
   cd ..
   docker-compose up -d postgres
   ```

6. Run migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

7. Start development server:
   ```bash
   uvicorn main:app --reload
   ```

   Backend will be available at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your Auth0 configuration
   ```

4. Start development server:
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:3000`

## Development

### Running Tests

**Backend:**
```bash
cd backend
pytest
```

**Frontend:**
```bash
cd frontend
npm test
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

## Environment Variables

### Backend (.env)

See `backend/.env.example` for required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `AUTH0_DOMAIN` - Auth0 tenant domain
- `AUTH0_CLIENT_ID` - Auth0 client ID
- `AUTH0_CLIENT_SECRET` - Auth0 client secret
- `AUTH0_AUDIENCE` - Auth0 API audience

### Frontend (.env.local)

See `frontend/.env.example` for required variables:
- `AUTH0_SECRET` - Secret for session encryption (generate with `openssl rand -hex 32`)
- `AUTH0_BASE_URL` - Base URL of your app
- `AUTH0_ISSUER_BASE_URL` - Auth0 tenant URL
- `AUTH0_CLIENT_ID` - Auth0 client ID
- `AUTH0_CLIENT_SECRET` - Auth0 client secret
- `NEXT_PUBLIC_API_URL` - Backend API URL

## Phase A Status

Phase A (Foundation) includes:

- ✅ Monorepo structure
- ✅ Backend FastAPI setup with health endpoint
- ✅ Frontend Next.js setup with shadcn/ui
- ✅ Database models and migrations
- ✅ Auth0 integration (backend and frontend)
- ✅ Docker Compose for local PostgreSQL
- ✅ Basic tests

See `BUILD-TASKS.md` for detailed progress tracking.

## Documentation

- [Build Tasks](./BUILD-TASKS.md) - Detailed build checklist
- [Backend README](./backend/README.md) - Backend-specific documentation
- [Frontend README](./frontend/README.md) - Frontend-specific documentation
- [Specifications](../benchmark/) - Technical specifications

## License

See main repository LICENSE file.
