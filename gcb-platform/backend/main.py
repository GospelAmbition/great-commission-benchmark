"""
Great Commission Benchmark Platform - FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.security_headers import SecurityHeadersMiddleware
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Great Commission Benchmark API",
    description="API for the Great Commission Benchmark platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Security headers middleware (must be first)
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint - returns ok immediately, then checks database.
    
    This ensures the app can pass healthchecks even before the database is ready.
    """
    # Return ok immediately - the app is running and can accept requests
    # Database connectivity is checked separately for monitoring purposes
    db_status = "unknown"
    try:
        from sqlalchemy import text
        from app.db.base import get_engine_safe
        engine = get_engine_safe()
        if engine:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_status = "connected"
        else:
            db_status = "not_configured"
    except Exception:
        db_status = "checking"
    
    return {"status": "ok", "database": db_status}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
