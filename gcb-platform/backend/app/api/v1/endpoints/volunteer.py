"""Volunteer API endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_db, get_current_user, require_admin
from app.db.models.volunteer_application import VolunteerApplication
from app.db.models.user import User
from app.schemas.volunteer import (
    VolunteerApplicationRequest,
    VolunteerApplicationResponse,
    VolunteerApplicationListItem,
    VolunteerApplicationListResponse
)

router = APIRouter()
optional_security = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(optional_security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    try:
        # Manually decode the token since we can't use the dependency directly
        from jose import JWTError, jwt
        from app.core.config import settings
        
        if not settings.NEXTAUTH_SECRET:
            return None
        
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.NEXTAUTH_SECRET,
            algorithms=["HS256"]
        )
        
        provider_id = payload.get("sub")
        if not provider_id:
            return None
        
        user = db.query(User).filter(User.auth0_id == provider_id).first()
        return user
    except Exception:
        # If authentication fails, return None (user is not authenticated)
        return None


@router.post("/apply", response_model=VolunteerApplicationResponse)
async def apply_volunteer(
    request: VolunteerApplicationRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Submit a volunteer application"""
    # If user is authenticated, link the application to their account
    user_id = current_user.id if current_user else None
    
    # Create application
    application = VolunteerApplication(
        user_id=user_id,
        email=request.email,
        name=request.name,
        role=request.role,
        background=request.background,
        motivation=request.motivation,
        status="pending"
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return VolunteerApplicationResponse(
        success=True,
        message="Volunteer application submitted successfully",
        application_id=application.id
    )


@router.get("/applications", response_model=VolunteerApplicationListResponse)
async def list_volunteer_applications(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    role: Optional[str] = Query(None)
):
    """List all volunteer applications (admin only)"""
    query = db.query(VolunteerApplication)
    
    # Filter by status if provided
    if status:
        query = query.filter(VolunteerApplication.status == status)
    
    # Filter by role if provided
    if role:
        query = query.filter(VolunteerApplication.role == role)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    applications = query.order_by(
        VolunteerApplication.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return VolunteerApplicationListResponse(
        applications=[
            VolunteerApplicationListItem(
                id=app.id,
                user_id=app.user_id,
                email=app.email,
                name=app.name,
                role=app.role.value,
                background=app.background,
                motivation=app.motivation,
                status=app.status,
                reviewed_at=app.reviewed_at,
                reviewed_by=app.reviewed_by,
                notes=app.notes,
                created_at=app.created_at,
                updated_at=app.updated_at
            )
            for app in applications
        ],
        total=total
    )
