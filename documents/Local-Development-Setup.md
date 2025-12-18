# Great Commission Benchmark — Local Development Setup

This document provides step-by-step instructions for setting up a local development environment for the Great Commission Benchmark project.

**Last Updated:** December 17, 2025

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Repository Setup](#repository-setup)
3. [Platform Development](#platform-development)
4. [CLI Runner Development](#cli-runner-development)
5. [Environment Variables](#environment-variables)
6. [Database Setup](#database-setup)
7. [Running Services Locally](#running-services-locally)
8. [IDE Configuration](#ide-configuration)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Version | Purpose | Installation |
|----------|---------|---------|--------------|
| **Node.js** | 20.x LTS | Next.js frontend | [nodejs.org](https://nodejs.org) |
| **Python** | 3.10+ | FastAPI backend, CLI tools | [python.org](https://python.org) |
| **PostgreSQL** | 15+ | Platform database | [postgresql.org](https://postgresql.org) or Docker |
| **Git** | Latest | Version control | [git-scm.com](https://git-scm.com) |
| **pnpm** | 8+ | Node package manager | `npm install -g pnpm` |

### Optional Software

| Software | Purpose | When Needed |
|----------|---------|-------------|
| **Docker** | Run PostgreSQL, isolated environments | Alternative to local PostgreSQL |
| **LM Studio** | Local model testing | CLI Runner local model development |
| **Ollama** | Alternative local models | CLI Runner local model development |

### Verify Installation

```bash
# Check Node.js
node --version  # Should show v20.x.x

# Check Python
python --version  # Should show Python 3.10+

# Check PostgreSQL
psql --version  # Should show psql 15+

# Check pnpm
pnpm --version  # Should show 8+
```

---

## Repository Setup

### Clone the Repository

```bash
# Clone via HTTPS
git clone https://github.com/[organization]/great-commission-benchmark.git
cd great-commission-benchmark

# Or via SSH
git clone git@github.com:[organization]/great-commission-benchmark.git
cd great-commission-benchmark
```

### Repository Structure

```
great-commission-benchmark/
├── gcb-platform/              # Web platform
│   ├── frontend/             # Next.js application
│   └── backend/              # FastAPI application
├── cli/
│   └── runner/               # gcb-runner CLI tool
├── benchmark/                # Specification documents
├── documents/                # Legal and process documents
└── README.md
```

---

## Platform Development

### Frontend Setup (Next.js)

```bash
# Navigate to frontend directory
cd gcb-platform/frontend

# Install dependencies
pnpm install

# Copy environment template
cp .env.example .env.local

# Start development server
pnpm dev
```

The frontend will be available at `http://localhost:3000`.

### Backend Setup (FastAPI)

```bash
# Navigate to backend directory
cd gcb-platform/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`.

### Running Both Together

For full local development, run both services in separate terminals:

**Terminal 1 (Frontend):**
```bash
cd gcb-platform/frontend
pnpm dev
```

**Terminal 2 (Backend):**
```bash
cd gcb-platform/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

---

## CLI Runner Development

The GCB Runner CLI is used by community members to run benchmark tests.

### Setup

```bash
# Navigate to runner directory
cd cli/runner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env

# Verify installation
gcb-runner --help
```

### Development Workflow

```bash
# Run CLI commands during development
gcb-runner config --show
gcb-runner test --model gpt-4o --backend openrouter

# View results
gcb-runner results list
gcb-runner results view --id 1

# Launch results viewer
gcb-runner viewer
# Opens browser to http://localhost:8080

# Run tests
pytest

# Type checking
mypy gcb_runner/
```

### Configuration Location

| Platform | Config Path |
|----------|-------------|
| **macOS/Linux** | `~/.gcb-runner/config.json` |
| **Windows** | `%USERPROFILE%\.gcb-runner\config.json` |

---

## Environment Variables

### Platform Frontend (.env.local)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Auth0
NEXT_PUBLIC_AUTH0_DOMAIN=your-dev-tenant.auth0.com
NEXT_PUBLIC_AUTH0_CLIENT_ID=your-dev-client-id
AUTH0_CLIENT_SECRET=your-dev-client-secret

# Stripe (test mode)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx

# Analytics (optional for local dev)
# NEXT_PUBLIC_UMAMI_SCRIPT_URL=
# NEXT_PUBLIC_UMAMI_WEBSITE_ID=
```

### Platform Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/gcb_dev

# Auth0
AUTH0_DOMAIN=your-dev-tenant.auth0.com
AUTH0_CLIENT_ID=your-dev-client-id
AUTH0_CLIENT_SECRET=your-dev-client-secret
AUTH0_AUDIENCE=https://api.dev.greatcommissionbenchmark.ai

# Stripe (test mode)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# OpenRouter
OPENROUTER_API_KEY=sk-or-xxx

# Email (optional for local dev)
# SENDGRID_API_KEY=

# Application
ENVIRONMENT=development
SECRET_KEY=dev-secret-key-change-in-production
```

### CLI Runner (.env)

```bash
# LLM Backend (primary)
OPENROUTER_API_KEY=sk-or-xxx

# Alternative backends (optional)
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
LM_STUDIO_URL=http://localhost:1234
OLLAMA_URL=http://localhost:11434

# Platform (for result uploads)
GCB_PLATFORM_URL=http://localhost:3000
```

---

## Database Setup

### Option 1: Local PostgreSQL

```bash
# macOS (Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Create database and user
createdb gcb_dev
psql -d gcb_dev -c "CREATE USER gcb_user WITH PASSWORD 'your_password';"
psql -d gcb_dev -c "GRANT ALL PRIVILEGES ON DATABASE gcb_dev TO gcb_user;"

# Update DATABASE_URL in .env
# DATABASE_URL=postgresql://gcb_user:your_password@localhost:5432/gcb_dev
```

### Option 2: Docker

```bash
# Start PostgreSQL container
docker run --name gcb-postgres \
  -e POSTGRES_DB=gcb_dev \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:15

# DATABASE_URL for Docker
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/gcb_dev
```

### Running Migrations

```bash
# Navigate to backend
cd gcb-platform/backend
source venv/bin/activate

# Run all migrations
alembic upgrade head

# Create a new migration (after model changes)
alembic revision --autogenerate -m "Description of changes"

# Rollback one migration
alembic downgrade -1
```

---

## Running Services Locally

### Quick Start Script

Create a `dev.sh` script in the repository root:

```bash
#!/bin/bash

# Start all development services
echo "Starting Great Commission Benchmark development environment..."

# Terminal multiplexer (requires tmux)
tmux new-session -d -s gcb

# Frontend
tmux send-keys -t gcb "cd gcb-platform/frontend && pnpm dev" C-m

# Backend
tmux split-window -h -t gcb
tmux send-keys -t gcb "cd gcb-platform/backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000" C-m

# Attach to session
tmux attach -t gcb
```

### Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Next.js application |
| **Backend API** | http://localhost:8000 | FastAPI endpoints |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Runner Viewer** | http://localhost:8080 | Results dashboard (when running) |

---

## IDE Configuration

### VS Code (Recommended)

Install the following extensions:

| Extension | Purpose |
|-----------|---------|
| **Python** | Python language support |
| **Pylance** | Python type checking |
| **ESLint** | JavaScript/TypeScript linting |
| **Prettier** | Code formatting |
| **Tailwind CSS IntelliSense** | Tailwind class suggestions |

**Workspace Settings** (`.vscode/settings.json`):

```json
{
  "python.defaultInterpreterPath": "./gcb-platform/backend/venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "tailwindCSS.experimental.classRegex": [
    ["cva\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"]
  ]
}
```

### PyCharm

1. Open the project root folder
2. Configure Python interpreter for each project:
   - `cli/runner/venv/bin/python`
   - `gcb-platform/backend/venv/bin/python`
3. Enable Django/FastAPI support if prompted
4. Configure pytest as the test runner

---

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port
lsof -i :3000  # or :8000

# Kill process
kill -9 <PID>
```

#### Python Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

#### Database Connection Failed

```bash
# Check PostgreSQL is running
pg_isready

# Check Docker container (if using Docker)
docker ps | grep gcb-postgres

# Restart PostgreSQL
# macOS:
brew services restart postgresql@15
# Docker:
docker restart gcb-postgres
```

#### Node Module Issues

```bash
# Clear and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

#### Alembic Migration Conflicts

```bash
# Reset migrations (development only!)
alembic downgrade base
alembic upgrade head

# If still failing, drop and recreate database
dropdb gcb_dev
createdb gcb_dev
alembic upgrade head
```

### Getting Help

| Issue Type | Contact |
|------------|---------|
| **Setup problems** | Discord `#dev-help` channel |
| **Bug reports** | GitHub Issues |
| **Security concerns** | Security contact (see SECURITY.md) |

---

## Related Documents

- [Contribution Guidelines](./Contribution-Guidelines.md) — How to contribute code
- [Testing Strategies](./Testing-Strategies.md) — Testing approaches and standards
- [Deployment Procedures](./Deployment-Procedures.md) — Deployment workflow
- [Technical Decisions](./Technical-Decisions.md) — Architecture decision records

---

*This document should be updated as the development environment evolves. Last review: December 2025.*
