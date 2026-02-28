"""
Pydantic Schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models import PlatformEnum, PostStatusEnum, ClipStatusEnum, ChannelPlatformEnum


# ─────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


# ─────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────
class UserOut(BaseModel):
    id: UUID
    email: str
    username: str
    is_active: bool
    plan: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Channels
# ─────────────────────────────────────────────
class ChannelCreate(BaseModel):
    platform: ChannelPlatformEnum
    external_channel_id: str
    channel_name: str
    channel_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class ChannelOut(BaseModel):
    id: UUID
    user_id: UUID
    platform: ChannelPlatformEnum
    external_channel_id: str
    channel_name: str
    channel_url: Optional[str]
    thumbnail_url: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Source Videos
# ─────────────────────────────────────────────
class SourceVideoOut(BaseModel):
    id: UUID
    channel_id: UUID
    external_video_id: str
    title: Optional[str]
    duration_seconds: Optional[int]
    thumbnail_url: Optional[str]
    processed: bool
    published_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Clips
# ─────────────────────────────────────────────
class ClipGenerateRequest(BaseModel):
    source_video_id: UUID
    num_clips: int = 5
    min_duration: int = 20   # seconds
    max_duration: int = 60   # seconds
    add_captions: bool = True
    add_broll: bool = False
    vertical_format: bool = True
    custom_prompt: Optional[str] = None


class ClipOut(BaseModel):
    id: UUID
    user_id: UUID
    source_video_id: Optional[UUID]
    title: Optional[str]
    description: Optional[str]
    start_time: Optional[float]
    end_time: Optional[float]
    duration: Optional[float]
    viral_score: float
    status: ClipStatusEnum
    s3_url: Optional[str]
    thumbnail_url: Optional[str]
    has_captions: bool
    has_broll: bool
    is_vertical: bool
    ai_tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Posts
# ─────────────────────────────────────────────
class PostCreate(BaseModel):
    clip_id: UUID
    platform: PlatformEnum
    title: Optional[str] = None
    description: Optional[str] = None
    hashtags: Optional[List[str]] = []
    scheduled_at: Optional[datetime] = None


class PostOut(BaseModel):
    id: UUID
    clip_id: UUID
    platform: PlatformEnum
    status: PostStatusEnum
    external_post_id: Optional[str]
    post_url: Optional[str]
    title: Optional[str]
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Analytics
# ─────────────────────────────────────────────
class AnalyticsSummary(BaseModel):
    total_views: int
    total_likes: int
    total_comments: int
    total_shares: int
    total_clips: int
    total_posts: int
    avg_engagement_rate: float
    best_performing_clip: Optional[ClipOut]
    platform_breakdown: dict


class UsageOut(BaseModel):
    month: str
    clips_generated: int
    clips_remaining: int
    channels_connected: int
    channels_remaining: int
    max_clips: int
    max_channels: int
