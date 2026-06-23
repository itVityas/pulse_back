from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from settings.config import database_config, project_config


engine = create_async_engine(
    database_config.get_url(),
    echo=project_config.debug,
    pool_size=database_config.db_pool_size,
    max_overflow=database_config.db_max_overflow,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncSession:
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception:
        await session.rollback()
        raise
