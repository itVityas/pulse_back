from celery import Celery
from celery.schedules import crontab


celery_app = Celery(
    'worker',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery_app.conf.beat_schedule = {
    'update-currency_rate': {
        'task': 'tasks.update_currency_rates_task',
        'schedule': crontab(minute='*/10')
    }
}

celery_app.conf.timezone = 'UTC'
