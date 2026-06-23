from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from celery_app import celery_app
from settings.config import database_config
from repository.currency import CurrencyData


@celery_app.task
def update_currency_rates_task():
    import asyncio

    async def _run():
        engine = create_async_engine(database_config.get_url())
        session_maker: AsyncSession = async_sessionmaker(engine, expire_on_commit=False)
        async with session_maker() as session:
            curerrensy = await CurrencyData(session).get_multi()
            for i in curerrensy:
                print(i)

    asyncio.run(_run())
