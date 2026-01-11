#!/usr/bin/env python3
"""
Backfill model_version_stats table from existing test_runs data.

This script populates the model_version_stats table with pre-computed aggregates
for all model-version pairs that have completed tests. Run this after deploying
the 017_add_model_version_stats migration.

Usage:
    python scripts/backfill_model_version_stats.py [--dry-run]

Options:
    --dry-run    Show what would be done without making changes
"""
import sys
import os
import argparse

# Add the backend directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.services.aggregation import AggregationService


def backfill_model_version_stats(dry_run: bool = False):
    """Populate model_version_stats from existing test_runs data."""
    db: Session = SessionLocal()
    
    try:
        print("\n" + "=" * 60)
        print("Backfilling model_version_stats table")
        print("=" * 60)
        
        if dry_run:
            print("\n** DRY RUN MODE - No changes will be made **\n")
        
        # Find all unique model-version pairs with completed tests
        from app.db.models.test_run import TestRun
        from sqlalchemy import distinct
        
        pairs = db.query(
            distinct(TestRun.model_id),
            TestRun.question_set_id
        ).filter(
            TestRun.status == "completed"
        ).all()
        
        print(f"Found {len(pairs)} unique model-version pairs with completed tests\n")
        
        if dry_run:
            # In dry-run mode, just show what would be processed
            from app.db.models.model import Model
            from app.db.models.question_set import QuestionSet
            
            for model_id, question_set_id in pairs:
                model = db.query(Model).filter(Model.id == model_id).first()
                question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
                
                # Count tests for this pair
                test_count = db.query(TestRun).filter(
                    TestRun.model_id == model_id,
                    TestRun.question_set_id == question_set_id,
                    TestRun.status == "completed"
                ).count()
                
                model_name = model.name if model else "Unknown"
                version = question_set.semantic_version if question_set else "Unknown"
                
                print(f"  Would process: {model_name} (v{version}) - {test_count} test(s)")
            
            print(f"\nDry run complete. {len(pairs)} stats entries would be created/updated.")
            return
        
        # Actually run the backfill
        success_count, error_count = AggregationService.backfill_all_stats(db)
        
        print("\n" + "=" * 60)
        print(f"Backfill complete!")
        print(f"  Success: {success_count}")
        print(f"  Errors:  {error_count}")
        print("=" * 60)
        
        # Show summary of what was created
        from app.db.models.model_version_stats import ModelVersionStats
        from app.db.models.model import Model
        
        print("\nCreated stats entries:")
        stats = db.query(ModelVersionStats).join(Model).order_by(
            ModelVersionStats.avg_overall_score.desc()
        ).limit(10).all()
        
        for stat in stats:
            print(f"  {stat.model.name}: {stat.test_count} test(s), avg score: {stat.avg_overall_score}")
        
        if len(stats) < success_count:
            print(f"  ... and {success_count - len(stats)} more")
        
    except Exception as e:
        print(f"\nError during backfill: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Backfill model_version_stats table from existing test data"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    backfill_model_version_stats(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
