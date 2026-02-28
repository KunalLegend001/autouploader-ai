"""
Database Models
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, Enum as SAEnum, JSON, BigInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────
class PlatformEnum(str, enum.Enum):
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REELS = "instagram_reels"
    TIKTOK = "tiktok"
    FACEBOOK_REELS = "facebook_reels"


class PostStatusEnum(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    UPLOADING = "uploading"
    PUBLISHED = "published"
    FAILED = "failed"


class ClipStatusEnum(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class ChannelPlatformEnum(str, enum.Enum):
    YOUTUBE = "youtube"


# ─────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    plan = Column(String(50), default="free")  # free, pro, enterprise
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    channels = relationship("Channel", back_populates="user", cascade="all, delete-orphan")
    clips = relationship("Clip", back_populates="user", cascade="all, delete-orphan")
    usage = relationship("UsageRecord", back_populates="user", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# Channels
# ─────────────────────────────────────────────
class Channel(Base):
    __tablename__ = "channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(SAEnum(ChannelPlatformEnum), nullable=False)
    external_channel_id = Column(String(255), nullable=False)
    channel_name = Column(String(255), nullable=False)
    channel_url = Column(String(500))
    thumbnail_url = Column(String(500))
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expiry = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="channels")
    source_videos = relationship("SourceVideo", back_populates="channel", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# Source Videos
# ─────────────────────────────────────────────
class SourceVideo(Base):
    __tablename__ = "source_videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("channels.id", ondelete="SET NULL"), nullable=True)
    external_video_id = Column(String(255), nullable=False)
    title = Column(String(500))
    description = Column(Text)
    duration_seconds = Column(Integer)
    thumbnail_url = Column(String(500))
    video_url = Column(String(500))
    local_path = Column(String(1000))
    transcript = Column(Text)
    published_at = Column(DateTime(timezone=True))
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    channel = relationship("Channel", back_populates="source_videos")
    clips = relationship("Clip", back_populates="source_video", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# Clips
# ─────────────────────────────────────────────
class Clip(Base):
    __tablename__ = "clips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_video_id = Column(UUID(as_uuid=True), ForeignKey("source_videos.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(500))
    description = Column(Text)
    transcript_segment = Column(Text)
    start_time = Column(Float)  # seconds
    end_time = Column(Float)    # seconds
    duration = Column(Float)    # seconds
    viral_score = Column(Float, default=0.0)  # AI score 0-100
    status = Column(SAEnum(ClipStatusEnum), default=ClipStatusEnum.PENDING)
    local_path = Column(String(1000))
    s3_url = Column(String(1000))
    thumbnail_url = Column(String(500))
    has_captions = Column(Boolean, default=False)
    has_broll = Column(Boolean, default=False)
    is_vertical = Column(Boolean, default=False)
    ai_tags = Column(JSON, default=list)  # ["motivation", "success", ...]
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="clips")
    source_video = relationship("SourceVideo", back_populates="clips")
    posts = relationship("Post", back_populates="clip", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# Posts (auto-posting records)
# ─────────────────────────────────────────────
class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clip_id = Column(UUID(as_uuid=True), ForeignKey("clips.id", ondelete="CASCADE"), nullable=False)
    platform = Column(SAEnum(PlatformEnum), nullable=False)
    status = Column(SAEnum(PostStatusEnum), default=PostStatusEnum.PENDING)
    external_post_id = Column(String(255))  # ID from the platform
    post_url = Column(String(500))
    title = Column(String(500))
    description = Column(Text)
    hashtags = Column(JSON, default=list)
    scheduled_at = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    celery_task_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    clip = relationship("Clip", back_populates="posts")
    analytics = relationship("PostAnalytics", back_populates="post", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# Analytics
# ─────────────────────────────────────────────
class PostAnalytics(Base):
    __tablename__ = "post_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    platform = Column(SAEnum(PlatformEnum), nullable=False)
    views = Column(BigInteger, default=0)
    likes = Column(BigInteger, default=0)
    comments = Column(BigInteger, default=0)
    shares = Column(BigInteger, default=0)
    watch_time_seconds = Column(BigInteger, default=0)
    followers_gained = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("Post", back_populates="analytics")


# ─────────────────────────────────────────────
# Usage tracking (rate limiting)
# ─────────────────────────────────────────────
class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    month = Column(String(7), nullable=False)  # "2026-02"
    clips_generated = Column(Integer, default=0)
    channels_connected = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    storage_bytes = Column(BigInteger, default=0)

    user = relationship("User", back_populates="usage")
