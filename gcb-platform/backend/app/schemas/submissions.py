"""Submissions API schemas"""
from typing import Optional, Dict, List
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class SubmissionUploadRequest(BaseModel):
    """CLI submission upload request"""
    export_data: Dict  # Full export JSON from CLI


class SubmissionUploadResponse(BaseModel):
    """Submission upload response"""
    submission_id: UUID
    status: str
    validation_errors: Optional[List[str]] = None
    message: str
    fee_waived: Optional[bool] = None  # Whether fee was waived
    payment_required: Optional[bool] = None  # Whether payment is required
    payment_intent_id: Optional[str] = None  # Stripe payment intent ID if payment required
    payment_url: Optional[str] = None  # URL to complete payment