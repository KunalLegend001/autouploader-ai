"""
Analytics Router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Clip, Post, PostAnalytics, User, PlatformEnum
from app.schemas import AnalyticsSummary, ClipOut
from app.auth import get_current_user

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated analytics across all platforms."""
    since = datetime.utcnow() - timedelta(days=days)

    # Total clips
    clip_count = await db.execute(
        select(func.count(Clip.id)).where(Clip.user_id == current_user.id)
    )
    total_clips = clip_count.scalar() or 0

    # Total posts
    post_count = await db.execute(
        select(func.count(Post.id))
        .join(Clip, Post.clip_id == Clip.id)
        .where(Clip.user_id == current_user.id)
    )
    total_posts = post_count.scalar() or 0

    # Aggregate metrics from analytics records
    metrics = await db.execute(
        select(
            func.sum(PostAnalytics.views).label("views"),
            func.sum(PostAnalytics.likes).label("likes"),
            func.sum(PostAnalytics.comments).label("comments"),
            func.sum(PostAnalytics.shares).label("shares"),
            func.avg(PostAnalytics.engagement_rate).label("avg_engagement"),
        )
        .join(Post, PostAnalytics.post_id == Post.id)
        .join(Clip, Post.clip_id == Clip.id)
        .where(
            Clip.user_id == current_user.id,
            PostAnalytics.recorded_at >= since,
        )
    )
    row = metrics.first()

    # Platform breakdown
    platform_rows = await db.execute(
        select(
            PostAnalytics.platform,
            func.sum(PostAnalytics.views).label("views"),
            func.sum(PostAnalytics.likes).label("likes"),
            func.count(Post.id).label("posts"),
        )
        .join(Post, PostAnalytics.post_id == Post.id)
        .join(Clip, Post.clip_id == Clip.id)
        .where(Clip.user_id == current_user.id)
        .group_by(PostAnalytics.platform)
    )
    platform_breakdown = {
        str(r.platform): {
            "views": r.views or 0,
            "likes": r.likes or 0,
            "posts": r.posts or 0,
        }
        for r in platform_rows
    }

    # Best performing clip (by views)
    best_clip_row = await db.execute(
        select(Clip)
        .join(Post, Post.clip_id == Clip.id)
        .join(PostAnalytics, PostAnalytics.post_id == Post.id)
        .where(Clip.user_id == current_user.id)
        .order_by(desc(PostAnalytics.views))
        .limit(1)
    )
    best_clip = best_clip_row.scalar_one_or_none()

    return AnalyticsSummary(
        total_views=int(row.views or 0),
        total_likes=int(row.likes or 0),
        total_comments=int(row.comments or 0),
        total_shares=int(row.shares or 0),
        total_clips=total_clips,
        total_posts=total_posts,
        avg_engagement_rate=float(row.avg_engagement or 0.0),
        best_performing_clip=ClipOut.model_validate(best_clip) if best_clip else None,
        platform_breakdown=platform_breakdown,
    )


@router.get("/posts/{post_id}/analytics")
async def get_post_analytics(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get time-series analytics for a specific post."""
    result = await db.execute(
        select(PostAnalytics)
        .join(Post, PostAnalytics.post_id == Post.id)
        .join(Clip, Post.clip_id == Clip.id)
        .where(PostAnalytics.post_id == post_id, Clip.user_id == current_user.id)
        .order_by(PostAnalytics.recorded_at.asc())
    )
    records = result.scalars().all()
    if not records:
        raise HTTPException(status_code=404, detail="No analytics found for this post")

    return {
        "post_id": str(post_id),
        "data_points": [
            {
                "timestamp": r.recorded_at.isoformat(),
                "views": r.views,
                "likes": r.likes,
                "comments": r.comments,
                "shares": r.shares,
                "engagement_rate": r.engagement_rate,
            }
            for r in records
        ],
    }
