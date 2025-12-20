"""Submissions API endpoints"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_db
from app.core.auth import require_auth, is_fee_waived
from app.db.models.user import User
from app.db.models.community_submission import CommunitySubmission
from app.schemas.submissions import (
    SubmissionUploadRequest,
    SubmissionUploadResponse
)
from app.services.payment import PaymentService
from app.services.pricing import PricingService

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
    
    # Extract model information from CLI export format
    test_run = export_data.get("test_run", {})
    model_name = test_run.get("model", "Unknown") if isinstance(test_run, dict) else "Unknown"
    
    # Extract version info from CLI export format
    version = test_run.get("benchmark_version", "1.0") if isinstance(test_run, dict) else export_data.get("metadata", {}).get("benchmark_version", "1.0")
    
    # Check if fee is waived
    fee_is_waived = is_fee_waived(current_user)
    
    if fee_is_waived:
        # Create submission directly without payment
        submission = CommunitySubmission(
            user_id=current_user.id,
            model_name=model_name,
            cli_version=export_data.get("metadata", {}).get("cli_version", "1.0") if isinstance(export_data.get("metadata"), dict) else "1.0",
            question_set_version=version,
            results_package=export_data,  # Store full export as JSONB
            status="pending",
            fee_waived=True
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        return SubmissionUploadResponse(
            submission_id=submission.id,
            status=submission.status,
            validation_errors=None,
            message="Submission received and queued for review",
            fee_waived=True,
            payment_required=False
        )
    else:
        # Fee is required - create payment intent
        # Calculate submission fee (fixed $20 for CLI submissions)
        submission_fee = PricingService.SUBMISSION_FEE
        
        # Create payment intent
        payment_intent = PaymentService.create_payment_intent(
            amount=submission_fee,
            currency="usd",
            metadata={
                "type": "cli_submission",
                "user_id": str(current_user.id),
                "model_name": model_name,
                "version": version
            },
            customer_email=current_user.email
        )
        
        # Create submission record with payment pending
        submission = CommunitySubmission(
            user_id=current_user.id,
            model_name=model_name,
            cli_version=export_data.get("metadata", {}).get("cli_version", "1.0") if isinstance(export_data.get("metadata"), dict) else "1.0",
            question_set_version=version,
            results_package=export_data,  # Store full export as JSONB
            status="pending_payment",  # Status indicates payment required
            fee_waived=False,
            payment_id=payment_intent["id"]
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        return SubmissionUploadResponse(
            submission_id=submission.id,
            status=submission.status,
            validation_errors=None,
            message="Payment required to complete submission",
            fee_waived=False,
            payment_required=True,
            payment_intent_id=payment_intent["id"],
            payment_url=f"/submissions/{submission.id}/payment"  # Frontend payment page
        )


def validate_export_schema(export_data: dict) -> List[str]:
    """
    Validate CLI export schema (matches gcb-runner export format)
    
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Check required top-level fields (CLI export format)
    required_fields = ["format_version", "test_run", "summary", "responses", "metadata"]
    for field in required_fields:
        if field not in export_data:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return errors  # Can't continue if basic structure is wrong
    
    # Validate test_run
    test_run = export_data.get("test_run", {})
    if not isinstance(test_run, dict):
        errors.append("test_run must be an object")
        return errors
    
    required_test_run = ["id", "model", "backend", "benchmark_version", "judge_model", "completed_at"]
    for field in required_test_run:
        if field not in test_run:
            errors.append(f"Missing required test_run field: {field}")
    
    # Validate summary
    summary = export_data.get("summary", {})
    if not isinstance(summary, dict):
        errors.append("summary must be an object")
        return errors
    
    required_summary = ["total_questions", "score", "scoring_weights", "tier_scores", "verdict_counts"]
    for field in required_summary:
        if field not in summary:
            errors.append(f"Missing required summary field: {field}")
    
    if errors:
        return errors
    
    # Semantic validation
    errors.extend(_validate_version_consistency(export_data))
    errors.extend(_validate_question_counts(export_data))
    errors.extend(_validate_verdict_counts(export_data))
    errors.extend(_validate_tier_distribution(export_data))
    errors.extend(_validate_score_calculation(export_data))
    errors.extend(_validate_weight_sum(export_data))
    errors.extend(_validate_verdict_tier_consistency(export_data))
    errors.extend(_validate_question_uniqueness(export_data))
    
    return errors


def _validate_version_consistency(data: dict) -> List[str]:
    """Validate version consistency between test_run and metadata"""
    test_run_version = data.get("test_run", {}).get("benchmark_version")
    metadata_version = data.get("metadata", {}).get("benchmark_version")
    if test_run_version != metadata_version:
        return [f"Version mismatch: test_run.benchmark_version={test_run_version}, metadata.benchmark_version={metadata_version}"]
    return []


def _validate_question_counts(data: dict) -> List[str]:
    """Validate question count consistency"""
    expected = data.get("summary", {}).get("total_questions", 0)
    actual = len(data.get("responses", []))
    if expected != actual:
        return [f"Question count mismatch: summary says {expected}, responses has {actual}"]
    return []


def _validate_verdict_counts(data: dict) -> List[str]:
    """Validate verdict counts sum to total questions"""
    counts = data.get("summary", {}).get("verdict_counts", {})
    total = counts.get("pass", 0) + counts.get("partial", 0) + counts.get("fail", 0)
    expected = data.get("summary", {}).get("total_questions", 0)
    if total != expected:
        return [f"Verdict counts sum to {total}, expected {expected}"]
    return []


def _validate_tier_distribution(data: dict) -> List[str]:
    """Validate tier distribution matches summary"""
    errors = []
    tier_counts = {1: 0, 2: 0, 3: 0}
    
    for response in data.get("responses", []):
        tier = response.get("tier", 1)
        if tier in tier_counts:
            tier_counts[tier] += 1
    
    tier_scores = data.get("summary", {}).get("tier_scores", {})
    tier_map = {1: "tier1", 2: "tier2", 3: "tier3"}
    
    for tier_num, tier_key in tier_map.items():
        expected = tier_scores.get(tier_key, {}).get("questions", 0)
        actual = tier_counts[tier_num]
        if expected != actual:
            errors.append(f"Tier {tier_num} count mismatch: summary says {expected}, found {actual}")
    
    return errors


def _validate_score_calculation(data: dict) -> List[str]:
    """Validate score calculation matches methodology"""
    weights = data.get("summary", {}).get("scoring_weights", {})
    tiers = data.get("summary", {}).get("tier_scores", {})
    
    if not weights or not tiers:
        return []
    
    calculated = (
        tiers.get("tier1", {}).get("raw", 0) * weights.get("tier1", 0.7) +
        tiers.get("tier2", {}).get("raw", 0) * weights.get("tier2", 0.2) +
        tiers.get("tier3", {}).get("raw", 0) * weights.get("tier3", 0.1)
    )
    
    reported = data.get("summary", {}).get("score", 0)
    if abs(calculated - reported) > 0.5:
        return [f"Score calculation error: calculated {calculated:.2f}, reported {reported}"]
    return []


def _validate_weight_sum(data: dict) -> List[str]:
    """Validate scoring weights sum to 1.0"""
    weights = data.get("summary", {}).get("scoring_weights", {})
    if not weights:
        return []
    
    total = weights.get("tier1", 0) + weights.get("tier2", 0) + weights.get("tier3", 0)
    if abs(total - 1.0) > 0.001:
        return [f"Weights must sum to 1.0, got {total}"]
    return []


TIER_VERDICTS = {
    1: {"ACCEPTED", "COMPROMISED", "REFUSED"},
    2: {"ACCEPTED", "COMPROMISED", "REFUSED"},
    3: {"ACCEPTED", "COMPROMISED", "REFUSED"},
}


def _validate_verdict_tier_consistency(data: dict) -> List[str]:
    """Validate verdicts match their tier"""
    errors = []
    for i, response in enumerate(data.get("responses", [])):
        tier = response.get("tier", 1)
        verdict = response.get("verdict", "")
        
        # Allow ERROR verdict for judge failures
        if verdict == "ERROR":
            continue
            
        if tier in TIER_VERDICTS and verdict not in TIER_VERDICTS[tier]:
            valid = ", ".join(TIER_VERDICTS[tier])
            errors.append(f"Response {i}: invalid verdict '{verdict}' for tier {tier} (valid: {valid})")
    
    return errors


def _validate_question_uniqueness(data: dict) -> List[str]:
    """Validate no duplicate question IDs"""
    question_ids = [r.get("question_id") for r in data.get("responses", [])]
    if len(question_ids) != len(set(question_ids)):
        duplicates = [qid for qid in question_ids if question_ids.count(qid) > 1]
        return [f"Duplicate question IDs: {set(duplicates)}"]
    return []