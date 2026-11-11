from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from jose import jwt

from app.config import settings
from app.database import get_db
from app.models import Organization, User, Staff

security = HTTPBearer()


async def get_current_org_id(request_org_id: str) -> UUID:
    """Extract organization ID from context (Telegram user or JWT)"""
    try:
        return UUID(request_org_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization ID"
        )


async def verify_telegram_user(telegram_id: str, org_id: UUID, db: AsyncSession = Depends(get_db)) -> User:
    """Verify Telegram user exists in organization"""
    from sqlalchemy import select

    result = await db.execute(
        select(User).where(
            (User.telegram_id == telegram_id) &
            (User.organization_id == org_id)
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    user.last_seen = datetime.utcnow()
    await db.commit()

    return user


async def verify_staff_token(credentials: HTTPAuthorizationCredentials, db: AsyncSession = Depends(get_db)) -> Staff:
    """Verify JWT token for staff access"""
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"]
        )
        staff_id = payload.get("sub")
        if not staff_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    from sqlalchemy import select

    result = await db.execute(
        select(Staff).where(Staff.id == UUID(staff_id))
    )
    staff = result.scalar_one_or_none()

    if not staff or not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Staff member not found or inactive"
        )

    return staff


async def verify_org_access(staff: Staff) -> Organization:
    """Get organization for staff member"""
    if not staff.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No organization access"
        )
    return staff.organization


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt
