"""Common schemas used across the API"""
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T')


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