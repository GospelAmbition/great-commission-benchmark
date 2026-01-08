#!/usr/bin/env python3
"""Check moderation logs for a specific test ID"""
import sys
import os
from uuid import UUID

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.models.moderation_log import ModerationLog
from app.db.models.test_run import TestRun
from app.db.models.user import User

def check_moderation_log(test_id_str: str):
    """Check moderation logs for a specific test ID"""
    db: Session = SessionLocal()
    
    try:
        test_id = UUID(test_id_str)
        
        # Check if test run exists
        test_run = db.query(TestRun).filter(TestRun.id == test_id).first()
        
        if not test_run:
            print(f"\n❌ Test run {test_id_str} not found in database")
            return
        
        print(f"\n{'='*80}")
        print(f"Test Run: {test_id_str}")
        print(f"Model: {test_run.model.name if test_run.model else 'Unknown'}")
        print(f"Status: {test_run.status}")
        print(f"Trust Tier: {test_run.trust_tier}")
        print(f"{'='*80}\n")
        
        # Get all moderation logs for this test
        logs = db.query(ModerationLog).filter(
            ModerationLog.test_run_id == test_id
        ).order_by(ModerationLog.created_at.desc()).all()
        
        if not logs:
            print("⚠ No moderation logs found for this test run")
            print("\nThis means the test has not been reviewed yet.")
            return
        
        print(f"Found {len(logs)} moderation log(s):\n")
        
        for i, log in enumerate(logs, 1):
            moderator = db.query(User).filter(User.id == log.moderator_id).first()
            moderator_name = moderator.name if moderator else "Unknown"
            moderator_email = moderator.email if moderator else "Unknown"
            
            print(f"Log #{i}:")
            print(f"  Review ID: {log.id}")
            print(f"  Moderator: {moderator_name} ({moderator_email})")
            print(f"  Action: {log.action}")
            print(f"  Created: {log.created_at}")
            print(f"  Sample Size: {log.sample_size}")
            print(f"  Agreements: {log.agreements}")
            print(f"  Disagreements: {log.disagreements}")
            if log.notes:
                print(f"  Notes: {log.notes[:200]}...")
            print()
        
        print(f"{'='*80}")
        print("✓ Moderation logs found - these should appear in the moderation history")
        print(f"{'='*80}\n")
            
    except ValueError as e:
        print(f"❌ Invalid UUID format: {test_id_str}")
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error checking moderation log: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_moderation_log.py <test_id>")
        print("Example: python check_moderation_log.py 90fcbb3f-45db-4a83-88bd-ccff9802e54c")
        sys.exit(1)
    
    check_moderation_log(sys.argv[1])
