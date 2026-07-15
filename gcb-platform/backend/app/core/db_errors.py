"""Database error handling helpers for API endpoints."""
from fastapi import HTTPException, status
from sqlalchemy.exc import OperationalError, TimeoutError


def raise_if_db_unavailable(exc: Exception) -> None:
    """Re-raise DB connectivity errors as HTTP 503; propagate all others."""
    if isinstance(exc, (OperationalError, TimeoutError)):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable",
        ) from exc
    raise
