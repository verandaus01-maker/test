"""
Celery Application
Background task processing for scraping, enrichment, and exports
"""

from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "leadscaper",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Task routes
celery_app.conf.task_routes = {
    'app.workers.scraping_tasks.*': {'queue': 'scraping'},
    'app.workers.enrichment_tasks.*': {'queue': 'enrichment'},
    'app.workers.export_tasks.*': {'queue': 'exports'},
}

# Periodic tasks (Celery Beat schedule)
celery_app.conf.beat_schedule = {
    'cleanup-old-exports': {
        'task': 'app.workers.maintenance_tasks.cleanup_old_exports',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'update-lead-scores': {
        'task': 'app.workers.scoring_tasks.update_all_lead_scores',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
    'check-scheduled-jobs': {
        'task': 'app.workers.scraping_tasks.check_scheduled_jobs',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks([
    'app.workers.scraping_tasks',
    'app.workers.enrichment_tasks',
    'app.workers.export_tasks',
    'app.workers.scoring_tasks',
    'app.workers.maintenance_tasks',
])
