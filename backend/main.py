"""
AutoUploader AI Agent - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio

from app.routers import auth, channels, clips, analytics, posting, users
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global readiness flag – set to True after DB initialises
_db_ready = False


async def _init_db_with_retry(max_attempts: int = 10, delay: float = 3.0):
    """Try to init the DB with retries so Railway startup doesn't crash."""
    global _db_ready
    from app.database import init_db

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"🗄️  DB init attempt {attempt}/{max_attempts}...")
            await init_db()
            _db_ready = True
            logger.info("✅ Database initialised successfully")
            return
        except Exception as exc:
            logger.warning(f"⚠️  DB not ready (attempt {attempt}): {exc}")
            if attempt < max_attempts:
                await asyncio.sleep(delay * attempt)   # back-off: 3s, 6s, 9s…
    logger.error("❌ Could not connect to DB after all retries – running without DB")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Non-fatal startup: DB init retries in background so /health passes immediately."""
    logger.info("🚀 Starting AutoUploader AI Agent...")
    # Run DB init in background so the HTTP server starts immediately
    # (Railway health check can pass right away while the DB warms up)
    asyncio.create_task(_init_db_with_retry())
    yield
    logger.info("🛑 Shutting down AutoUploader AI Agent...")


app = FastAPI(
    title="AutoUploader AI Agent API",
    description="AI-powered video clip generation and auto-posting system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.(vercel|railway)\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(channels.router, prefix="/api/v1/channels", tags=["Channels"])
app.include_router(clips.router, prefix="/api/v1/clips", tags=["Clips"])
app.include_router(posting.router, prefix="/api/v1/posting", tags=["Posting"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


@app.get("/")
async def root():
    return {
        "name": "AutoUploader AI Agent",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Always returns 200 – used by Railway to confirm the process is alive."""
    return {"status": "healthy"}


@app.get("/ready")
async def readiness_check():
    """Returns 200 only after DB is connected."""
    if _db_ready:
        return {"status": "ready", "db": "connected"}
    return {"status": "starting", "db": "connecting"}, 503
