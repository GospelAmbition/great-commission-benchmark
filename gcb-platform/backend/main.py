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

# MCP + OAuth wiring (imported lazily after the existing API loads so a
# misconfiguration in OAuth env doesn't break the dashboard).
from app.core.mcp_oauth.endpoints import router as oauth_router  # noqa: E402
from app.core.mcp_oauth.well_known import router as oauth_well_known_router  # noqa: E402
from app.core.mcp_oauth.middleware import bearer_auth_asgi  # noqa: E402
from app.core.mcp_oauth.config import get_oauth_settings  # noqa: E402
from app.mcp.app import build_mcp_app  # noqa: E402
logger.info("MCP + OAuth modules loaded")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    logger.info("Application starting up...")
    
    # Warm caches in background to not block startup
    # This ensures health checks pass immediately while cache warms
    import asyncio
    from app.services.cache_warmer import warm_all_caches, start_background_refresh
    
    async def delayed_cache_warm():
        """Warm cache after a short delay to ensure DB is ready"""
        await asyncio.sleep(2)  # Wait for DB connections to be established
        try:
            await warm_all_caches()
            start_background_refresh()
        except Exception as e:
            logger.error(f"Cache warming failed during startup: {e}")
    
    # Start cache warming task (non-blocking)
    asyncio.create_task(delayed_cache_warm())

    # Hydrate the in-process MCP OAuth signing key cache. We do this in
    # the foreground (it is a single SELECT + maybe one INSERT on first
    # boot) so /mcp + /.well-known/jwks.json never serve an empty JWKS.
    try:
        from app.core.mcp_oauth.keys import ensure_signing_key, reload_keys
        from app.db.base import SessionLocal as _SL

        with _SL() as _key_db:
            ensure_signing_key(_key_db)
            reload_keys(_key_db)
        logger.info("MCP OAuth signing key cache loaded")
    except Exception as exc:
        # Don't fail boot of the dashboard if OAuth env is incomplete in
        # this environment — /mcp will simply 401 with a clear message.
        logger.warning("MCP OAuth signing key load skipped: %s", exc)

    logger.info("Application startup complete - ready to serve requests")
    yield
    
    # Shutdown
    logger.info("Application shutting down...")
    from app.services.cache_warmer import stop_background_refresh
    stop_background_refresh()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Great Commission Benchmark API",
    description="API for the Great Commission Benchmark platform",
    version="1.0.0",
    lifespan=lifespan,
)
logger.info("FastAPI app instance created")

# Security headers middleware (must be first)
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware. The Claude.ai connector frontend and the iPhone app
# both call /mcp from claude.ai / claude.com origins; allow them in
# addition to the existing dashboard origins, and expose the headers
# the MCP transport relies on.
_MCP_CORS_EXTRA_ORIGINS = [
    "https://claude.ai",
    "https://www.claude.ai",
    "https://claude.com",
    "https://www.claude.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + _MCP_CORS_EXTRA_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "WWW-Authenticate",
        "Mcp-Session-Id",
        "MCP-Protocol-Version",
    ],
)

# Include API router
app.include_router(api_router, prefix="/api")

# OAuth discovery + endpoints + MCP transport.
# RFC 9728 / 8414 metadata MUST live at the origin root (not /api/...)
# so RFC-compliant MCP clients can discover them via well-known paths.
app.include_router(oauth_well_known_router)
app.include_router(oauth_router)
app.mount("/mcp", bearer_auth_asgi(build_mcp_app()))
logger.info("Mounted /mcp + /oauth + /.well-known endpoints")


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
    import os
    import uvicorn
    # Port: 8001 for local dev (no PORT set), otherwise use PORT (e.g. Railway)
    port = int(os.environ.get("PORT", 8001))
    # Reload in dev only (when PORT is not set); production sets PORT so reload stays off
    use_reload = "PORT" not in os.environ or os.environ.get("RELOAD", "").lower() in ("1", "true", "yes")
    uvicorn.run(
        "main:app",  # string so reloader can re-import
        host="0.0.0.0",
        port=port,
        reload=use_reload,
    )
