#!/usr/bin/env python3
"""Quick script to restore admin permissions for chris@chasm.solutions

This script updates the user to have admin role and all admin permissions.

Usage:
    cd gcb-platform/backend
    source venv/bin/activate  # or activate your virtual environment
    python scripts/restore_admin.py
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.models.user import User

def restore_admin():
    """Restore admin permissions for chris@chasm.solutions"""
    db: Session = SessionLocal()
    
    try:
        email = "chris@chasm.solutions"
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"\n❌ User with email '{email}' not found in the database.")
            print("\nPossible reasons:")
            print("  1. The user hasn't signed in yet (users are created on first OAuth login)")
            print("  2. The email address might be different in the database")
            print("\nTo find the user, run:")
            print("   python scripts/create_admin.py --list-users")
            return False
        
        # Check current status
        print(f"\nFound user: {user.email}")
        print(f"  Current role: {user.role}")
        print(f"  Current can_admin: {user.can_admin}")
        print(f"  Current can_view_benchmark: {user.can_view_benchmark}")
        print(f"  Current can_edit_benchmark: {user.can_edit_benchmark}")
        print(f"  Current can_moderate: {user.can_moderate}")
        print(f"  Current can_manage_blog: {user.can_manage_blog}")
        
        # Update to admin
        old_role = user.role
        old_can_admin = user.can_admin
        
        user.role = "admin"
        user.can_admin = True
        # Admin cascades to all permissions
        user.can_view_benchmark = True
        user.can_edit_benchmark = True
        user.can_moderate = True
        user.can_manage_blog = True
        
        db.commit()
        db.refresh(user)
        
        print(f"\n✅ Successfully restored admin permissions for '{email}'")
        print(f"   Role changed: {old_role} → {user.role}")
        print(f"   Admin permission changed: {old_can_admin} → {user.can_admin}")
        print(f"   All permissions granted: ✓")
        print(f"   User ID: {user.id}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    restore_admin()
