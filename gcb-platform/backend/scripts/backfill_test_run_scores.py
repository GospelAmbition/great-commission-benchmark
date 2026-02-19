#!/usr/bin/env python3
"""
Backfill pre-computed scores for existing completed test runs.

Populates overall_score, tier1_score, tier2_score, tier3_score, category_scores,
verdict_distribution, and total_questions on test_runs that have status='completed'
but overall_score IS NULL. Run once after deploying the 024_add_test_run_scores migration.

Usage:
    python scripts/backfill_test_run_scores.py [--dry-run]
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.models.test_run import TestRun
from app.services.scoring import compute_and_store_test_run_scores


def backfill_test_run_scores(dry_run: bool = False) -> tuple[int, int]:
    """Backfill scores for completed test runs with null overall_score."""
    db: Session = SessionLocal()
    success_count = 0
    error_count = 0

    try:
        test_runs = db.query(TestRun).filter(
            TestRun.status == "completed",
            TestRun.overall_score.is_(None),
        ).all()

        print(f"Found {len(test_runs)} completed test run(s) with null scores")

        for test_run in test_runs:
            try:
                if not dry_run:
                    compute_and_store_test_run_scores(db, test_run)
                    db.commit()
                print(f"  ✓ {test_run.id} (model_id={test_run.model_id})")
                success_count += 1
            except Exception as e:
                print(f"  ✗ {test_run.id}: {e}")
                error_count += 1
                db.rollback()

        return success_count, error_count
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill test run scores")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN - no changes will be made\n")

    success, errors = backfill_test_run_scores(dry_run=args.dry_run)

    print(f"\nDone: {success} updated, {errors} errors")
