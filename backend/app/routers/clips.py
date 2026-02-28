"""
Clips Router — AI clip generation
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID
import os
from datetime import datetime
from app.database import get_db
from app.models import Clip, SourceVideo, User, UsageRecord, ClipStatusEnum
from app.schemas import ClipGenerateRequest, ClipOut
from app.auth import get_current_user
from app.config import settings
from app.services.youtube_downloader import YouTubeDownloader

router = APIRouter()


@router.get("/", response_model=List[ClipOut])
async def list_clips(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Clip).where(Clip.user_id == current_user.id)
    if status:
        query = query.where(Clip.status == status)
    query = query.order_by(Clip.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/generate", status_code=202)
async def generate_clips(
    data: ClipGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger AI clip generation from a source video.
    Returns task info immediately — processing happens in background.
    """
    # Check monthly usage limit
    month = datetime.utcnow().strftime("%Y-%m")
    usage_result = await db.execute(
        select(UsageRecord).where(
            UsageRecord.user_id == current_user.id,
            UsageRecord.month == month,
        )
    )
    usage = usage_result.scalar_one_or_none()
    clips_used = usage.clips_generated if usage else 0

    if clips_used + data.num_clips > settings.MAX_CLIPS_PER_MONTH:
        remaining = max(0, settings.MAX_CLIPS_PER_MONTH - clips_used)
        raise HTTPException(
            status_code=429,
            detail=f"Monthly clip limit reached. You have {remaining} clips remaining this month.",
        )

    # Get source video
    sv_result = await db.execute(
        select(SourceVideo).where(SourceVideo.id == data.source_video_id)
    )
    source_video = sv_result.scalar_one_or_none()
    if not source_video:
        raise HTTPException(status_code=404, detail="Source video not found")

    # Check if video is already downloaded locally
    video_path = source_video.local_path
    if not video_path or not os.path.exists(video_path):
        if not source_video.video_url:
            raise HTTPException(status_code=400, detail="No video URL available. Please provide a YouTube URL.")
        video_path = source_video.video_url  # pass URL; pipeline will download it

    # Queue Celery task
    from app.tasks.clip_tasks import generate_clips as celery_generate
    task = celery_generate.delay(
        source_video_id=str(data.source_video_id),
        user_id=str(current_user.id),
        video_path=video_path,
        num_clips=data.num_clips,
        min_duration=data.min_duration,
        max_duration=data.max_duration,
        add_captions=data.add_captions,
        add_broll=data.add_broll,
        vertical_format=data.vertical_format,
        custom_prompt=data.custom_prompt,
    )

    return {
        "message": "Clip generation started",
        "task_id": task.id,
        "source_video_id": str(data.source_video_id),
        "estimated_time_minutes": data.num_clips * 3,
    }


@router.post("/generate-from-url", status_code=202)
async def generate_clips_from_url(
    youtube_url: str,
    num_clips: int = 5,
    add_captions: bool = True,
    vertical_format: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Direct URL input — download + generate clips from a YouTube URL."""
    downloader = YouTubeDownloader()
    try:
        info = await downloader.get_video_info(youtube_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot fetch video info: {e}")

    # Create SourceVideo without a channel (channel_id is nullable)
    sv = SourceVideo(
        channel_id=None,
        external_video_id=info.get("id", "direct"),
        title=info.get("title", "Unknown"),
        description=info.get("description", ""),
        thumbnail_url=info.get("thumbnail"),
        duration_seconds=info.get("duration"),
        video_url=youtube_url,
    )
    db.add(sv)
    await db.flush()
    await db.refresh(sv)

    from app.tasks.clip_tasks import generate_clips as celery_generate
    task = celery_generate.delay(
        source_video_id=str(sv.id),
        user_id=str(current_user.id),
        video_path=youtube_url,
        num_clips=num_clips,
        add_captions=add_captions,
        vertical_format=vertical_format,
    )

    return {
        "message": "Download and clip generation started",
        "task_id": task.id,
        "video_title": info.get("title"),
        "video_duration": info.get("duration"),
        "estimated_time_minutes": num_clips * 3,
    }


@router.get("/{clip_id}", response_model=ClipOut)
async def get_clip(
    clip_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Clip).where(Clip.id == clip_id, Clip.user_id == current_user.id)
    )
    clip = result.scalar_one_or_none()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    return clip


@router.delete("/{clip_id}", status_code=204)
async def delete_clip(
    clip_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Clip).where(Clip.id == clip_id, Clip.user_id == current_user.id)
    )
    clip = result.scalar_one_or_none()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    await db.delete(clip)
