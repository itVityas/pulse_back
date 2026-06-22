from src.celery.celery_app import celery_app
from src.celery.tasks import update_currency_rates_task

__all__ = ("celery_app", "update_currency_rates_task")
