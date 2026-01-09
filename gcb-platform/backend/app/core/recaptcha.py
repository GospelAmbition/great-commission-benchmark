"""Google reCAPTCHA v3 verification"""
import httpx
from typing import Tuple
from app.core.config import settings


async def verify_recaptcha(token: str) -> Tuple[bool, float]:
    """Verify reCAPTCHA v3 token with Google's API.
    
    Args:
        token: The reCAPTCHA token from the frontend
        
    Returns:
        Tuple of (is_valid, score). Score is between 0.0 and 1.0.
        Returns (False, 0.0) if verification fails or is disabled.
    """
    # Skip verification if disabled or no secret key configured
    if not settings.RECAPTCHA_ENABLED or not settings.RECAPTCHA_SECRET_KEY:
        # In development, allow requests without verification
        return (True, 1.0)
    
    if not token:
        return (False, 0.0)
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": settings.RECAPTCHA_SECRET_KEY,
                    "response": token,
                },
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("success", False):
                return (False, 0.0)
            
            # Get score (0.0 to 1.0, higher is better)
            score = data.get("score", 0.0)
            
            # Typically, scores above 0.5 are considered legitimate
            # Adjust threshold as needed (0.5 is a common default)
            is_valid = score >= 0.5
            
            return (is_valid, score)
    except Exception as e:
        # Log error but don't expose details to client
        print(f"reCAPTCHA verification error: {e}")
        return (False, 0.0)
