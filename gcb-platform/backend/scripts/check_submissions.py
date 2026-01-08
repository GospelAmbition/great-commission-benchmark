#!/usr/bin/env python3
"""Quick script to check CLI submission status in the database"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.models.community_submission import CommunitySubmission
from app.db.models.user import User
from datetime import datetime

def check_submissions():
    """Check all community submissions and their status"""
    db: Session = SessionLocal()
    
    try:
        # Get all submissions
        all_submissions = db.query(CommunitySubmission).order_by(
            CommunitySubmission.submitted_at.desc()
        ).all()
        
        print(f"\n{'='*80}")
        print(f"Total CLI Submissions: {len(all_submissions)}")
        print(f"{'='*80}\n")
        
        if not all_submissions:
            print("No submissions found in the database.")
            return
        
        # Group by status
        by_status = {}
        for sub in all_submissions:
            status = sub.status or "unknown"
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(sub)
        
        print("Submissions by Status:")
        for status, subs in sorted(by_status.items()):
            print(f"  {status}: {len(subs)}")
        
        print(f"\n{'='*80}")
        print("Detailed Submission Information:")
        print(f"{'='*80}\n")
        
        for sub in all_submissions:
            print(f"Submission ID: {sub.id}")
            print(f"  Model: {sub.model_name}")
            print(f"  Status: {sub.status}")
            print(f"  Submitted: {sub.submitted_at}")
            
            if sub.reviewer_id:
                reviewer = db.query(User).filter(User.id == sub.reviewer_id).first()
                reviewer_name = reviewer.name if reviewer else "Unknown"
                reviewer_email = reviewer.email if reviewer else "Unknown"
                print(f"  Reviewed by: {reviewer_name} ({reviewer_email})")
                print(f"  Reviewed at: {sub.reviewed_at}")
                if sub.reviewer_notes:
                    print(f"  Reviewer notes: {sub.reviewer_notes[:100]}...")
            
            user = db.query(User).filter(User.id == sub.user_id).first()
            if user:
                print(f"  Submitted by: {user.name or user.email}")
            
            print(f"  Overall Score: {sub.overall_score}")
            print()
        
        # Specifically check for approved submissions
        approved = [s for s in all_submissions if s.status == "approved"]
        if approved:
            print(f"\n{'='*80}")
            print(f"✓ Found {len(approved)} APPROVED submission(s):")
            print(f"{'='*80}\n")
            for sub in approved:
                print(f"  ✓ {sub.id} - {sub.model_name} (Reviewed: {sub.reviewed_at})")
        else:
            print(f"\n{'='*80}")
            print("⚠ No approved submissions found")
            print(f"{'='*80}\n")
            
    except Exception as e:
        print(f"Error checking submissions: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_submissions()
