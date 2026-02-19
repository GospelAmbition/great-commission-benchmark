#!/usr/bin/env python3
"""
Permanently delete test runs (and their results) from the database.
Use for corrupted or erroneous submissions. Recalculates leaderboard stats after deletion.
When the last run for a model+version is deleted, the corresponding model_version_stats
row is removed so the model no longer appears on the leaderboard.

Note: This script does not clear the API cache. If the platform is running, the leaderboard
may show stale data until cache TTL or the next request; use Admin > Data > delete in the UI
to also invalidate cache, or restart the backend.

Usage:
    python scripts/delete_test_runs.py <test_run_id_1> [<test_run_id_2> ...]

Example:
    python scripts/delete_test_runs.py \\
        ebbbafa1-a324-499e-9704-2f4005405798 \\
        edb9e2de-b7cc-4f54-b236-5f89984cc05d

Run locally: set DATABASE_URL in .env (or env) and run from backend dir.
Run on Railway: use a one-off command with the backend service (DATABASE_URL is set).
"""
import sys
import os
from uuid import UUID

# Add the backend directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.models.test_run import TestRun
from app.db.models.result import Result
from app.services.aggregation import AggregationService


def delete_test_run(db: Session, test_run_id: UUID) -> bool:
    """Delete one test run and its results; recalc model stats. Returns True if deleted."""
    test_run = db.query(TestRun).filter(TestRun.id == test_run_id).first()
    if not test_run:
        print(f"  Test run {test_run_id} not found, skipping.")
        return False

    model_id = test_run.model_id
    question_set_id = test_run.question_set_id

    deleted_results = db.query(Result).filter(
        Result.test_run_id == test_run_id
    ).delete(synchronize_session=False)
    db.delete(test_run)
    db.commit()
    print(f"  Deleted test run {test_run_id} and {deleted_results} result(s).")

    try:
        AggregationService.recalculate_model_stats(db, model_id, question_set_id)
        print(f"  Recalculated model_version_stats for model {model_id}.")
    except Exception as e:
        print(f"  Warning: recalculate_model_stats failed: {e}")

    return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    uuids = []
    for arg in sys.argv[1:]:
        try:
            uuids.append(UUID(arg))
        except ValueError:
            print(f"Invalid UUID: {arg}")
            sys.exit(1)

    db: Session = SessionLocal()
    try:
        print(f"Deleting {len(uuids)} test run(s)...")
        for uid in uuids:
            delete_test_run(db, uid)
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
