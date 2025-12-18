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
    """Health check endpoint - returns ok even if database is not ready"""
    try:
        # Try to check database connectivity without failing
        from sqlalchemy import text
        from app.db.base import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        # Return ok even if database check fails - app can start without DB
        # Railway will retry, and once DB is ready, it will show connected
        return {"status": "ok", "database": "checking"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
