"""
Great Commission Benchmark Platform - FastAPI Backend
"""
import logging
import sys
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

logger.info("Starting main.py import...")

from app.core.config import settings
logger.info("Config loaded successfully")

from app.core.security_headers import SecurityHeadersMiddleware
logger.info("Security headers middleware loaded")

from app.api.v1.router import api_router
logger.info("API router loaded successfully")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    logger.info("Application startup complete - ready to serve requests")
    yield
    # Shutdown
    logger.info("Application shutting down")


app = FastAPI(
    title="Great Commission Benchmark API",
    description="API for the Great Commission Benchmark platform",
    version="1.0.0",
    lifespan=lifespan,
)
logger.info("FastAPI app instance created")

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


# Exception handler to log errors
# Note: HTTPException and RequestValidationError are handled by FastAPI's built-in handlers
# This only catches truly unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Log all unhandled exceptions with full traceback and ensure CORS headers are present"""
    logger.error(f"Unhandled exception on {request.method} {request.url.path}:")
    logger.error(traceback.format_exc())
    
    # Create response
    response = JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
    
    # Ensure CORS headers are added for error responses
    origin = request.headers.get("origin")
    if origin and origin in settings.CORS_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint - returns ok immediately.
    
    This ensures the app can pass healthchecks even before the database is ready.
    The health check should be fast and not block on external dependencies.
    """
    return {"status": "ok"}


logger.info("===== Application module loaded successfully =====")
logger.info(f"CORS origins configured: {settings.CORS_ORIGINS}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
