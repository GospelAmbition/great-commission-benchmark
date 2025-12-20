#!/usr/bin/env python3
"""List all moderation logs in the database"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.models.moderation_log import ModerationLog
from app.db.models.test_run import TestRun
from app.db.models.user import User
from sqlalchemy import desc

def list_all_moderation_logs():
    """List all moderation logs"""
    db: Session = SessionLocal()
    
    try:
        # Get all moderation logs
        logs = db.query(ModerationLog).order_by(desc(ModerationLog.created_at)).all()
        
        print(f"\n{'='*80}")
        print(f"Total Moderation Logs: {len(logs)}")
        print(f"{'='*80}\n")
        
        if not logs:
            print("No moderation logs found in the database.")
            return
        
        for i, log in enumerate(logs, 1):
            test_run = db.query(TestRun).filter(TestRun.id == log.test_run_id).first()
            moderator = db.query(User).filter(User.id == log.moderator_id).first()
            
            model_name = test_run.model.name if (test_run and test_run.model) else "Unknown"
            moderator_name = moderator.name if moderator else "Unknown"
            moderator_email = moderator.email if moderator else "Unknown"
            
            print(f"Log #{i}:")
            print(f"  Review ID: {log.id}")
            print(f"  Test Run ID: {log.test_run_id}")
            print(f"  Model: {model_name}")
            print(f"  Moderator: {moderator_name} ({moderator_email})")
            print(f"  Action: {log.action}")
            print(f"  Created: {log.created_at}")
            print(f"  Sample Size: {log.sample_size}")
            print(f"  Agreements: {log.agreements}")
            print(f"  Disagreements: {log.disagreements}")
            if log.notes:
                print(f"  Notes: {log.notes[:100]}...")
            print()
        
        # Also check test runs
        test_runs = db.query(TestRun).order_by(desc(TestRun.created_at)).limit(10).all()
        print(f"\n{'='*80}")
        print(f"Recent Test Runs (showing first 10):")
        print(f"{'='*80}\n")
        
        for tr in test_runs:
            model_name = tr.model.name if tr.model else "Unknown"
            print(f"  {tr.id} - {model_name} - Status: {tr.status} - Trust Tier: {tr.trust_tier}")
            
    except Exception as e:
        print(f"Error listing moderation logs: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    list_all_moderation_logs()
