"""
Users Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from app.database import get_db
from app.models import User, UsageRecord
from app.schemas import UserOut, UsageOut
from app.auth import get_current_user
from app.config import settings

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/me/usage", response_model=UsageOut)
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    month = datetime.utcnow().strftime("%Y-%m")
    result = await db.execute(
        select(UsageRecord).where(
            UsageRecord.user_id == current_user.id,
            UsageRecord.month == month,
        )
    )
    usage = result.scalar_one_or_none()

    clips_generated = usage.clips_generated if usage else 0
    channels_connected = usage.channels_connected if usage else 0

    return UsageOut(
        month=month,
        clips_generated=clips_generated,
        clips_remaining=max(0, settings.MAX_CLIPS_PER_MONTH - clips_generated),
        channels_connected=channels_connected,
        channels_remaining=max(0, settings.MAX_CHANNELS_PER_USER - channels_connected),
        max_clips=settings.MAX_CLIPS_PER_MONTH,
        max_channels=settings.MAX_CHANNELS_PER_USER,
    )
