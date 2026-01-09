#!/usr/bin/env python3
"""Setup script to ensure development database is ready and admin user exists.

This script:
1. Checks if database tables exist (runs migrations if needed)
2. Creates or promotes the specified user to admin

Usage:
    python scripts/setup_dev_admin.py --email chris@chasm.solutions
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from app.db.base import SessionLocal, engine
from app.db.models.user import User
from app.core.config import settings


def check_tables_exist() -> bool:
    """Check if database tables exist"""
    try:
        # Use a direct connection to check tables
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """))
            exists = result.scalar()
            return bool(exists)
    except Exception as e:
        print(f"⚠️  Could not check tables: {e}")
        return False


def run_migrations():
    """Run database migrations"""
    try:
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config(str(Path(__file__).parent.parent / "alembic.ini"))
        print("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully.")
        return True
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        print("\nPlease run migrations manually:")
        print("  cd gcb-platform/backend")
        print("  source venv/bin/activate")
        print("  alembic upgrade head")
        return False


def ensure_admin_user(email: str) -> bool:
    """Ensure the specified user exists and is an admin"""
    from scripts.create_admin import promote_to_admin
    
    db: Session = SessionLocal()
    try:
        return promote_to_admin(db, email.lower().strip(), create_if_missing=True)
    except Exception as e:
        print(f"❌ Error ensuring admin user: {e}")
        return False
    finally:
        db.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Setup development database and ensure admin user exists",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--email",
        type=str,
        default="chris@chasm.solutions",
        help="Email address of the admin user (default: chris@chasm.solutions)"
    )
    parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help="Skip running migrations (assume tables already exist)"
    )
    
    args = parser.parse_args()
    
    # Check database connection
    if not settings.DATABASE_URL:
        print("❌ Error: DATABASE_URL not configured.")
        print("   Make sure you have a .env file with DATABASE_URL set.")
        sys.exit(1)
    
    # Check if tables exist
    if not args.skip_migrations:
        if not check_tables_exist():
            print("📋 Database tables don't exist. Running migrations...")
            if not run_migrations():
                sys.exit(1)
            # Verify tables exist after migrations
            if not check_tables_exist():
                print("❌ Error: Tables still don't exist after migrations.")
                print("   Please check your DATABASE_URL and database connection.")
                sys.exit(1)
        else:
            print("✅ Database tables exist.")
    else:
        print("⏭️  Skipping migration check.")
    
    # Ensure admin user
    print(f"\n👤 Ensuring admin user: {args.email}")
    if ensure_admin_user(args.email):
        print("\n✅ Setup complete! The user is now an administrator.")
    else:
        print("\n❌ Failed to set up admin user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
