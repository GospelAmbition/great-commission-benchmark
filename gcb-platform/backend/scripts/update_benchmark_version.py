#!/usr/bin/env python3
"""
Update the active benchmark version to 1.0.0.

This script updates the semantic_version of the currently active QuestionSet
to "1.0.0". After running this script, you may need to:
1. Restart the backend server to clear the cache, OR
2. Wait for the cache to expire (1 hour for public_stats)
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.models.question_set import QuestionSet


def update_benchmark_version():
    """Update the active QuestionSet version to 1.0.0"""
    db: Session = SessionLocal()
    
    try:
        # Find the active question set
        active_qs = db.query(QuestionSet).filter(
            QuestionSet.status == "active"
        ).first()
        
        if not active_qs:
            print("ERROR: No active QuestionSet found in the database.")
            print("Please ensure there is an active version before running this script.")
            return 1
        
        old_version = active_qs.semantic_version
        print(f"\nCurrent active version: {old_version}")
        print(f"Question Set ID: {active_qs.id}")
        print(f"Marketing Version: {active_qs.marketing_version}")
        
        if old_version == "1.0.0":
            print("\nVersion is already 1.0.0. No update needed.")
            return 0
        
        # Check if version 1.0.0 already exists
        existing_1_0 = db.query(QuestionSet).filter(
            QuestionSet.semantic_version == "1.0.0"
        ).first()
        
        if existing_1_0 and existing_1_0.id != active_qs.id:
            print(f"\nWARNING: A QuestionSet with version 1.0.0 already exists:")
            print(f"  ID: {existing_1_0.id}")
            print(f"  Status: {existing_1_0.status}")
            print(f"\nThis script will update the active version ({old_version}) to 1.0.0.")
            print("This may cause a version conflict. Continue? (y/n): ", end="")
            response = input().strip().lower()
            if response != 'y':
                print("Aborted.")
                return 1
        
        # Update the version
        active_qs.semantic_version = "1.0.0"
        db.commit()
        
        print(f"\n✓ Successfully updated version from {old_version} to 1.0.0")
        print(f"\nNOTE: The cache may still show the old version for up to 1 hour.")
        print("To see the change immediately, restart the backend server.")
        
        return 0
        
    except Exception as e:
        db.rollback()
        print(f"\nERROR: Failed to update version: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    exit_code = update_benchmark_version()
    sys.exit(exit_code)
