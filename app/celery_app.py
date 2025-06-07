from celery import Celery

celery_app = Celery("app")
celery_app.config_from_object("app.celeryconfig")
import app.jobs.email_jobs.email_jobs
import app.jobs.schedules.schedules

celery_app.autodiscover_tasks(["app.jobs.email_jobs", "app.jobs.schedules"])
