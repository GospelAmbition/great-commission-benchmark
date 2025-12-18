"""Newsletter API endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_db
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