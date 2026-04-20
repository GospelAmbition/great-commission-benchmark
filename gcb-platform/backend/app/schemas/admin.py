"""Admin API schemas"""
from typing import Optional, List, Dict
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class UserListItem(BaseModel):
    """User list item"""
    id: UUID
    email: str
    name: Optional[str]
    role: str
    created_at: str
    test_count: int
    fee_waived: Optional[bool] = None
    fee_waived_reason: Optional[str] = None
    can_view_benchmark: bool = False
    can_edit_benchmark: bool = False
    can_moderate: bool = False
    can_manage_blog: bool = False
    can_admin: bool = False


class UserListResponse(BaseModel):
    """User list response"""
    users: List[UserListItem]
    total: int


class UpdateUserRoleRequest(BaseModel):
    """Update user role request"""
    role: str  # 'user', 'moderator', 'blog_manager', 'benchmark_viewer', 'benchmark_administrator', 'admin'


class UpdateUserRoleResponse(BaseModel):
    """Update user role response"""
    user_id: UUID
    role: str
    message: str


class UpdateUserPermissionsRequest(BaseModel):
    """Update user permissions request"""
    can_view_benchmark: Optional[bool] = None
    can_edit_benchmark: Optional[bool] = None
    can_moderate: Optional[bool] = None
    can_manage_blog: Optional[bool] = None
    can_admin: Optional[bool] = None


class UserPermissionsResponse(BaseModel):
    """User permissions response"""
    user_id: UUID
    can_view_benchmark: bool
    can_edit_benchmark: bool
    can_moderate: bool
    can_manage_blog: bool
    can_admin: bool
    message: str


class UpdateFeeWaiverRequest(BaseModel):
    """Update fee waiver request"""
    waived: bool
    reason: Optional[str] = None


class UpdateFeeWaiverResponse(BaseModel):
    """Update fee waiver response"""
    user_id: UUID
    fee_waived: bool
    fee_waived_reason: Optional[str] = None
    message: str


class QuestionImportRequest(BaseModel):
    """Question import request"""
    questions: List[Dict]  # Question data
    dry_run: bool = False


class QuestionImportResponse(BaseModel):
    """Question import response"""
    imported: int
    errors: List[str]
    dry_run: bool


class QuestionCreateRequest(BaseModel):
    """Question create request"""
    question_set_id: UUID
    tier: int
    category: str
    content: str
    metadata: Optional[Dict] = None  # Only 'difficulty' should be stored here
    expected_verdict: Optional[str] = None
    is_locked: Optional[bool] = False
    notes: Optional[str] = None


class QuestionUpdateRequest(BaseModel):
    """Question update request"""
    tier: Optional[int] = None
    category: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict] = None  # Only 'difficulty' should be stored here
    expected_verdict: Optional[str] = None
    is_locked: Optional[bool] = None
    notes: Optional[str] = None


class QuestionResponse(BaseModel):
    """Question response"""
    id: UUID
    question_set_id: UUID
    tier: int
    category: str
    content: str
    metadata: Optional[Dict] = None  # Only 'difficulty' should be stored here
    expected_verdict: Optional[str] = None
    is_locked: bool
    notes: Optional[str] = None


class QuestionSetCreateRequest(BaseModel):
    """Question set create request"""
    semantic_version: str = "1.0"
    marketing_version: str = "Version 1"
    notes: Optional[str] = None
    target_question_count: Optional[int] = None  # Optional target (e.g., 200 or 300)


class VersionCreateRequest(BaseModel):
    """Version create request"""
    semantic_version: str
    question_ids: List[UUID]
    description: Optional[str] = None


class VersionPublishRequest(BaseModel):
    """Version publish request"""
    version: str


class AdminStatsResponse(BaseModel):
    """Admin stats response"""
    users: Dict
    tests: Dict
    revenue: Dict
    moderation: Dict
    api_keys: Dict
    newsletter: Optional[Dict] = None


class CategoryDifficultyBreakdown(BaseModel):
    """Difficulty breakdown for a category"""
    easy: int = 0
    medium: int = 0
    hard: int = 0


class CategoryStats(BaseModel):
    """Category statistics"""
    count: int
    target: int
    difficulty: CategoryDifficultyBreakdown = CategoryDifficultyBreakdown()


class TierStats(BaseModel):
    """Tier statistics"""
    count: int
    target: int
    categories: Dict[str, CategoryStats]


class DifficultyCount(BaseModel):
    """Difficulty count for a single difficulty level"""
    count: int
    percentage: float


class DifficultyStats(BaseModel):
    """Difficulty distribution statistics"""
    easy: DifficultyCount
    medium: DifficultyCount
    hard: DifficultyCount


class QuestionSetStatsResponse(BaseModel):
    """Question set statistics response"""
    question_set_id: UUID
    semantic_version: str
    marketing_version: str
    total_questions: int
    target_total: int
    target_is_auto: bool  # True if target was auto-calculated from actual count
    tier_stats: Dict[int, TierStats]
    difficulty_stats: DifficultyStats
    category_difficulty_matrix: Dict[str, CategoryDifficultyBreakdown]  # category -> difficulty breakdown


class QuestionSetCopyRequest(BaseModel):
    """Question set copy request"""
    new_semantic_version: str
    new_marketing_version: str
    notes: Optional[str] = None


class QuestionSetUpdateTargetRequest(BaseModel):
    """Request to update question set target"""
    target_question_count: Optional[int] = None  # Set to None to use auto-calculation


class QuestionSetUpdateTargetResponse(BaseModel):
    """Response after updating question set target"""
    question_set_id: UUID
    target_question_count: Optional[int]
    message: str


# =============================================================================
# Stripe Configuration Schemas
# =============================================================================

class StripeConfigStatusResponse(BaseModel):
    """Response showing current Stripe configuration status"""
    is_configured: bool
    source: str  # 'database' or 'environment'
    is_live_mode: bool
    config_name: Optional[str] = None
    config_id: Optional[str] = None
    secret_key_masked: Optional[str] = None
    publishable_key_masked: Optional[str] = None
    webhook_secret_masked: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by_email: Optional[str] = None


class StripeConfigCreateRequest(BaseModel):
    """Request to create or update Stripe configuration"""
    secret_key: str  # Will be encrypted
    publishable_key: str
    webhook_secret: Optional[str] = None  # Will be encrypted
    name: Optional[str] = None  # Descriptive name (e.g., "Production - Ministry Name")


class StripeConfigTestRequest(BaseModel):
    """Request to test Stripe credentials"""
    secret_key: str


class StripeConfigTestResponse(BaseModel):
    """Response from testing Stripe credentials"""
    success: bool
    error: Optional[str] = None
    account_id: Optional[str] = None
    business_name: Optional[str] = None
    country: Optional[str] = None
    default_currency: Optional[str] = None
    charges_enabled: Optional[bool] = None
    payouts_enabled: Optional[bool] = None
    is_restricted_key: Optional[bool] = None
    message: Optional[str] = None
    config_source: Optional[str] = None  # "database" or "environment"


class StripeBalanceResponse(BaseModel):
    """Response showing Stripe account balance"""
    available: List[Dict]  # [{amount, currency}]
    pending: List[Dict]  # [{amount, currency}]
    livemode: bool


class StripeTransactionItem(BaseModel):
    """A single balance transaction"""
    id: str
    amount: float
    currency: str
    net: float
    fee: float
    type: str
    status: str
    description: Optional[str] = None
    created: str
    available_on: Optional[str] = None
    source: Optional[str] = None


class StripeTransactionsResponse(BaseModel):
    """Response containing list of balance transactions"""
    data: List[StripeTransactionItem]
    has_more: bool
    total_count: Optional[int] = None


class StripePaymentIntentItem(BaseModel):
    """A single payment intent"""
    id: str
    amount: float
    currency: str
    status: str
    description: Optional[str] = None
    receipt_email: Optional[str] = None
    metadata: Dict = {}
    created: str
    payment_method_types: List[str] = []


class StripePaymentIntentsResponse(BaseModel):
    """Response containing list of payment intents"""
    data: List[StripePaymentIntentItem]
    has_more: bool


class StripeChargeItem(BaseModel):
    """A single charge"""
    id: str
    amount: float
    amount_refunded: float
    currency: str
    status: str
    paid: bool
    refunded: bool
    disputed: bool
    description: Optional[str] = None
    receipt_email: Optional[str] = None
    receipt_url: Optional[str] = None
    payment_intent: Optional[str] = None
    metadata: Dict = {}
    created: str
    failure_code: Optional[str] = None
    failure_message: Optional[str] = None


class StripeChargesResponse(BaseModel):
    """Response containing list of charges"""
    data: List[StripeChargeItem]
    has_more: bool


class StripeRefundItem(BaseModel):
    """A single refund"""
    id: str
    amount: float
    currency: str
    status: str
    reason: Optional[str] = None
    payment_intent: Optional[str] = None
    charge: Optional[str] = None
    created: str
    metadata: Dict = {}


class StripeRefundsResponse(BaseModel):
    """Response containing list of refunds"""
    data: List[StripeRefundItem]
    has_more: bool


# =============================================================================
# Newsletter Admin Schemas
# =============================================================================

class NewsletterSubscriberListItem(BaseModel):
    """Newsletter subscriber list item for admin view"""
    id: UUID
    email: str
    is_active: bool
    mailerlite_subscriber_id: Optional[str] = None
    subscribed_at: Optional[datetime] = None
    unsubscribed_at: Optional[datetime] = None


class NewsletterSubscriberListResponse(BaseModel):
    """Newsletter subscriber list response"""
    items: List[NewsletterSubscriberListItem]
    total: int


class NewsletterSubscriberDetail(BaseModel):
    """Detailed newsletter subscriber view with optional MailerLite data"""
    id: UUID
    email: str
    is_active: bool
    mailerlite_subscriber_id: Optional[str] = None
    subscribed_at: Optional[datetime] = None
    unsubscribed_at: Optional[datetime] = None
    # Live MailerLite data (populated when MailerLite is configured)
    mailerlite_status: Optional[str] = None
    mailerlite_subscribed_at: Optional[str] = None
    mailerlite_opens_count: Optional[int] = None
    mailerlite_clicks_count: Optional[int] = None


class NewsletterStatsResponse(BaseModel):
    """Newsletter stats for admin dashboard"""
    total: int
    active: int
    unsubscribed: int
    synced_to_mailerlite: int
    mailerlite_configured: bool


class MailerLiteSubscriberItem(BaseModel):
    """A single subscriber from MailerLite API"""
    id: str
    email: str
    status: str
    subscribed_at: Optional[str] = None
    opens_count: Optional[int] = None
    clicks_count: Optional[int] = None


class MailerLiteSubscriberListResponse(BaseModel):
    """Response containing subscribers fetched from MailerLite"""
    items: List[MailerLiteSubscriberItem]
    next_cursor: Optional[str] = None
    has_more: bool = False


class NewsletterHtmlPreviewResponse(BaseModel):
    """Sanitized HTML for a blog post as an email-ready newsletter body."""
    subject: str
    html: str
    web_version_url: Optional[str] = None


class NewsletterSendRequest(BaseModel):
    """Send the given insights post as a MailerLite campaign to the configured group."""
    post_id: UUID
    dry_run: bool = True


class NewsletterSendResponse(BaseModel):
    """Result of a newsletter send (or dry run)."""
    dry_run: bool
    active_subscribers: int
    campaign_id: Optional[str] = None
    message: str
