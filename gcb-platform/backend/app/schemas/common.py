"""Common schemas used across the API"""
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

T = TypeVar('T')


class GCBBaseModel(BaseModel):
    """Base model for GCB schemas that allows 'model_' prefixed fields.
    
    Pydantic v2 reserves 'model_' prefix by default. Since we have legitimate
    fields like model_id, model_name, model_provider, we disable this protection.
    """
    model_config = ConfigDict(protected_namespaces=())


class PaginationParams(BaseModel):
    """Pagination query parameters"""
    limit: int = 50
    offset: int = 0


class PaginationResponse(BaseModel):
    """Pagination metadata"""
    limit: int
    offset: int
    total: int
    has_more: bool


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response"""
    success: bool = True
    data: T


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: dict


class TimestampMixin(BaseModel):
    """Mixin for timestamps"""
    created_at: datetime
    updated_at: Optional[datetime] = None