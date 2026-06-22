from celery import Celery
from celery.schedules import crontab


celery_app = Celery(
    'worker',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

celery_app.conf.imports = ('src.celery.tasks',)

celery_app.conf.beat_schedule = {
    'update-currency-rate': {
        'task': 'src.celery.tasks.update_currency_rates_task',
        'schedule': crontab(minute='*/1')
    }
}

celery_app.conf.timezone = 'UTC'
