"""Newsletter API schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class NewsletterSubscribeRequest(BaseModel):
    """Newsletter subscription request"""
    email: EmailStr
    recaptcha_token: Optional[str] = None


class NewsletterSubscribeResponse(BaseModel):
    """Newsletter subscription response"""
    success: bool
    message: str


class NewsletterUnsubscribeRequest(BaseModel):
    """Newsletter unsubscribe request"""
    email: EmailStr
    token: Optional[str] = None  # Optional verification token


class NewsletterUnsubscribeResponse(BaseModel):
    """Newsletter unsubscribe response"""
    success: bool
    message: str