from celery_app.celery_app import celery_app



@celery_app.task
def update_currency_rates_task():
    print(1)
