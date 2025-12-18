"""Submissions API endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_db
from app.core.auth import require_auth
from app.db.models.user import User
from app.db.models.community_submission import CommunitySubmission
from app.schemas.submissions import (
    SubmissionUploadRequest,
    SubmissionUploadResponse
)

router = APIRouter()


@router.post("", response_model=SubmissionUploadResponse)
async def upload_submission(
    request: SubmissionUploadRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Upload CLI submission export"""
    export_data = request.export_data
    
    # Validate export schema
    validation_errors = validate_export_schema(export_data)
    
    if validation_errors:
        return SubmissionUploadResponse(
            submission_id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder
            status="rejected",
            validation_errors=validation_errors,
            message="Validation failed"
        )
    
    # Extract model information
    model_info = export_data.get("model", {})
    model_name = model_info.get("name", "Unknown") if isinstance(model_info, dict) else "Unknown"
    
    # Extract version info
    version = export_data.get("version", "1.0")
    
    # Create submission record
    submission = CommunitySubmission(
        user_id=current_user.id,
        model_name=model_name,
        cli_version=export_data.get("cli_version", "1.0"),
        question_set_version=version,
        results_package=export_data,  # Store full export as JSONB
        status="pending"
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    return SubmissionUploadResponse(
        submission_id=submission.id,
        status=submission.status,
        validation_errors=None,
        message="Submission received and queued for review"
    )


def validate_export_schema(export_data: dict) -> List[str]:
    """
    Validate CLI export schema
    
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Check required top-level fields
    required_fields = ["version", "model", "questions", "results"]
    for field in required_fields:
        if field not in export_data:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return errors
    
    # Validate version consistency
    version = export_data.get("version")
    questions = export_data.get("questions", [])
    results = export_data.get("results", [])
    
    # Check question count consistency
    if len(questions) != len(results):
        errors.append(f"Question count ({len(questions)}) does not match result count ({len(results)})")
    
    # Validate each result
    for idx, result in enumerate(results):
        if "question_id" not in result:
            errors.append(f"Result {idx} missing question_id")
        if "verdict" not in result:
            errors.append(f"Result {idx} missing verdict")
        if result.get("verdict") not in ["ACCEPTED", "COMPROMISED", "REFUSED", "HEDGED", "ERROR"]:
            errors.append(f"Result {idx} has invalid verdict: {result.get('verdict')}")
    
    # Validate score calculation (simplified)
    if "scores" in export_data:
        scores = export_data["scores"]
        # TODO: Verify score calculation matches methodology
    
    return errors