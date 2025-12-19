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


def promote_to_admin(db: Session, email: str) -> bool:
    """Promote a user to admin role by email"""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        print(f"\n❌ User with email '{email}' not found in the database.")
        print("\nPossible reasons:")
        print("  1. The user hasn't signed in yet (users are created on first OAuth login)")
        print("  2. The email address is incorrect")
        print("\nTo create the user:")
        print("  1. Have them sign in via Google OAuth on the platform")
        print("  2. Then run this script again with their email")
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
            promote_to_admin(db, args.email.lower().strip())
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
