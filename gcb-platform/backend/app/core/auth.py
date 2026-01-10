"""Authentication and authorization utilities"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import SessionLocal
from app.db.models.user import User

security = HTTPBearer()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from NextAuth JWT token
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    if not settings.NEXTAUTH_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication not configured"
        )
    
    try:
        # Verify NextAuth JWT token using HS256 algorithm
        payload = jwt.decode(
            token,
            settings.NEXTAUTH_SECRET,
            algorithms=["HS256"]
        )
        
        # Get provider account ID (Google user ID) from token
        provider_id = payload.get("sub")
        if not provider_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get or create user in database
        user = db.query(User).filter(User.auth0_id == provider_id).first()
        
        if not user:
            # Create user if doesn't exist
            email = payload.get("email", "")
            name = payload.get("name", "")
            # Default role is "user" - can be updated by admins
            role = payload.get("role", "user")
            
            user = User(
                auth0_id=provider_id,  # Keep field name for now, stores Google ID
                email=email,
                name=name,
                role=role
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


def has_permission(user: User, permission: str) -> bool:
    """
    Check if user has a specific permission.
    
    Admin permission cascades to all permissions.
    
    Args:
        user: User instance to check
        permission: Permission name ('can_view_benchmark', 'can_edit_benchmark', 
                   'can_moderate', 'can_manage_blog', 'can_admin')
    
    Returns:
        True if user has the permission, False otherwise
    """
    # Admin has all permissions
    if user.can_admin:
        return True
    
    # Check specific permission
    return getattr(user, permission, False)


def get_user_permissions(user: User) -> set[str]:
    """
    Get all effective permissions for a user.
    
    Admin permission cascades to all permissions.
    
    Args:
        user: User instance
    
    Returns:
        Set of permission names the user has
    """
    permissions = set()
    
    # Admin has all permissions
    if user.can_admin:
        return {
            'can_view_benchmark',
            'can_edit_benchmark',
            'can_moderate',
            'can_manage_blog',
            'can_admin'
        }
    
    # Check each permission
    if user.can_view_benchmark:
        permissions.add('can_view_benchmark')
    if user.can_edit_benchmark:
        permissions.add('can_edit_benchmark')
    if user.can_moderate:
        permissions.add('can_moderate')
    if user.can_manage_blog:
        permissions.add('can_manage_blog')
    if user.can_admin:
        permissions.add('can_admin')
    
    return permissions


def require_permission(permission_name: str):
    """
    Dependency factory for permission-based authorization
    
    Args:
        permission_name: Required permission ('can_view_benchmark', 'can_edit_benchmark',
                        'can_moderate', 'can_manage_blog', 'can_admin')
    
    Returns:
        Dependency function that checks user permission
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not has_permission(current_user, permission_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required permission: {permission_name}"
            )
        
        return current_user
    
    return permission_checker


# Convenience dependencies
require_auth = get_current_user
require_benchmark_viewer = require_permission("can_view_benchmark")
require_benchmark_editor = require_permission("can_edit_benchmark")
require_moderator = require_permission("can_moderate")
require_blog_manager = require_permission("can_manage_blog")
require_admin = require_permission("can_admin")

# Legacy role-based check for backward compatibility during migration
def require_role(required_role: str):
    """
    Legacy role-based authorization (deprecated, use require_permission instead)
    
    Maps roles to permissions for backward compatibility.
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Map roles to permissions
        role_permission_map = {
            "moderator": "can_moderate",
            "blog_manager": "can_manage_blog",
            "benchmark_developer": "can_edit_benchmark",
            "admin": "can_admin"
        }
        
        # Check if user has the required permission
        required_permission = role_permission_map.get(required_role)
        if required_permission and has_permission(current_user, required_permission):
            return current_user
        
        # Fallback: check role directly if permissions not set (during migration)
        role_hierarchy = {
            "user": 1,
            "moderator": 2,
            "blog_manager": 3,
            "benchmark_developer": 4,
            "admin": 5
        }
        
        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(required_role, 999)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        
        return current_user
    
    return role_checker


def is_fee_waived(user: User) -> bool:
    """
    Check if user has fees waived.
    
    This applies to both platform test requests and CLI submission fees.
    Fee is automatically waived for users with special permissions.
    Regular users can have fee waived via the fee_waived flag.
    
    Args:
        user: User instance to check
        
    Returns:
        True if fee is waived, False otherwise
    """
    # Auto-waive for users with special permissions
    if (has_permission(user, "can_moderate") or 
        has_permission(user, "can_manage_blog") or 
        has_permission(user, "can_edit_benchmark") or 
        has_permission(user, "can_admin")):
        return True
    # Manual waiver flag
    return user.fee_waived
