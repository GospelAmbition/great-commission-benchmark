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


def require_role(required_role: str):
    """
    Dependency factory for role-based authorization
    
    Args:
        required_role: Required role ('user', 'moderator', 'benchmark_developer', 'admin')
    
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        role_hierarchy = {
            "user": 1,
            "moderator": 2,
            "benchmark_developer": 3,
            "admin": 4
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


# Convenience dependencies
require_auth = get_current_user
require_moderator = require_role("moderator")
require_benchmark_developer = require_role("benchmark_developer")
require_admin = require_role("admin")


def is_fee_waived(user: User) -> bool:
    """
    Check if user has fees waived.
    
    This applies to both platform test requests and CLI submission fees.
    Fee is automatically waived for moderators and admins.
    Regular users can have fee waived via the fee_waived flag.
    
    Args:
        user: User instance to check
        
    Returns:
        True if fee is waived, False otherwise
    """
    # Auto-waive for moderators, benchmark developers, and admins
    if user.role in ("moderator", "benchmark_developer", "admin"):
        return True
    # Manual waiver flag
    return user.fee_waived
