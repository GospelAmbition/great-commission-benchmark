#!/usr/bin/env python3
"""
Reprocess approved community submissions to create TestRun and Result records.
This fixes approved submissions that were approved before the leaderboard integration was implemented.
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.db.base import SessionLocal
from app.db.models.community_submission import CommunitySubmission
from app.db.models.test_run import TestRun
from app.db.models.model import Model
from app.db.models.question_set import QuestionSet
from app.db.models.methodology_version import MethodologyVersion
from app.db.models.question import Question
from app.db.models.result import Result


def reprocess_approved_submissions():
    """Find approved submissions without TestRuns and create them"""
    db: Session = SessionLocal()
    
    try:
        # Get all approved submissions
        approved_submissions = db.query(CommunitySubmission).filter(
            CommunitySubmission.status == "approved"
        ).all()
        
        print(f"\nFound {len(approved_submissions)} approved submission(s)")
        
        for submission in approved_submissions:
            print(f"\n{'='*60}")
            print(f"Processing: {submission.id}")
            print(f"Model: {submission.model_name}")
            
            results_package = submission.results_package
            test_run_data = results_package.get("test_run", {})
            model_id_str = test_run_data.get("model", submission.model_name)
            
            # Check if model exists
            model = db.query(Model).filter(Model.model_id == model_id_str).first()
            
            if model:
                # Check if TestRun already exists
                existing = db.query(TestRun).filter(
                    TestRun.model_id == model.id,
                    TestRun.user_id == submission.user_id,
                    TestRun.status == "completed"
                ).first()
                
                if existing:
                    print(f"  ✓ TestRun already exists: {existing.id}")
                    continue
            
            print(f"  Creating TestRun and Results...")
            
            # Get or create Model
            if not model:
                provider = "Unknown"
                if "/" in model_id_str:
                    provider = model_id_str.split("/")[0]
                model = Model(
                    model_id=model_id_str,
                    name=submission.model_name,
                    provider=provider,
                    is_active=True
                )
                db.add(model)
                db.flush()
                print(f"  Created model: {model.model_id}")
            
            # Get QuestionSet
            question_set = db.query(QuestionSet).filter(
                QuestionSet.semantic_version == submission.question_set_version
            ).first()
            if not question_set:
                question_set = db.query(QuestionSet).filter(
                    QuestionSet.status == "active"
                ).order_by(QuestionSet.created_at.desc()).first()
            
            if not question_set:
                print(f"  ✗ No question set found!")
                continue
            
            print(f"  Using question set: {question_set.semantic_version}")
            
            # Get methodology version for this question set
            methodology_version = db.query(MethodologyVersion).filter(
                MethodologyVersion.question_set_id == question_set.id
            ).first()
            if not methodology_version:
                # Create a default methodology version for this question set
                methodology_version = MethodologyVersion(
                    question_set_id=question_set.id,
                    judge_prompt="Default judge prompt",
                    scoring_config={"tier1": 0.7, "tier2": 0.2, "tier3": 0.1},
                    active_from=datetime.now(timezone.utc)
                )
                db.add(methodology_version)
                db.flush()
                print(f"  Created methodology version for question set")
            
            # Parse completed_at
            completed_at = datetime.now(timezone.utc)
            if test_run_data.get("completed_at"):
                try:
                    completed_at = datetime.fromisoformat(
                        test_run_data["completed_at"].replace("Z", "+00:00")
                    )
                except:
                    pass
            
            # Create TestRun
            test_run = TestRun(
                user_id=submission.user_id,
                model_id=model.id,
                question_set_id=question_set.id,
                methodology_version_id=methodology_version.id,
                status="completed",
                trust_tier="community",
                completed_at=completed_at,
                started_at=completed_at,
            )
            db.add(test_run)
            db.flush()
            print(f"  Created TestRun: {test_run.id}")
            
            # Create Results - build a content-to-ID mapping first
            db_questions = db.query(Question).filter(
                Question.question_set_id == question_set.id
            ).all()
            
            # Create lookup by content (stripped for matching)
            content_to_question = {}
            for q in db_questions:
                content_key = q.content.strip()
                content_to_question[content_key] = q
            
            # Also create lookup by tier+category for fallback
            tier_cat_to_questions = {}
            for q in db_questions:
                key = (q.tier, q.category)
                if key not in tier_cat_to_questions:
                    tier_cat_to_questions[key] = []
                tier_cat_to_questions[key].append(q)
            
            responses = results_package.get("responses", [])
            results_created = 0
            questions_not_found = 0
            used_question_ids = set()
            
            for response_data in responses:
                # Try to find question by ID first (in case IDs match)
                question_id_str = response_data.get("question_id")
                question = None
                
                if question_id_str:
                    try:
                        question = db.query(Question).filter(
                            Question.id == question_id_str,
                            Question.question_set_id == question_set.id
                        ).first()
                    except:
                        pass
                
                # If not found by ID, try to match by content from the original question
                # We need to get the original question content - check if it's in the response
                # For CLI submissions, we might need to use tier+category matching
                if not question:
                    tier = response_data.get("tier")
                    category = response_data.get("category")
                    
                    # Try tier+category match
                    if tier and category:
                        candidates = tier_cat_to_questions.get((tier, category), [])
                        for candidate in candidates:
                            if candidate.id not in used_question_ids:
                                question = candidate
                                break
                
                if not question:
                    questions_not_found += 1
                    continue
                
                used_question_ids.add(question.id)
                
                result = Result(
                    test_run_id=test_run.id,
                    question_id=question.id,
                    response=response_data.get("response", ""),
                    verdict=response_data.get("verdict", "UNKNOWN"),
                    reasoning=response_data.get("judge_reasoning", ""),
                )
                db.add(result)
                results_created += 1
            
            db.commit()
            print(f"  ✓ Created {results_created} results")
            if questions_not_found > 0:
                print(f"  ⚠ {questions_not_found} questions not found in database")
        
        print(f"\n{'='*60}")
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    reprocess_approved_submissions()
