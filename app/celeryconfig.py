from celery.schedules import crontab
from app.core import settings


broker_url = settings.CELERY_BROKER_URL

result_backend = settings.CELERY_RESULT_BACKEND

timezone = settings.CELERY_TIME_ZONE
task_serializer = "json"
accept_content = ["json"]
worker_prefetch_multiplier = 1
task_acks_late = True
beat_schedule = {
    "send_reminders": {
        "task": "send_email_verification_reminders",
        "args": (),
        "kwargs": {},
        "schedule": crontab(minute="0", hour="9", day_of_week="saturday"),
    },
}
