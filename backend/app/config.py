"""
AutoUploader Configuration Settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AutoUploader AI Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION-USE-STRONG-SECRET"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS – explicit origins. Add your exact Vercel/Railway URLs here.
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://frontend-liard-zeta-46.vercel.app",
    ]

    # Suffix patterns for dynamic origin matching (e.g. preview deployments)
    ALLOWED_ORIGIN_SUFFIXES: List[str] = [
        ".vercel.app",
        ".railway.app",
    ]

    # Database – Railway provides postgresql://, we need postgresql+asyncpg://
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/autouploader"

    @property
    def async_database_url(self) -> str:
        """Always returns URL with the asyncpg driver scheme."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    WHISPER_MODEL: str = "whisper-1"

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "autouploader-clips"
    S3_BASE_URL: str = ""

    # YouTube API
    YOUTUBE_API_KEY: str = ""
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""

    # Meta (Facebook/Instagram) API
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    META_GRAPH_API_VERSION: str = "v18.0"

    # TikTok API
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""

    # Pexels (B-roll stock footage)
    PEXELS_API_KEY: str = ""

    # Pixabay (B-roll stock footage)
    PIXABAY_API_KEY: str = ""

    # FFmpeg path
    FFMPEG_PATH: str = "ffmpeg"
    FFPROBE_PATH: str = "ffprobe"

    # Clip generation limits
    MAX_CLIPS_PER_MONTH: int = 30
    MAX_CHANNELS_PER_USER: int = 3
    MAX_CLIP_DURATION_SECONDS: int = 90
    MIN_CLIP_DURATION_SECONDS: int = 20

    # Storage
    TEMP_DIR: str = "/tmp/autouploader"
    CLIPS_OUTPUT_DIR: str = "/tmp/autouploader/clips"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure temp directories exist
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.CLIPS_OUTPUT_DIR, exist_ok=True)
