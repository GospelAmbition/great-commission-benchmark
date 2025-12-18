# Great Commission Benchmark - Backend

FastAPI backend for the Great Commission Benchmark platform.

## Setup

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
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

## Database Migrations

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

## Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## Project Structure

```
backend/
├── alembic/              # Database migrations
├── app/
│   ├── api/             # API routes
│   ├── core/            # Core configuration and utilities
│   ├── db/              # Database models and configuration
│   └── ...
├── tests/               # Test suite
├── main.py              # FastAPI application entry point
└── requirements.txt     # Python dependencies
```

## Environment Variables

See `.env.example` for required environment variables.
