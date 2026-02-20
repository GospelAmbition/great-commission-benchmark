"""Health check endpoint"""
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "gcb-backend"}


@router.get("/recaptcha")
async def recaptcha_status():
    """Report reCAPTCHA configuration status (no secrets exposed). Use to verify installation."""
    enabled = bool(settings.RECAPTCHA_ENABLED)
    secret_set = bool(settings.RECAPTCHA_SECRET_KEY and settings.RECAPTCHA_SECRET_KEY.strip())
    configured = enabled and secret_set
    return {
        "recaptcha_enabled": enabled,
        "recaptcha_configured": configured,
        "message": "reCAPTCHA is active and required for contact form"
        if configured
        else "reCAPTCHA is not configured or disabled; contact form will accept submissions without verification",
    }
