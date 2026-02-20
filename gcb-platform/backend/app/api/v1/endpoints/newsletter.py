"""Newsletter API endpoints"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_db
from app.core.config import settings
from app.core.recaptcha import verify_recaptcha
from app.db.models.newsletter_subscriber import NewsletterSubscriber
from app.schemas.newsletter import (
    NewsletterSubscribeRequest,
    NewsletterSubscribeResponse,
    NewsletterUnsubscribeRequest,
    NewsletterUnsubscribeResponse
)
from app.services.newsletter import NewsletterService
from app.services.action_log import ActionLogService

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
            # Reactivate in database
            existing.is_active = True
            existing.unsubscribed_at = None
            
            # Sync with MailerLite (reactivate)
            mailerlite_id = await NewsletterService.reactivate_subscriber(request.email)
            if mailerlite_id:
                existing.mailerlite_subscriber_id = mailerlite_id
            
            db.commit()
            ActionLogService.log_action(
                db, "newsletter.subscribe", "anonymous",
                entity_type="newsletter_subscriber", entity_id=str(existing.id),
                metadata={"action": "reactivate"}
            )
            return NewsletterSubscribeResponse(
                success=True,
                message="Subscription reactivated"
            )
    
    # Create new subscription in database
    subscriber = NewsletterSubscriber(
        email=request.email,
        is_active=True
    )
    db.add(subscriber)
    db.flush()  # Get the ID before syncing
    
    # Sync with MailerLite
    mailerlite_id = await NewsletterService.sync_subscriber_to_mailerlite(request.email)
    if mailerlite_id:
        subscriber.mailerlite_subscriber_id = mailerlite_id
    
    db.commit()

    ActionLogService.log_action(
        db, "newsletter.subscribe", "anonymous",
        entity_type="newsletter_subscriber", entity_id=str(subscriber.id),
        metadata={}
    )

    return NewsletterSubscribeResponse(
        success=True,
        message="Successfully subscribed to newsletter"
    )


@router.post("/unsubscribe", response_model=NewsletterUnsubscribeResponse)
async def unsubscribe_newsletter(
    request: NewsletterUnsubscribeRequest,
    db: Session = Depends(get_db)
):
    """Unsubscribe from newsletter"""
    # Find subscriber
    subscriber = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.email == request.email
    ).first()
    
    if not subscriber:
        # Don't reveal if email exists or not for privacy
        return NewsletterUnsubscribeResponse(
            success=True,
            message="If subscribed, you have been unsubscribed"
        )
    
    if not subscriber.is_active:
        return NewsletterUnsubscribeResponse(
            success=True,
            message="Already unsubscribed"
        )
    
    # Update database
    subscriber.is_active = False
    subscriber.unsubscribed_at = datetime.utcnow()
    
    # Sync with MailerLite
    await NewsletterService.remove_subscriber_from_mailerlite(request.email)
    
    db.commit()

    ActionLogService.log_action(
        db, "newsletter.unsubscribe", "anonymous",
        entity_type="newsletter_subscriber", entity_id=str(subscriber.id),
        metadata={}
    )
    
    return NewsletterUnsubscribeResponse(
        success=True,
        message="Successfully unsubscribed from newsletter"
    )