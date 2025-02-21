

from celery import Celery
from celery.schedules import crontab
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery
celery = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configure Celery
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Schedule periodic tasks
celery.conf.beat_schedule = {
    "process-data-quality": {
        "task": "app.jobs.tasks.process_data_quality",
        "schedule": crontab(minute="*/15")  # Every 15 minutes
    },
    "cleanup-expired-data": {
        "task": "app.jobs.tasks.cleanup_expired_data",
        "schedule": crontab(hour="0", minute="0")  # Daily at midnight
    }
}

