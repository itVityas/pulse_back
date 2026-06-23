from datetime import date, timedelta

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from celery_app import celery_app
from settings.config import database_config
from service.currency_upload import get_currency_from_nbrb


@celery_app.task
def update_currency_rates_task():
    import asyncio

    async def _run():
        engine = create_async_engine(database_config.get_url())
        session_maker: AsyncSession = async_sessionmaker(engine, expire_on_commit=False)
        async with session_maker() as session:
            yesterday = date.today() - timedelta(days=1)
            await get_currency_from_nbrb(session, yesterday)

    asyncio.run(_run())
