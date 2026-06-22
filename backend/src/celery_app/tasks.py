from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from celery_app.celery_app import celery_app
from settings.config import database_config
from repository.currency import CurrencyData


@celery_app.task
def update_currency_rates_task():
    import asyncio

    async def _run():
        print(database_config.get_url())
        engine = create_async_engine(database_config.get_url())
        session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        curerrensy = CurrencyData(session).get_multi()
        for i in curerrensy:
            print(i)

    asyncio.run(_run())
