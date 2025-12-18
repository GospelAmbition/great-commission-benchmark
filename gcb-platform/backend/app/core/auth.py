"""Authentication and authorization utilities"""
from typing import Optional
import httpx
from functools import lru_cache
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt, jwk
from jose.utils import base64url_decode
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import SessionLocal
from app.db.models.user import User

security = HTTPBearer()

# Cache for JWKS keys
_jwks_cache = {}


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_jwks():
    """Fetch JWKS from Auth0 for token verification"""
    global _jwks_cache
    if not _jwks_cache:
        if not settings.AUTH0_DOMAIN:
            return None
        
        jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        try:
            response = httpx.get(jwks_url, timeout=10.0)
            response.raise_for_status()
            _jwks_cache = response.json()
        except Exception:
            return None
    
    return _jwks_cache


def get_rsa_key(token: str):
    """Get the RSA key for verifying the token"""
    jwks = get_jwks()
    if not jwks:
        return None
    
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        return None
    
    for key in jwks.get("keys", []):
        if key.get("kid") == unverified_header.get("kid"):
            return {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    return None


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
        # Get RSA key for verification
        rsa_key = get_rsa_key(token)
        
        if rsa_key and settings.AUTH0_DOMAIN:
            # Verify token with proper signature verification
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=settings.AUTH0_AUDIENCE,
                issuer=f"https://{settings.AUTH0_DOMAIN}/"
            )
        else:
            # Fallback for development/testing without Auth0 configured
            # WARNING: This should not be used in production
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
        
        auth0_id = payload.get("sub")
        if not auth0_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Validate token expiration is handled by jose library
        
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
        
    except JWTError as e:
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
