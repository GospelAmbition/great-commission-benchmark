"""Contact form API endpoints"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_db
from app.core.config import settings
from app.core.recaptcha import verify_recaptcha
from app.db.models.contact_submission import ContactSubmission
from app.db.models.notification_setting import NotificationSetting, NotificationType
from app.schemas.contact import (
    ContactSubmitRequest,
    ContactSubmitResponse
)
from app.services.email import EmailService
from app.services.action_log import ActionLogService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/submit", response_model=ContactSubmitResponse)
async def submit_contact_form(
    request: ContactSubmitRequest,
    db: Session = Depends(get_db)
):
    """Submit a contact form (public endpoint with reCAPTCHA protection)"""
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
    
    # Create contact submission
    submission = ContactSubmission(
        name=request.name,
        email=request.email,
        subject=request.subject,
        message=request.message
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # Send notification email to designated recipient
    try:
        notification_setting = db.query(NotificationSetting).filter(
            NotificationSetting.notification_type == NotificationType.CONTACT
        ).first()
        
        if notification_setting and notification_setting.is_enabled and notification_setting.recipient_email:
            await EmailService.send_contact_notification_email(
                admin_email=notification_setting.recipient_email,
                contact_name=request.name,
                contact_email=request.email,
                subject=request.subject.value,
                message=request.message,
                submission_id=str(submission.id)
            )
    except Exception as e:
        # Log error but don't fail the submission
        logger.warning(f"Failed to send contact notification email: {e}")

    ActionLogService.log_action(
        db, "contact.submit", "anonymous",
        entity_type="contact_submission", entity_id=str(submission.id),
        metadata={"subject": request.subject.value}
    )
    
    return ContactSubmitResponse(
        success=True,
        message="Thank you for contacting us. We'll get back to you soon.",
        submission_id=submission.id
    )
