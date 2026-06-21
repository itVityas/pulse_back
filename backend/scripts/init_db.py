#!/usr/bin/env python
import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Try to activate virtual environment if not already activated
venv_path = project_root / '.venv'
if venv_path.exists():
    # Add virtual environment site-packages to path
    site_packages = venv_path / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
    if site_packages.exists():
        sys.path.insert(0, str(site_packages))

from alembic.config import Config
from alembic import command
from settings.database import get_session, engine 
from fixtures.load_fixtures import FixtureLoad


def do_run_migrations(connection, alembic_cfg):
    """Синхронная функция для выполнения миграций внутри контекста соединения"""
    alembic_cfg.attributes['connection'] = connection
    command.upgrade(alembic_cfg, "head")


async def run_migrations():
    """Запуск миграций Alembic"""
    print("🔄 Running migrations...")
    alembic_cfg = Config("alembic.ini")
    async with engine.begin() as conn:
        await conn.run_sync(do_run_migrations, alembic_cfg)
    print("✅ Migrations completed")


async def load_fixtures():
    """Загрузка фикстур"""
    print("📦 Loading fixtures...")
    async for session in get_session():
        await FixtureLoad(session).load_all_fixtures(Path(Path.cwd(), 'src/fixtures/'))
    print("✅ Fixtures loaded")


async def init_database():
    """Полная инициализация базы данных"""
    try:
        # 1. Запускаем миграции
        await run_migrations()

        # 2. Загружаем фикстуры
        await load_fixtures()

        print("🎉 Database initialization completed successfully!")

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(init_database())
