"""Newsletter API endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_db
from app.core.config import settings
from app.core.recaptcha import verify_recaptcha
from app.db.models.newsletter_subscriber import NewsletterSubscriber
from app.schemas.newsletter import (
    NewsletterSubscribeRequest,
    NewsletterSubscribeResponse
)

router = APIRouter()


@router.post("/subscribe", response_model=NewsletterSubscribeResponse)
async def subscribe_newsletter(
    request: NewsletterSubscribeRequest,
    db: Session = Depends(get_db)
):
    """Subscribe to newsletter"""
    # Verify reCAPTCHA if enabled
    if settings.RECAPTCHA_ENABLED and settings.RECAPTCHA_SECRET_KEY:
        if not request.recaptcha_token:
            raise HTTPException(
                status_code=400,
                detail="reCAPTCHA token is required"
            )
        is_valid, score = await verify_recaptcha(request.recaptcha_token)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="reCAPTCHA verification failed. Please try again."
            )
    
    # Check if already subscribed
    existing = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.email == request.email
    ).first()
    
    if existing:
        if existing.is_active:
            return NewsletterSubscribeResponse(
                success=True,
                message="Email already subscribed"
            )
        else:
            # Reactivate
            existing.is_active = True
            db.commit()
            return NewsletterSubscribeResponse(
                success=True,
                message="Subscription reactivated"
            )
    
    # Create new subscription
    subscriber = NewsletterSubscriber(
        email=request.email,
        is_active=True
    )
    db.add(subscriber)
    db.commit()
    
    return NewsletterSubscribeResponse(
        success=True,
        message="Successfully subscribed to newsletter"
    )