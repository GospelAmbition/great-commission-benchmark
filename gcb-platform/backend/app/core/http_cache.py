"""HTTP cache headers for public, slowly changing benchmark data."""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Short browser TTL, 5-minute shared/edge TTL, and a long stale window so
# crawlers and the Next.js data cache can reuse responses. Backend Redis is
# still invalidated immediately when new results publish.
PUBLIC_CACHE_CONTROL = (
    "public, max-age=60, s-maxage=300, stale-while-revalidate=86400"
)


def set_public_cache_headers(response: Response | None, cache_status: str | None = None) -> None:
    """Attach Cache-Control (and optional X-Cache) to a public GET response."""
    if response is None:
        return
    response.headers["Cache-Control"] = PUBLIC_CACHE_CONTROL
    if cache_status:
        response.headers["X-Cache"] = cache_status


class PublicCacheControlMiddleware(BaseHTTPMiddleware):
    """Add Cache-Control to successful public GET responses that omit it."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        if (
            request.method == "GET"
            and request.url.path.startswith("/api/public")
            and response.status_code == 200
            and "cache-control" not in response.headers
        ):
            response.headers["Cache-Control"] = PUBLIC_CACHE_CONTROL
        return response
