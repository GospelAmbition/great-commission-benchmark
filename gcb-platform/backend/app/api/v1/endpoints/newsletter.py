"""Newsletter API endpoints"""
from datetime import datetime, timedelta, timezone
from html import escape
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.auth import get_db
from app.core.config import settings
from app.core.recaptcha import verify_recaptcha
from app.db.models.newsletter_subscriber import NewsletterSubscriber
from app.schemas.newsletter import (
    NewsletterSubscribeRequest,
    NewsletterConfirmRequest,
    NewsletterSubscribeResponse,
    NewsletterUnsubscribeRequest,
    NewsletterUnsubscribeResponse
)
from app.services.newsletter_sync import queue_sync
from app.services.action_log import ActionLogService
from app.services.newsletter_links import read_unsubscribe_token, read_resubscribe_token, resubscribe_url

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
        func.lower(func.trim(NewsletterSubscriber.email)) == request.email
    ).order_by(NewsletterSubscriber.is_active).with_for_update().first()
    
    if existing:
        if existing.is_active:
            return NewsletterSubscribeResponse(
                success=True,
                message="Email already subscribed"
            )
        if existing.resubscribe_pending:
            return NewsletterSubscribeResponse(success=True, status="sync_pending", message="Your confirmation was received. Subscription synchronization is pending.")
        now = datetime.now(timezone.utc)
        requested = existing.resubscribe_requested_at
        if requested and requested.tzinfo is None:
            requested = requested.replace(tzinfo=timezone.utc)
        if existing.resubscribe_nonce and requested and requested > now - timedelta(minutes=10):
            return NewsletterSubscribeResponse(success=True, status="confirmation_required", message="Check your email to confirm resubscription. The link is valid for 24 hours.")
        if not settings.RESEND_API_KEY:
            raise HTTPException(status_code=503, detail="Confirmation email is temporarily unavailable. Please try again later.")
        nonce = uuid4()
        subscriber_id, email = existing.id, existing.email
        try:
            link = resubscribe_url(subscriber_id, nonce)
        except ValueError as exc:
            raise HTTPException(status_code=503, detail="Confirmation email is temporarily unavailable.") from exc
        existing.resubscribe_nonce = nonce
        existing.resubscribe_requested_at = now
        db.commit()  # Release row locks before sending the confirmation email.
        from app.services.email import EmailService
        sent = await EmailService.send_email(
            to=email, subject="Confirm your GCB newsletter resubscription",
            html_content=(
                '<p>You requested to receive the Great Commission Benchmark newsletter again.</p>'
                f'<p><a href="{escape(link, quote=True)}">Confirm resubscription</a></p>'
                '<p>This link is valid for 24 hours. If you did not request this, ignore this email; '
                'your address remains unsubscribed.</p>'
            ),
        )
        if not sent:
            db.query(NewsletterSubscriber).filter(
                NewsletterSubscriber.id == subscriber_id, NewsletterSubscriber.resubscribe_nonce == nonce,
            ).update({NewsletterSubscriber.resubscribe_nonce: None, NewsletterSubscriber.resubscribe_requested_at: None}, synchronize_session=False)
            db.commit()
            raise HTTPException(status_code=503, detail="The confirmation email could not be sent. Please try again later.")
        return NewsletterSubscribeResponse(success=True, status="confirmation_required", message="Check your email to confirm resubscription. The link is valid for 24 hours.")

    # Create new subscription in database
    subscriber = NewsletterSubscriber(
        email=request.email,
        is_active=True
    )
    db.add(subscriber)
    # New rows default to pending. Sync is durable even during an API outage.
    
    from sqlalchemy.exc import IntegrityError
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        # A concurrent import/webhook/signup may have claimed this address.
        # Never treat that conflict as consent to reactivate the winning row.
        raise HTTPException(status_code=409, detail="Subscription changed while processing. Please try again.") from exc

    ActionLogService.log_action(
        db, "newsletter.subscribe", "anonymous",
        entity_type="newsletter_subscriber", entity_id=str(subscriber.id),
        metadata={}
    )

    return NewsletterSubscribeResponse(
        success=True,
        message="Successfully subscribed to newsletter"
    )


@router.post("/confirm-resubscribe", response_model=NewsletterSubscribeResponse)
async def confirm_resubscribe(request: NewsletterConfirmRequest, db: Session = Depends(get_db)):
    """Consume a purpose-bound, expiring confirmation; retain suppression until provider verification."""
    from app.db.models.action_log import ActionLog
    try:
        subscriber_id, nonce = read_resubscribe_token(request.token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="This confirmation link is invalid or expired. Request a new link from the newsletter signup page.") from exc
    sub = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.id == subscriber_id).with_for_update().first()
    if not sub or sub.resubscribe_nonce != nonce:
        raise HTTPException(status_code=400, detail="This confirmation link has already been used or cancelled. Request a new link if needed.")
    sub.resubscribe_confirmed_at = datetime.now(timezone.utc)
    queue_sync(sub, resubscribe=True)
    db.add(ActionLog(action="newsletter.resubscribe_confirmed", actor_type="anonymous",
                     entity_type="newsletter_subscriber", entity_id=str(sub.id),
                     extra_data={"source": "email_confirmation"}))
    db.commit()
    return NewsletterSubscribeResponse(success=True, status="sync_pending", message="Resubscription confirmed. Your subscription will resume after MailerLite verifies the address; delivery restrictions may still apply.")


@router.post("/unsubscribe", response_model=NewsletterUnsubscribeResponse)
async def unsubscribe_newsletter(
    request: NewsletterUnsubscribeRequest,
    db: Session = Depends(get_db)
):
    """Unsubscribe from newsletter"""
    email = request.email.lower() if request.email else None
    if request.token:
        try:
            subscriber_id = read_unsubscribe_token(request.token)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="This unsubscribe link is invalid. Enter your email address to unsubscribe.") from exc
        target = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.id == subscriber_id).first()
        if not target:
            from app.db.models.newsletter_subscriber_merge import NewsletterSubscriberMerge
            alias = db.get(NewsletterSubscriberMerge, subscriber_id)
            target = db.get(NewsletterSubscriber, alias.subscriber_id) if alias else None
        email = target.email.strip().lower() if target else None
    if email:
        subscribers = db.query(NewsletterSubscriber).filter(
            func.lower(func.trim(NewsletterSubscriber.email)) == email
        ).with_for_update().all()
        from app.db.models.action_log import ActionLog
        for subscriber in subscribers:
            if subscriber.is_active or subscriber.resubscribe_nonce or subscriber.resubscribe_pending:
                subscriber.is_active = False
                subscriber.unsubscribed_at = datetime.utcnow()
                queue_sync(subscriber)
                db.add(ActionLog(action="newsletter.unsubscribe", actor_type="anonymous",
                                 entity_type="newsletter_subscriber", entity_id=str(subscriber.id),
                                 extra_data={"source": "signed_link" if request.token else "email_form"}))
        db.commit()
    return NewsletterUnsubscribeResponse(
        success=True,
        message="If subscribed, you have been unsubscribed"
    )


@router.post("/webhooks/mailerlite")
async def mailerlite_webhook(request: Request, db: Session = Depends(get_db)):
    """Receive signed subscriber events; do no provider I/O during delivery."""
    import hashlib
    import hmac
    import json
    from sqlalchemy.exc import IntegrityError
    from app.services.newsletter_webhook import apply_webhook

    if not settings.MAILERLITE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Newsletter webhook is not configured")
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > 1_000_000:
            raise HTTPException(status_code=413, detail="Webhook payload is too large")
    signature = request.headers.get("Signature", "")
    expected = hmac.new(settings.MAILERLITE_WEBHOOK_SECRET.encode(), bytes(body), hashlib.sha256).hexdigest()
    if not signature.isascii() or not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    try:
        return apply_webhook(db, json.loads(body))
    except (ValueError, TypeError, UnicodeDecodeError) as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid webhook payload") from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Concurrent subscriber change; retry delivery") from exc
