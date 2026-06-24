from celery import Celery
from celery.schedules import crontab


celery_app = Celery(
    'worker',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

celery_app.conf.imports = ('celery_app.tasks',)

celery_app.conf.beat_schedule = {
    'update-currency-rate': {
        'task': 'celery_app.tasks.update_currency_rates_task',
        'schedule': crontab(hour=3, minute=0)
    }
}

celery_app.conf.timezone = 'UTC'
