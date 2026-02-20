"""Database models"""
# Import all models so Alembic can detect them
from app.db.models.user import User
from app.db.models.user_api_key import UserAPIKey
from app.db.models.model import Model
from app.db.models.question_set import QuestionSet
from app.db.models.question import Question
from app.db.models.methodology_version import MethodologyVersion
from app.db.models.test_run import TestRun
from app.db.models.result import Result
from app.db.models.moderation_log import ModerationLog
from app.db.models.sponsorship_request import SponsorshipRequest
from app.db.models.newsletter_subscriber import NewsletterSubscriber
from app.db.models.community_submission import CommunitySubmission
from app.db.models.notification_preference import NotificationPreference
from app.db.models.blog_category import BlogCategory
from app.db.models.blog_post import BlogPost
from app.db.models.model_version_stats import ModelVersionStats
from app.db.models.stripe_config import StripeConfig
from app.db.models.volunteer_application import VolunteerApplication
from app.db.models.contact_submission import ContactSubmission
from app.db.models.notification_setting import NotificationSetting
from app.db.models.action_log import ActionLog

__all__ = [
    "User",
    "UserAPIKey",
    "Model",
    "QuestionSet",
    "Question",
    "MethodologyVersion",
    "TestRun",
    "Result",
    "ModerationLog",
    "SponsorshipRequest",
    "NewsletterSubscriber",
    "CommunitySubmission",
    "NotificationPreference",
    "BlogCategory",
    "BlogPost",
    "ModelVersionStats",
    "StripeConfig",
    "VolunteerApplication",
    "ContactSubmission",
    "NotificationSetting",
    "ActionLog",
]
