from celery_app import celery_app
from settings.database import get_session
from repository.currency import CurrencyData


@celery_app.task
def update_currency_rates_task():
    import asyncio

    async def _run():
        async for session in get_session():
            curerrensy = await CurrencyData(session).get_multi()
            for i in curerrensy:
                print(i)
            break

    asyncio.run(_run())
