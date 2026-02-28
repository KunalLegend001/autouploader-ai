"""
Auto-Posting Router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from app.database import get_db
from app.models import Clip, Post, User, PostStatusEnum
from app.schemas import PostCreate, PostOut
from app.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=PostOut, status_code=202)
async def create_post(
    data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Schedule/immediately post a clip to a platform."""
    # Verify clip ownership
    clip_result = await db.execute(
        select(Clip).where(Clip.id == data.clip_id, Clip.user_id == current_user.id)
    )
    clip = clip_result.scalar_one_or_none()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    if not clip.s3_url:
        raise HTTPException(status_code=400, detail="Clip is not ready yet (processing)")

    post = Post(
        clip_id=data.clip_id,
        platform=data.platform,
        title=data.title or clip.title,
        description=data.description or clip.description,
        hashtags=data.hashtags or [],
        scheduled_at=data.scheduled_at,
        status=PostStatusEnum.QUEUED,
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)

    # Dispatch Celery task
    from app.tasks.posting_tasks import upload_to_platform
    task = upload_to_platform.apply_async(
        args=[str(post.id)],
        eta=data.scheduled_at if data.scheduled_at else None,
    )
    post.celery_task_id = task.id
    await db.flush()

    return post


@router.get("/", response_model=List[PostOut])
async def list_posts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Post)
        .join(Clip, Post.clip_id == Clip.id)
        .where(Clip.user_id == current_user.id)
        .order_by(Post.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{post_id}", response_model=PostOut)
async def get_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Post)
        .join(Clip, Post.clip_id == Clip.id)
        .where(Post.id == post_id, Clip.user_id == current_user.id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
