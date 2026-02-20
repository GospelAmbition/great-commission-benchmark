#!/usr/bin/env python3
"""Investigate an orphan record by UUID. Supports community_submission_id or test_run_id."""
import sys
import os
from uuid import UUID

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session, joinedload
from app.db.base import SessionLocal
from app.db.models.community_submission import CommunitySubmission
from app.db.models.test_run import TestRun
from app.db.models.moderation_log import ModerationLog
from app.db.models.model import Model
from app.db.models.user import User


def investigate(uuid_str: str):
    db: Session = SessionLocal()
    try:
        uid = UUID(uuid_str)

        # 1. Check if it's a CommunitySubmission
        cs = db.query(CommunitySubmission).options(
            joinedload(CommunitySubmission.user),
            joinedload(CommunitySubmission.reviewer),
        ).filter(CommunitySubmission.id == uid).first()

        if cs:
            print("=" * 70)
            print("COMMUNITY SUBMISSION")
            print("=" * 70)
            print(f"  ID:            {cs.id}")
            print(f"  Model name:    {cs.model_name}")
            print(f"  Status:        {cs.status}")
            print(f"  Submitted:     {cs.submitted_at}")
            print(f"  Reviewed at:   {cs.reviewed_at}")
            print(f"  Reviewer ID:   {cs.reviewer_id}")
            print(f"  User ID:       {cs.user_id}")
            if cs.user:
                print(f"  User email:    {cs.user.email}")
            if cs.reviewer:
                print(f"  Reviewer:      {cs.reviewer.email}")

            # Check for linked TestRun(s)
            runs = db.query(TestRun).options(
                joinedload(TestRun.model),
                joinedload(TestRun.user),
            ).filter(TestRun.community_submission_id == uid).all()

            print(f"\n  Linked TestRuns: {len(runs)}")
            if not runs:
                print("  >>> ORPHANED: Approved submission with NO associated test run <<<")
                if cs.status == "approved":
                    print("  >>> Run cleanup: POST /api/admin/cleanup/orphaned-approved-submissions <<<")
            else:
                for r in runs:
                    print(f"    - {r.id} (model: {r.model.name if r.model else '?'}, status: {r.status})")

            # ModerationLog for those runs
            run_ids = [r.id for r in runs]
            if run_ids:
                logs = db.query(ModerationLog).filter(
                    ModerationLog.test_run_id.in_(run_ids)
                ).all()
                print(f"\n  ModerationLogs for linked runs: {len(logs)}")

            print("=" * 70)
            return

        # 2. Check if it's a TestRun
        tr = db.query(TestRun).options(
            joinedload(TestRun.model),
            joinedload(TestRun.community_submission),
            joinedload(TestRun.user),
        ).filter(TestRun.id == uid).first()

        if tr:
            print("=" * 70)
            print("TEST RUN")
            print("=" * 70)
            print(f"  ID:                    {tr.id}")
            print(f"  Model:                 {tr.model.name if tr.model else '?'}")
            print(f"  Status:                {tr.status}")
            print(f"  community_submission:   {tr.community_submission_id}")
            if tr.community_submission:
                print(f"  Submission status:     {tr.community_submission.status}")

            logs = db.query(ModerationLog).filter(ModerationLog.test_run_id == uid).all()
            print(f"\n  ModerationLogs: {len(logs)}")

            print("=" * 70)
            return

        # 3. Check ModerationLog (orphaned = log exists but test_run gone)
        log = db.query(ModerationLog).filter(ModerationLog.id == uid).first()
        if log:
            run = db.query(TestRun).filter(TestRun.id == log.test_run_id).first()
            print("=" * 70)
            print("MODERATION LOG")
            print("=" * 70)
            print(f"  ID:          {log.id}")
            print(f"  test_run_id: {log.test_run_id}")
            print(f"  TestRun exists: {run is not None}")
            if run is None:
                print("  >>> ORPHANED: ModerationLog references deleted TestRun <<<")
                print("  >>> Run cleanup: POST /api/admin/cleanup/orphaned-moderation-logs <<<")
            print("=" * 70)
            return

        print(f"No record found for UUID: {uuid_str}")
        print("Checked: CommunitySubmission, TestRun, ModerationLog")

    except ValueError as e:
        print(f"Invalid UUID: {uuid_str}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python investigate_orphan.py <uuid>")
        print("Example: python investigate_orphan.py eddf6a8a-10b9-413d-9a59-e63c14afb20e")
        sys.exit(1)
    investigate(sys.argv[1])
