"""Newsletter API schemas"""
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Literal, Optional


class NewsletterEmailRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def canonical_email(cls, value: str) -> str:
        return value.lower()


class NewsletterSubscribeRequest(NewsletterEmailRequest):
    """Newsletter subscription request"""
    recaptcha_token: Optional[str] = None
    source: Literal[
        "header", "home_hero", "home_results", "model_results", "model_archived",
        "insights_header", "article_header", "article_end", "leaderboard",
        "recent_tests", "footer", "newsletter_page",
    ] = "newsletter_page"


class NewsletterSubscribeResponse(BaseModel):
    """Newsletter subscription response"""
    success: bool
    message: str
    status: Optional[str] = None


class NewsletterConfirmRequest(BaseModel):
    token: str = Field(min_length=1, max_length=250)


class NewsletterUnsubscribeRequest(BaseModel):
    """Newsletter unsubscribe request"""
    email: Optional[EmailStr] = None
    token: Optional[str] = Field(default=None, max_length=150)

    @model_validator(mode="after")
    def require_identity(self):
        if not self.email and not self.token:
            raise ValueError("Provide an email address or unsubscribe link")
        return self


class NewsletterUnsubscribeResponse(BaseModel):
    """Newsletter unsubscribe response"""
    success: bool
    message: str
