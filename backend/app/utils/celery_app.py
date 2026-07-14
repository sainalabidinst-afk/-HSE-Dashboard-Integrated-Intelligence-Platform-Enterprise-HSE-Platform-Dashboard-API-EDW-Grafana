"""
Celery application configuration for async tasks.
Used for: alert sending, report generation, data sync
"""

import os
from celery import Celery
from app.config import settings

# Initialize Celery
celery_app = Celery(
    "hse_tasks",
    broker=settings.REDIS_URL or "redis://localhost:6379/0",
    backend=settings.REDIS_URL or "redis://localhost:6379/0",
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Jakarta",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
)


# Example tasks
@celery_app.task(bind=True)
def send_alert_email(self, recipient: str, subject: str, body: str):
    """Send alert email (implement SMTP logic here)."""
    # Implementation depends on email provider
    pass


@celery_app.task(bind=True)
def generate_pdf_report(self, report_type: str, site_id: str, period_days: int):
    """Generate PDF report asynchronously."""
    # Implementation with ReportLab or WeasyPrint
    pass
