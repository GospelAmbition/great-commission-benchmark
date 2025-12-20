"""Tests API endpoints"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_db
from app.core.auth import require_auth, is_fee_waived
from app.db.models.user import User
from app.db.models.test_run import TestRun
from app.db.models.model import Model
from app.db.models.question_set import QuestionSet
from app.db.models.result import Result
from app.services.executor import BenchmarkExecutor
from app.services.openrouter import OpenRouterClient
from app.services.scoring import ScoringService
from app.schemas.tests import (
    CreateTestRequest,
    CreateTestResponse,
    TestProgressResponse,
    CancelTestResponse,
    RetestRequest,
    RetestResponse,
    RetestHistoryItem,
    RetestHistoryResponse,
    ScoreComparison,
    CategoryComparison,
    TestComparisonResponse
)

router = APIRouter()


@router.post("", response_model=CreateTestResponse)
async def create_test(
    request: CreateTestRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a new test run"""
    from app.db.models.methodology_version import MethodologyVersion
    from app.db.models.question import Question
    from app.services.pricing import PricingService
    
    # Look up model by OpenRouter model ID (string), or create if doesn't exist
    model = db.query(Model).filter(Model.model_id == request.model_id).first()
    if not model:
        # Create the model entry - extract provider and name from model_id
        provider = request.model_id.split("/")[0] if "/" in request.model_id else "unknown"
        model_name = request.model_id.split("/")[-1] if "/" in request.model_id else request.model_id
        
        model = Model(
            model_id=request.model_id,
            name=model_name,
            provider=provider,
            is_active=True
        )
        db.add(model)
        db.commit()
        db.refresh(model)
    
    # Get question set - by version if specified, otherwise by question_set_id or default to active
    if request.version:
        # Look up by semantic version through MethodologyVersion
        methodology_version = db.query(MethodologyVersion).filter(
            MethodologyVersion.semantic_version == request.version
        ).first()
        if not methodology_version:
            raise HTTPException(status_code=404, detail=f"Version {request.version} not found")
        question_set = db.query(QuestionSet).filter(
            QuestionSet.id == methodology_version.question_set_id
        ).first()
    elif request.question_set_id:
        question_set = db.query(QuestionSet).filter(QuestionSet.id == request.question_set_id).first()
        methodology_version = db.query(MethodologyVersion).filter(
            MethodologyVersion.question_set_id == question_set.id
        ).order_by(MethodologyVersion.active_from.desc()).first() if question_set else None
    else:
        question_set = db.query(QuestionSet).filter(QuestionSet.status == "active").first()
        methodology_version = db.query(MethodologyVersion).filter(
            MethodologyVersion.question_set_id == question_set.id
        ).order_by(MethodologyVersion.active_from.desc()).first() if question_set else None
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    if not methodology_version:
        raise HTTPException(status_code=404, detail="Methodology version not found")
    
    # Calculate cost using pricing service
    question_count = db.query(Question).filter(
        Question.question_set_id == question_set.id
    ).count()
    
    pricing_breakdown = await PricingService.calculate_test_cost(
        model.model_id,
        question_count
    )
    cost_estimate = float(pricing_breakdown["total"])
    
    # Check if fee is waived for this user
    fee_waived = is_fee_waived(current_user)
    
    # Create test run
    # Note: status is "pending_payment" for all tests, but fee-waived users have
    # payment_status="succeeded" so they can start the test immediately
    test_run = TestRun(
        user_id=current_user.id,
        model_id=model.id,  # Use database UUID, not OpenRouter model ID
        question_set_id=question_set.id,
        methodology_version_id=methodology_version.id,
        status="pending_payment",
        total_cost=0.0 if fee_waived else cost_estimate,
        payment_status="succeeded" if fee_waived else None
    )
    db.add(test_run)
    db.commit()
    db.refresh(test_run)
    
    # Payment intent will be created via /api/payments/create-intent endpoint
    payment_intent_id = None
    
    return CreateTestResponse(
        test_id=test_run.id,
        cost_estimate=0.0 if fee_waived else cost_estimate,
        payment_intent_id=payment_intent_id,
        status=test_run.status,
        fee_waived=fee_waived
    )


@router.post("/{test_id}/start", response_model=dict)
async def start_test(
    test_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Start a test run"""
    test_run = db.query(TestRun).filter(
        TestRun.id == test_id,
        TestRun.user_id == current_user.id
    ).first()
    
    if not test_run:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if test_run.status != "pending_payment":
        raise HTTPException(status_code=400, detail=f"Test cannot be started. Current status: {test_run.status}")
    
    # Verify payment completed
    if test_run.payment_status != "succeeded":
        raise HTTPException(
            status_code=402,
            detail="Payment required. Please complete payment before starting the test."
        )
    
    # Update status
    from datetime import datetime
    test_run.status = "running"
    test_run.started_at = datetime.utcnow()
    db.commit()
    
    # Start execution in background
    openrouter_client = OpenRouterClient()
    executor = BenchmarkExecutor(db, openrouter_client)
    
    async def run_test():
        try:
            await executor.execute(str(test_id))
        except Exception as e:
            # Update test run with error
            test_run = db.query(TestRun).filter(TestRun.id == test_id).first()
            if test_run:
                test_run.status = "failed"
                test_run.last_error = str(e)
                db.commit()
        finally:
            await openrouter_client.close()
    
    background_tasks.add_task(run_test)
    
    return {
        "test_id": str(test_run.id),
        "status": test_run.status,
        "started_at": test_run.started_at.isoformat() if test_run.started_at else None
    }


@router.get("/{test_id}/progress", response_model=TestProgressResponse)
async def get_test_progress(
    test_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get test run progress"""
    test_run = db.query(TestRun).filter(
        TestRun.id == test_id,
        TestRun.user_id == current_user.id
    ).first()
    
    if not test_run:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Count completed questions
    from app.db.models.result import Result
    completed = db.query(Result).filter(Result.test_run_id == test_id).count()
    
    # Get total questions
    from app.db.models.question import Question
    total = db.query(Question).filter(Question.question_set_id == test_run.question_set_id).count()
    
    # Get current question info
    current_tier = None
    current_category = None
    if test_run.checkpoint_question_index:
        questions = db.query(Question).filter(
            Question.question_set_id == test_run.question_set_id
        ).order_by(Question.tier, Question.category).all()
        
        if test_run.checkpoint_question_index < len(questions):
            current_q = questions[test_run.checkpoint_question_index]
            current_tier = current_q.tier
            current_category = current_q.category
    
    # Estimate completion time (simplified)
    estimated_completion = None
    if test_run.started_at and completed > 0:
        from datetime import datetime, timedelta
        elapsed = datetime.utcnow() - test_run.started_at
        rate = completed / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
        if rate > 0:
            remaining = total - completed
            estimated_seconds = remaining / rate
            estimated_completion = datetime.utcnow() + timedelta(seconds=estimated_seconds)
    
    return TestProgressResponse(
        test_id=test_run.id,
        status=test_run.status,
        progress={
            "completed": completed,
            "total": total,
            "percentage": int((completed / total) * 100) if total > 0 else 0
        },
        current_tier=current_tier,
        current_category=current_category,
        estimated_completion=estimated_completion,
        started_at=test_run.started_at
    )


@router.post("/{test_id}/cancel", response_model=CancelTestResponse)
async def cancel_test(
    test_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Cancel a test run"""
    test_run = db.query(TestRun).filter(
        TestRun.id == test_id,
        TestRun.user_id == current_user.id
    ).first()
    
    if not test_run:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if test_run.status in ["completed", "cancelled", "failed"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel test with status: {test_run.status}")
    
    # Update status
    test_run.status = "cancelled"
    db.commit()
    
    # Determine refund eligibility
    refund_eligible = test_run.status == "pending_payment" or (
        test_run.status == "running" and test_run.checkpoint_question_index == 0
    )
    
    refund_amount = None
    if refund_eligible:
        refund_amount = float(test_run.total_cost or 0)
    
    return CancelTestResponse(
        test_id=test_run.id,
        status=test_run.status,
        refund_eligible=refund_eligible,
        refund_amount=refund_amount
    )


@router.post("/{test_id}/retest", response_model=RetestResponse)
async def retest(
    test_id: UUID,
    request: RetestRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a retest of a completed test"""
    original_test = db.query(TestRun).filter(
        TestRun.id == test_id,
        TestRun.user_id == current_user.id
    ).first()
    
    if not original_test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if original_test.status != "completed":
        raise HTTPException(status_code=400, detail="Can only retest completed tests")
    
    # Check if fee is waived for this user
    fee_waived = is_fee_waived(current_user)
    
    # Create new test run with same parameters
    new_test = TestRun(
        user_id=current_user.id,
        model_id=original_test.model_id,
        question_set_id=original_test.question_set_id,
        methodology_version_id=original_test.methodology_version_id,
        status="pending_payment",
        total_cost=0.0 if fee_waived else original_test.total_cost,
        payment_status="succeeded" if fee_waived else None
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    
    return RetestResponse(
        new_test_id=new_test.id,
        original_test_id=original_test.id,
        cost_estimate=0.0 if fee_waived else float(new_test.total_cost or 0),
        fee_waived=fee_waived
    )


@router.get("/{test_id}/retest/history", response_model=RetestHistoryResponse)
async def get_retest_history(
    test_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Get retest history for a test.
    Returns all tests for the same model and question set version.
    """
    # Get the original test
    original_test = db.query(TestRun).filter(
        TestRun.id == test_id,
        TestRun.user_id == current_user.id
    ).first()
    
    if not original_test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Get all tests for this model and question set by this user
    related_tests = db.query(TestRun).filter(
        TestRun.user_id == current_user.id,
        TestRun.model_id == original_test.model_id,
        TestRun.question_set_id == original_test.question_set_id,
        TestRun.status == "completed"
    ).order_by(TestRun.completed_at.desc()).all()
    
    # Build history items
    history_items = []
    for test in related_tests:
        scores = None
        try:
            scores = ScoringService.calculate_scores(db, str(test.id))
        except:
            pass
        
        history_items.append(RetestHistoryItem(
            test_id=test.id,
            completed_at=test.completed_at,
            overall_score=scores["overall"] if scores else None,
            tier1_score=scores["tier1"] if scores else None,
            tier2_score=scores["tier2"] if scores else None,
            tier3_score=scores["tier3"] if scores else None,
            trust_tier=test.trust_tier or "automated",
            benchmark_version=test.question_set.semantic_version
        ))
    
    return RetestHistoryResponse(
        model_id=original_test.model_id,
        model_name=original_test.model.name,
        tests=history_items,
        total_tests=len(history_items)
    )


@router.get("/{test_id}/compare", response_model=TestComparisonResponse)
async def compare_tests(
    test_id: UUID,
    compare_to: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Compare two test runs.
    Returns detailed comparison of scores, categories, and verdicts.
    """
    # Get both tests
    test1 = db.query(TestRun).filter(
        TestRun.id == test_id,
        TestRun.user_id == current_user.id
    ).first()
    
    test2 = db.query(TestRun).filter(
        TestRun.id == compare_to,
        TestRun.user_id == current_user.id
    ).first()
    
    if not test1 or not test2:
        raise HTTPException(status_code=404, detail="One or both tests not found")
    
    if test1.status != "completed" or test2.status != "completed":
        raise HTTPException(status_code=400, detail="Can only compare completed tests")
    
    # Calculate scores for both tests
    try:
        scores1 = ScoringService.calculate_scores(db, str(test1.id))
        scores2 = ScoringService.calculate_scores(db, str(test2.id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate scores: {str(e)}")
    
    # Calculate score deltas
    score_delta = ScoreComparison(
        overall=round(scores2["overall"] - scores1["overall"], 2),
        tier1=round(scores2["tier1"] - scores1["tier1"], 2),
        tier2=round(scores2["tier2"] - scores1["tier2"], 2),
        tier3=round(scores2["tier3"] - scores1["tier3"], 2)
    )
    
    # Compare categories
    category_comparison = []
    all_categories = set(scores1.get("category_scores", {}).keys()) | set(scores2.get("category_scores", {}).keys())
    
    improved_categories = []
    declined_categories = []
    
    for category in sorted(all_categories):
        score1 = scores1.get("category_scores", {}).get(category, 0)
        score2 = scores2.get("category_scores", {}).get(category, 0)
        delta = round(score2 - score1, 2)
        
        category_comparison.append(CategoryComparison(
            category=category,
            test1_score=score1,
            test2_score=score2,
            delta=delta
        ))
        
        if delta > 5:  # Significant improvement threshold
            improved_categories.append(category)
        elif delta < -5:  # Significant decline threshold
            declined_categories.append(category)
    
    # Compare verdict distributions
    verdict_comparison = {
        "test1": scores1.get("verdict_distribution", {}),
        "test2": scores2.get("verdict_distribution", {}),
        "delta": {}
    }
    
    all_verdicts = ["ACCEPTED", "COMPROMISED", "REFUSED", "ERROR"]
    for verdict in all_verdicts:
        v1 = scores1.get("verdict_distribution", {}).get(verdict, 0)
        v2 = scores2.get("verdict_distribution", {}).get(verdict, 0)
        verdict_comparison["delta"][verdict] = v2 - v1
    
    return TestComparisonResponse(
        test1={
            "test_id": str(test1.id),
            "model_name": test1.model.name,
            "completed_at": test1.completed_at.isoformat() if test1.completed_at else None,
            "scores": {
                "overall": scores1["overall"],
                "tier1": scores1["tier1"],
                "tier2": scores1["tier2"],
                "tier3": scores1["tier3"]
            }
        },
        test2={
            "test_id": str(test2.id),
            "model_name": test2.model.name,
            "completed_at": test2.completed_at.isoformat() if test2.completed_at else None,
            "scores": {
                "overall": scores2["overall"],
                "tier1": scores2["tier1"],
                "tier2": scores2["tier2"],
                "tier3": scores2["tier3"]
            }
        },
        score_delta=score_delta,
        category_comparison=category_comparison,
        verdict_comparison=verdict_comparison,
        improved_categories=improved_categories,
        declined_categories=declined_categories
    )