"""
Channels Router — Connect YouTube channels
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID
from app.database import get_db
from app.models import Channel, User, ChannelPlatformEnum
from app.schemas import ChannelCreate, ChannelOut
from app.auth import get_current_user
from app.config import settings
from app.services.youtube_downloader import YouTubeDownloader

router = APIRouter()


@router.get("/", response_model=List[ChannelOut])
async def list_channels(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Channel).where(Channel.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/", response_model=ChannelOut, status_code=201)
async def add_channel(
    data: ChannelCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check channel limit
    count_result = await db.execute(
        select(func.count(Channel.id)).where(
            Channel.user_id == current_user.id,
            Channel.is_active == True,
        )
    )
    count = count_result.scalar()
    if count >= settings.MAX_CHANNELS_PER_USER:
        raise HTTPException(
            status_code=403,
            detail=f"Channel limit reached ({settings.MAX_CHANNELS_PER_USER} channels max on your plan)",
        )

    # Check duplicate
    existing = await db.execute(
        select(Channel).where(
            Channel.user_id == current_user.id,
            Channel.external_channel_id == data.external_channel_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Channel already connected")

    channel = Channel(**data.model_dump(), user_id=current_user.id)
    db.add(channel)
    await db.flush()
    await db.refresh(channel)
    return channel


@router.delete("/{channel_id}", status_code=204)
async def remove_channel(
    channel_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Channel).where(
            Channel.id == channel_id,
            Channel.user_id == current_user.id,
        )
    )
    channel = result.scalar_one_or_none()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    await db.delete(channel)


@router.get("/{channel_id}/videos")
async def get_channel_videos(
    channel_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch latest videos from a connected channel."""
    result = await db.execute(
        select(Channel).where(
            Channel.id == channel_id,
            Channel.user_id == current_user.id,
        )
    )
    channel = result.scalar_one_or_none()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    downloader = YouTubeDownloader()
    videos = await downloader.get_channel_videos(
        channel_id=channel.external_channel_id,
        access_token=channel.access_token,
        max_results=20,
    )
    return {"videos": videos, "count": len(videos)}
