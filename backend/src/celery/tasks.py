from .celery_app import celery_app


@celery_app.task
def update_currency_rates_task():
    import asyncio

    async def _run():
        print('Hello World!')
    asyncio.run(_run())
