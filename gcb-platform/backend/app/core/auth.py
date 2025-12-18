"""Authentication and authorization utilities"""
from typing import Optional
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
    Get current authenticated user from JWT token
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    try:
        # Verify and decode JWT token
        # Auth0 uses RS256, so we need to get the public key
        # For now, we'll use a simple verification
        # In production, fetch JWKS from Auth0
        unverified_header = jwt.get_unverified_header(token)
        
        # Get the public key from Auth0
        # This is a simplified version - in production, use jwks_client
        payload = jwt.decode(
            token,
            options={"verify_signature": False}  # TODO: Implement proper signature verification
        )
        
        auth0_id = payload.get("sub")
        if not auth0_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get or create user in database
        user = db.query(User).filter(User.auth0_id == auth0_id).first()
        
        if not user:
            # Create user if doesn't exist
            email = payload.get("email", "")
            name = payload.get("name", "")
            # Get role from token (set in Auth0)
            role = payload.get("https://gcb.app/role", "user")
            
            user = User(
                auth0_id=auth0_id,
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
        required_role: Required role ('user', 'moderator', 'admin')
    
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        role_hierarchy = {
            "user": 1,
            "moderator": 2,
            "admin": 3
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
require_admin = require_role("admin")
