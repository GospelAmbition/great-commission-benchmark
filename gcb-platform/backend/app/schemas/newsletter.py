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