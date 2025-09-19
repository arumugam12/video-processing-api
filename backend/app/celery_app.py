from celery import Celery
from .config import settings


celery_app = Celery(
    "video_tasks",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(task_track_started=True, result_expires=3600)

# Import tasks to register them
from . import tasks  # noqa: F401



