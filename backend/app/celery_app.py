"""
Celery Worker — Background task queue
"""

from celery import Celery
from app.config import settings

celery_app = Celery(
    "autouploader",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.clip_tasks",
        "app.tasks.posting_tasks",
        "app.tasks.analytics_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # Process one task at a time (video heavy)
    task_routes={
        "app.tasks.clip_tasks.*": {"queue": "clips"},
        "app.tasks.posting_tasks.*": {"queue": "posting"},
        "app.tasks.analytics_tasks.*": {"queue": "analytics"},
    },
    beat_schedule={
        # Poll analytics every hour
        "sync-analytics": {
            "task": "app.tasks.analytics_tasks.sync_all_analytics",
            "schedule": 3600,
        },
        # Check for new videos every 30 minutes
        "check-new-videos": {
            "task": "app.tasks.clip_tasks.check_new_videos",
            "schedule": 1800,
        },
    },
)
