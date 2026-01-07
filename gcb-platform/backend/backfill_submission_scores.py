#!/usr/bin/env python3
"""
Backfill scores for existing community submissions.
This fixes submissions that were created before the score extraction was implemented.
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.models.community_submission import CommunitySubmission


def backfill_submission_scores():
    """Update all submissions with scores extracted from results_package"""
    db: Session = SessionLocal()
    
    try:
        # Get all submissions
        submissions = db.query(CommunitySubmission).all()
        
        print(f"\nFound {len(submissions)} submission(s)")
        
        updated = 0
        for submission in submissions:
            results_package = submission.results_package
            if not results_package:
                print(f"  Skipping {submission.id}: no results_package")
                continue
            
            summary = results_package.get("summary", {})
            tier_scores = summary.get("tier_scores", {})
            
            # Extract scores
            overall_score = int(round(summary.get("score", 0)))
            tier1_score = int(round(tier_scores.get("tier1", {}).get("raw", 0)))
            tier2_score = int(round(tier_scores.get("tier2", {}).get("raw", 0)))
            tier3_score = int(round(tier_scores.get("tier3", {}).get("raw", 0)))
            
            # Check if update needed
            needs_update = (
                submission.overall_score != overall_score or
                submission.tier1_score != tier1_score or
                submission.tier2_score != tier2_score or
                submission.tier3_score != tier3_score
            )
            
            if needs_update:
                print(f"\n{'='*60}")
                print(f"Submission: {submission.id}")
                print(f"Model: {submission.model_name}")
                print(f"  Before: overall={submission.overall_score}, t1={submission.tier1_score}, t2={submission.tier2_score}, t3={submission.tier3_score}")
                print(f"  After:  overall={overall_score}, t1={tier1_score}, t2={tier2_score}, t3={tier3_score}")
                
                submission.overall_score = overall_score
                submission.tier1_score = tier1_score
                submission.tier2_score = tier2_score
                submission.tier3_score = tier3_score
                updated += 1
        
        db.commit()
        print(f"\n{'='*60}")
        print(f"Updated {updated} submission(s)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    backfill_submission_scores()

