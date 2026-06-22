from celery_app.celery_app import celery_app
from celery_app.tasks import update_currency_rates_task

__all__ = ("celery_app", "update_currency_rates_task")
