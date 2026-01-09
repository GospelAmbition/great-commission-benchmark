#!/usr/bin/env python3
"""Script to create or promote a user to admin role.

This script allows you to set up the initial administrator account by:
1. Finding a user by email and promoting them to admin, OR
2. Creating a new admin user (if they haven't signed in yet)

Usage:
    python scripts/create_admin.py --email user@example.com
    
    Or to list all users:
    python scripts/create_admin.py --list-users
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.models.user import User
from app.core.config import settings


def list_users(db: Session):
    """List all users in the database"""
    users = db.query(User).order_by(User.created_at).all()
    
    if not users:
        print("No users found in the database.")
        return
    
    print(f"\nFound {len(users)} user(s):\n")
    print(f"{'Email':<40} {'Name':<30} {'Role':<15} {'Created':<20}")
    print("-" * 105)
    
    for user in users:
        created = user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else "N/A"
        print(f"{user.email:<40} {user.name or 'N/A':<30} {user.role:<15} {created:<20}")
    
    print()


def promote_to_admin(db: Session, email: str, create_if_missing: bool = False) -> bool:
    """Promote a user to admin role by email"""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        if create_if_missing:
            # Create user for development purposes
            # Use a placeholder auth0_id that won't conflict with real OAuth users
            # Format: dev-{email_hash} to ensure uniqueness
            import hashlib
            email_hash = hashlib.md5(email.encode()).hexdigest()[:16]
            auth0_id = f"dev-{email_hash}"
            
            # Check if this auth0_id already exists (shouldn't happen, but be safe)
            existing = db.query(User).filter(User.auth0_id == auth0_id).first()
            if existing:
                print(f"\n⚠️  Warning: Found existing user with dev auth0_id, using existing user.")
                user = existing
            else:
                user = User(
                    auth0_id=auth0_id,
                    email=email,
                    name=email.split("@")[0].replace(".", " ").title(),  # Generate name from email
                    role="admin"  # Set directly to admin since we're creating for admin purposes
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"\n✅ Created new user '{email}' with admin role.")
                print(f"   User ID: {user.id}")
                print(f"   Note: This is a development user. For production, users should sign in via OAuth first.")
                return True
        else:
            print(f"\n❌ User with email '{email}' not found in the database.")
            print("\nPossible reasons:")
            print("  1. The user hasn't signed in yet (users are created on first OAuth login)")
            print("  2. The email address is incorrect")
            print("\nTo create the user:")
            print("  1. Have them sign in via Google OAuth on the platform")
            print("  2. Then run this script again with their email")
            print("\nOr for development, use --create-if-missing flag:")
            print(f"   python scripts/create_admin.py --email {email} --create-if-missing")
            return False
    
    if user.role == "admin":
        print(f"\n✅ User '{email}' is already an admin.")
        return True
    
    old_role = user.role
    user.role = "admin"
    db.commit()
    db.refresh(user)
    
    print(f"\n✅ Successfully promoted user '{email}' to admin role.")
    print(f"   Previous role: {old_role}")
    print(f"   New role: {user.role}")
    print(f"   User ID: {user.id}")
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create or promote a user to admin role",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Promote existing user to admin
  python scripts/create_admin.py --email admin@example.com
  
  # List all users
  python scripts/create_admin.py --list-users
        """
    )
    parser.add_argument(
        "--email",
        type=str,
        help="Email address of the user to promote to admin"
    )
    parser.add_argument(
        "--list-users",
        action="store_true",
        help="List all users in the database"
    )
    parser.add_argument(
        "--create-if-missing",
        action="store_true",
        help="Create the user if they don't exist (for development only)"
    )
    
    args = parser.parse_args()
    
    # Check database connection
    if not settings.DATABASE_URL:
        print("❌ Error: DATABASE_URL not configured.")
        print("   Make sure you have a .env file with DATABASE_URL set.")
        sys.exit(1)
    
    db: Session = SessionLocal()
    
    try:
        if args.list_users:
            list_users(db)
        elif args.email:
            promote_to_admin(db, args.email.lower().strip(), create_if_missing=args.create_if_missing)
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg or "relation" in error_msg.lower():
            print(f"\n❌ Error: Database tables don't exist yet.")
            print("\nYou need to run database migrations first:")
            print("  1. Make sure PostgreSQL is running")
            print("  2. Check that DATABASE_URL is set in your .env file")
            print("  3. Run migrations:")
            print("     cd gcb-platform/backend")
            print("     source venv/bin/activate  # or activate your virtual environment")
            print("     alembic upgrade head")
            print("  4. Then run this script again")
        else:
            print(f"\n❌ Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
