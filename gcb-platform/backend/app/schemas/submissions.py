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