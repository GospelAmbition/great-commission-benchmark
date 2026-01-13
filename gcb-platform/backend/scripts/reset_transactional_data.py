#!/usr/bin/env python3
"""Script to reset transactional data in the database.

This script clears all transactional data (test runs, results, models, etc.)
while preserving schema, users, questions, and methodology versions.

IMPORTANT: This script should be used with caution, especially in production.

Usage:
    # Local development (will prompt for confirmation)
    python scripts/reset_transactional_data.py
    
    # Dry run (preview what would be deleted)
    python scripts/reset_transactional_data.py --dry-run
    
    # Production (requires explicit flags)
    python scripts/reset_transactional_data.py --production --confirm
    
    # Skip certain tables
    python scripts/reset_transactional_data.py --skip-models --skip-moderation-log
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.base import SessionLocal
from app.db.models.result import Result
from app.db.models.test_run import TestRun
from app.db.models.model import Model
from app.db.models.sponsorship_request import SponsorshipRequest
from app.db.models.community_submission import CommunitySubmission
from app.db.models.moderation_log import ModerationLog
from app.core.config import settings


# Tables to clear in order (respects foreign key constraints)
TABLES_TO_CLEAR = [
    ("results", Result, "Individual question results"),
    ("test_runs", TestRun, "Test run records"),
    ("sponsorship_requests", SponsorshipRequest, "Model sponsorship requests"),
    ("community_submissions", CommunitySubmission, "Community question submissions"),
    ("moderation_log", ModerationLog, "Moderation audit trail"),
    ("models", Model, "AI model records"),
]


def detect_environment() -> str:
    """Detect if we're running against local or production database."""
    db_url = settings.DATABASE_URL.lower()
    
    # Check for common production indicators
    production_indicators = [
        "railway",
        "heroku",
        "render",
        "aws",
        "azure",
        "gcp",
        "production",
        "prod",
    ]
    
    for indicator in production_indicators:
        if indicator in db_url:
            return "production"
    
    # Check for local indicators
    local_indicators = ["localhost", "127.0.0.1", "local"]
    for indicator in local_indicators:
        if indicator in db_url:
            return "local"
    
    # If unsure, treat as production for safety
    return "unknown"


def get_table_counts(db: Session) -> dict:
    """Get current row counts for all tables to be cleared."""
    counts = {}
    for table_name, model, description in TABLES_TO_CLEAR:
        try:
            count = db.query(model).count()
            counts[table_name] = count
        except Exception as e:
            counts[table_name] = f"Error: {e}"
    return counts


def clear_table(db: Session, table_name: str, model, dry_run: bool = False) -> int:
    """Clear all records from a table. Returns count of deleted records."""
    count = db.query(model).count()
    
    if count == 0:
        return 0
    
    if not dry_run:
        db.query(model).delete(synchronize_session=False)
    
    return count


def reset_transactional_data(
    db: Session,
    dry_run: bool = False,
    skip_models: bool = False,
    skip_moderation_log: bool = False,
) -> dict:
    """
    Reset all transactional data.
    
    Args:
        db: Database session
        dry_run: If True, only preview what would be deleted
        skip_models: If True, preserve model records
        skip_moderation_log: If True, preserve moderation log records
    
    Returns:
        Dictionary with deletion counts per table
    """
    results = {}
    
    tables = TABLES_TO_CLEAR.copy()
    
    # Apply skip filters
    if skip_models:
        tables = [(t, m, d) for t, m, d in tables if t != "models"]
    if skip_moderation_log:
        tables = [(t, m, d) for t, m, d in tables if t != "moderation_log"]
    
    for table_name, model, description in tables:
        try:
            deleted_count = clear_table(db, table_name, model, dry_run)
            results[table_name] = {
                "deleted": deleted_count,
                "description": description,
                "status": "preview" if dry_run else "deleted"
            }
        except Exception as e:
            results[table_name] = {
                "deleted": 0,
                "description": description,
                "status": f"error: {e}"
            }
    
    if not dry_run:
        db.commit()
    
    return results


def print_banner(environment: str):
    """Print warning banner."""
    print("\n" + "=" * 70)
    print("  TRANSACTIONAL DATA RESET SCRIPT")
    print("=" * 70)
    print(f"\n  Environment: {environment.upper()}")
    print(f"  Database: {settings.DATABASE_URL[:50]}...")
    print()


def print_counts(counts: dict, title: str = "Current Record Counts"):
    """Print table counts in a formatted way."""
    print(f"\n{title}:")
    print("-" * 50)
    total = 0
    for table_name, count in counts.items():
        if isinstance(count, int):
            total += count
            print(f"  {table_name:<30} {count:>10,}")
        else:
            print(f"  {table_name:<30} {count}")
    print("-" * 50)
    print(f"  {'TOTAL':<30} {total:>10,}")
    print()


def print_results(results: dict, dry_run: bool):
    """Print deletion results."""
    action = "Would delete" if dry_run else "Deleted"
    print(f"\n{action}:")
    print("-" * 60)
    total = 0
    for table_name, info in results.items():
        status = info["status"]
        deleted = info["deleted"]
        desc = info["description"]
        total += deleted if isinstance(deleted, int) else 0
        
        if "error" in status:
            print(f"  ❌ {table_name:<25} ERROR: {status}")
        elif deleted > 0:
            print(f"  ✓ {table_name:<25} {deleted:>10,} records  ({desc})")
        else:
            print(f"  - {table_name:<25} {'no records':>10}  ({desc})")
    print("-" * 60)
    print(f"  {'TOTAL':<25} {total:>10,} records")
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Reset transactional data in the database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be deleted (dry run)
  python scripts/reset_transactional_data.py --dry-run
  
  # Reset local database (will prompt for confirmation)
  python scripts/reset_transactional_data.py
  
  # Reset production database (requires explicit flags)
  python scripts/reset_transactional_data.py --production --confirm
  
  # Skip certain tables
  python scripts/reset_transactional_data.py --skip-models
  
Data that will be cleared:
  - results             Individual question results
  - test_runs           Test run records
  - sponsorship_requests  Model sponsorship requests
  - community_submissions Community question submissions
  - moderation_log      Moderation audit trail
  - models              AI model records

Data that will be PRESERVED:
  - users               User accounts
  - questions           Benchmark questions
  - question_sets       Question set definitions
  - methodology_versions  Scoring methodology versions
  - newsletter_subscribers  Email subscribers
  - user_api_keys       User API keys
        """
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be deleted without making changes"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Acknowledge this is a production database"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt (required with --production)"
    )
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Preserve model records"
    )
    parser.add_argument(
        "--skip-moderation-log",
        action="store_true",
        help="Preserve moderation log records"
    )
    
    args = parser.parse_args()
    
    # Check database connection
    if not settings.DATABASE_URL:
        print("❌ Error: DATABASE_URL not configured.")
        print("   Make sure you have a .env file with DATABASE_URL set.")
        sys.exit(1)
    
    # Detect environment
    environment = detect_environment()
    
    # Safety checks for production
    if environment == "production" or environment == "unknown":
        if not args.production:
            print("\n⚠️  WARNING: This appears to be a PRODUCTION database!")
            print("   To reset production data, you must use: --production --confirm")
            print(f"\n   Detected environment: {environment}")
            print(f"   Database URL: {settings.DATABASE_URL[:50]}...")
            sys.exit(1)
        
        if not args.confirm and not args.dry_run:
            print("\n⚠️  WARNING: Production database reset requires --confirm flag")
            print("   Use: --production --confirm")
            sys.exit(1)
    
    # Print banner
    print_banner(environment)
    
    db: Session = SessionLocal()
    
    try:
        # Get current counts
        counts = get_table_counts(db)
        print_counts(counts)
        
        # Check if there's anything to delete
        total_records = sum(c for c in counts.values() if isinstance(c, int))
        if total_records == 0:
            print("✓ No transactional data to clear. Database is already clean.")
            sys.exit(0)
        
        # Dry run mode
        if args.dry_run:
            print("\n🔍 DRY RUN MODE - No changes will be made\n")
            results = reset_transactional_data(
                db,
                dry_run=True,
                skip_models=args.skip_models,
                skip_moderation_log=args.skip_moderation_log
            )
            print_results(results, dry_run=True)
            print("To actually delete this data, run without --dry-run")
            sys.exit(0)
        
        # Confirmation for local development
        if environment == "local" and not args.confirm:
            print("\n⚠️  This will PERMANENTLY DELETE the data listed above.")
            print("   This action cannot be undone.\n")
            
            response = input("Type 'DELETE' to confirm: ").strip()
            if response != "DELETE":
                print("\n❌ Aborted. No changes made.")
                sys.exit(1)
        
        # Perform deletion
        print("\n🗑️  Deleting transactional data...\n")
        results = reset_transactional_data(
            db,
            dry_run=False,
            skip_models=args.skip_models,
            skip_moderation_log=args.skip_moderation_log
        )
        print_results(results, dry_run=False)
        
        # Verify deletion
        new_counts = get_table_counts(db)
        remaining = sum(c for c in new_counts.values() if isinstance(c, int))
        
        if remaining == 0:
            print("✅ All transactional data has been cleared successfully!")
        else:
            print(f"⚠️  Some records may remain ({remaining} total)")
            print_counts(new_counts, "Remaining Records")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

