"""API Key schemas"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class CreateAPIKeyRequest(BaseModel):
    """Request to create a new API key"""
    name: str = Field(..., min_length=1, max_length=255, description="Friendly name for the API key")


class CreateAPIKeyResponse(BaseModel):
    """Response after creating an API key - includes the full key (only shown once)"""
    id: UUID
    name: str
    key: str  # Full API key - only returned on creation
    key_prefix: str
    created_at: datetime
    message: str = "Store this API key securely. It will not be shown again."


class APIKeyListItem(BaseModel):
    """API key list item (without the actual key)"""
    id: UUID
    name: str
    key_prefix: str
    is_active: bool
    last_used_at: Optional[datetime] = None
    created_at: datetime
    expires_at: Optional[datetime] = None


class APIKeyListResponse(BaseModel):
    """List of user's API keys"""
    api_keys: List[APIKeyListItem]
    total: int


class RevokeAPIKeyResponse(BaseModel):
    """Response after revoking an API key"""
    id: UUID
    message: str = "API key revoked successfully"
