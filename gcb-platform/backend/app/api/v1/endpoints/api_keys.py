"""User API Key management endpoints"""
import secrets
import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_db, require_auth
from app.db.models.user import User
from app.db.models.user_api_key import UserAPIKey
from app.schemas.api_keys import (
    CreateAPIKeyRequest,
    CreateAPIKeyResponse,
    APIKeyListItem,
    APIKeyListResponse,
    RevokeAPIKeyResponse
)

router = APIRouter()

# Constants
API_KEY_PREFIX = "gcb_"
API_KEY_LENGTH = 32  # Length of random portion


def generate_api_key() -> tuple[str, str, str]:
    """Generate a new API key.
    
    Returns:
        tuple: (full_key, key_prefix, key_hash)
    """
    # Generate random bytes and convert to hex
    random_part = secrets.token_hex(API_KEY_LENGTH)
    full_key = f"{API_KEY_PREFIX}{random_part}"
    
    # Key prefix for identification (first 8 chars after gcb_)
    key_prefix = f"{API_KEY_PREFIX}{random_part[:4]}"
    
    # Hash the full key for storage
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    
    return full_key, key_prefix, key_hash


def hash_api_key(key: str) -> str:
    """Hash an API key for comparison."""
    return hashlib.sha256(key.encode()).hexdigest()


@router.post("", response_model=CreateAPIKeyResponse)
async def create_api_key(
    request: CreateAPIKeyRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Create a new API key for the current user.
    
    The full API key is only returned once. Store it securely.
    """
    # Check if user has too many keys (limit to 10)
    existing_count = db.query(UserAPIKey).filter(
        UserAPIKey.user_id == current_user.id,
        UserAPIKey.is_active == True
    ).count()
    
    if existing_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum of 10 active API keys allowed. Please revoke an existing key first."
        )
    
    # Check for duplicate name
    existing_name = db.query(UserAPIKey).filter(
        UserAPIKey.user_id == current_user.id,
        UserAPIKey.name == request.name,
        UserAPIKey.is_active == True
    ).first()
    
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An API key with this name already exists."
        )
    
    # Generate new key
    full_key, key_prefix, key_hash = generate_api_key()
    
    # Create database record
    api_key = UserAPIKey(
        user_id=current_user.id,
        name=request.name,
        key_prefix=key_prefix,
        key_hash=key_hash,
        is_active=True
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return CreateAPIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        key=full_key,
        key_prefix=key_prefix,
        created_at=api_key.created_at
    )


@router.get("", response_model=APIKeyListResponse)
async def list_api_keys(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    List all API keys for the current user.
    
    Note: The actual key values are not returned, only metadata.
    """
    api_keys = db.query(UserAPIKey).filter(
        UserAPIKey.user_id == current_user.id
    ).order_by(UserAPIKey.created_at.desc()).all()
    
    items = [
        APIKeyListItem(
            id=key.id,
            name=key.name,
            key_prefix=key.key_prefix,
            is_active=key.is_active,
            last_used_at=key.last_used_at,
            created_at=key.created_at,
            expires_at=key.expires_at
        )
        for key in api_keys
    ]
    
    return APIKeyListResponse(
        api_keys=items,
        total=len(items)
    )


@router.delete("/{key_id}", response_model=RevokeAPIKeyResponse)
async def revoke_api_key(
    key_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Revoke an API key.
    
    This permanently disables the key. The action cannot be undone.
    """
    api_key = db.query(UserAPIKey).filter(
        UserAPIKey.id == key_id,
        UserAPIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    if not api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key is already revoked"
        )
    
    # Revoke the key
    api_key.is_active = False
    db.commit()
    
    return RevokeAPIKeyResponse(id=api_key.id)


# Utility function for validating API keys (used by runner endpoints)
def validate_api_key(db: Session, api_key: str) -> tuple[UserAPIKey | None, User | None]:
    """
    Validate an API key and return the key record and associated user.
    
    Args:
        db: Database session
        api_key: The full API key to validate
        
    Returns:
        tuple: (UserAPIKey, User) if valid, (None, None) if invalid
    """
    if not api_key or not api_key.startswith(API_KEY_PREFIX):
        return None, None
    
    # Hash the provided key
    key_hash = hash_api_key(api_key)
    
    # Look up the key
    db_key = db.query(UserAPIKey).filter(
        UserAPIKey.key_hash == key_hash,
        UserAPIKey.is_active == True
    ).first()
    
    if not db_key:
        return None, None
    
    # Check if expired
    if db_key.expires_at and db_key.expires_at < datetime.utcnow():
        return None, None
    
    # Update last used timestamp
    db_key.last_used_at = datetime.utcnow()
    db.commit()
    
    # Get the user
    user = db.query(User).filter(User.id == db_key.user_id).first()
    
    return db_key, user
