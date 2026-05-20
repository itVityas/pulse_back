import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from service.security import hash_password
from model.user import User
from model.currency import Currency
from model.category import Category
from model.matrix_type import MatrixType
from model.os import OS
from model.screen_resolution import ScreenResolution
from model.shop import Shop


class FixtureLoad:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def load_users(self, fixture_file: Path):
        if not fixture_file.exists():
            raise FileNotFoundError(f"Fixture file {fixture_file} not found")
        with open(fixture_file, 'r') as file:
            fixture_data = json.load(file)

        for line in fixture_data:
            username = line.get('username')
            password = line.get('password')
            is_active = line.get('is_active')
            is_admin = line.get('is_admin')

            result = await self.session.execute(select(User).where(User.username == username))
            existing_user = result.scalar_one_or_none()

            if not existing_user:
                new_user = User(
                    username=username,
                    password=hash_password(password),
                    is_active=is_active,
                    is_admin=is_admin
                )
                self.session.add(new_user)
                await self.session.commit()

    async def load_currencies(self, fixture_file: Path):
        if not fixture_file.exists():
            raise FileNotFoundError(f"Fixture file {fixture_file} not found")
        with open(fixture_file, 'r') as file:
            fixture_data = json.load(file)

        for line in fixture_data:
            name = line.get('name')

            result = await self.session.execute(select(Currency).where(Currency.name == name))
            existing_currency = result.scalar_one_or_none()

            if not existing_currency:
                new_currency = Currency(
                    name=name
                )
                self.session.add(new_currency)
                await self.session.commit()

    async def load_categories(self, fixture_file: Path):
        if not fixture_file.exists():
            raise FileNotFoundError(f"Fixture file {fixture_file} not found")
        with open(fixture_file, 'r') as file:
            fixture_data = json.load(file)

        for line in fixture_data:
            name = line.get('name')

            result = await self.session.execute(select(Category).where(Category.name == name))
            existing_category = result.scalar_one_or_none()

            if not existing_category:
                new_category = Category(
                    name=name
                )
                self.session.add(new_category)
                await self.session.commit()

    async def load_matrix_types(self, fixture_file: Path):
        if not fixture_file.exists():
            raise FileNotFoundError(f"Fixture file {fixture_file} not found")
        with open(fixture_file, 'r') as file:
            fixture_data = json.load(file)

        for line in fixture_data:
            name = line.get('name')

            result = await self.session.execute(select(MatrixType).where(MatrixType.name == name))
            existing_matrix_type = result.scalar_one_or_none()

            if not existing_matrix_type:
                new_matrix_type = MatrixType(
                    name=name
                )
                self.session.add(new_matrix_type)
                await self.session.commit()

    async def load_os(self, fixture_file: Path):
        if not fixture_file.exists():
            raise FileNotFoundError(f"Fixture file {fixture_file} not found")
        with open(fixture_file, 'r') as file:
            fixture_data = json.load(file)

        for line in fixture_data:
            name = line.get('name')

            result = await self.session.execute(select(OS).where(OS.name == name))
            existing_os = result.scalar_one_or_none()

            if not existing_os:
                new_os = OS(
                    name=name
                )
                self.session.add(new_os)
                await self.session.commit()

    async def load_shop(self, fixture_file: Path):
        if not fixture_file.exists():
            raise FileNotFoundError(f"Fixture file {fixture_file} not found")
        with open(fixture_file, 'r') as file:
            fixture_data = json.load(file)

        for line in fixture_data:
            name = line.get('name')
            url = line.get('url')

            result = await self.session.execute(select(Category).where(Category.name == name))
            existing_shop = result.scalar_one_or_none()

            if not existing_shop:
                new_shop = Shop(
                    name=name,
                    url=url,
                )
                self.session.add(new_shop)
                await self.session.commit()

    async def load_screen_resolutions(self, fixture_file: Path):
        if not fixture_file.exists():
            raise FileNotFoundError(f"Fixture file {fixture_file} not found")
        with open(fixture_file, 'r') as file:
            fixture_data = json.load(file)

        for line in fixture_data:
            name = line.get('name')
            width = line.get('width')
            height = line.get('height')

            result = await self.session.execute(select(ScreenResolution).where(ScreenResolution.name == name))
            existing_screen_resolution = result.scalar_one_or_none()

            if not existing_screen_resolution:
                new_screen_resolution = ScreenResolution(
                    name=name,
                    width=width,
                    height=height
                )
                self.session.add(new_screen_resolution)
                await self.session.commit()

    async def load_all_fixtures(self, fixtures_dir: Path):
        fixtures_files = fixtures_dir.glob('*.json')
        for fixture_file in fixtures_files:
            if 'user' in fixture_file.name:
                await self.load_users(fixture_file)
            if 'currency' in fixture_file.name:
                await self.load_currencies(fixture_file)
            if 'category' in fixture_file.name:
                await self.load_categories(fixture_file)
            if 'matrix_type' in fixture_file.name:
                await self.load_matrix_types(fixture_file)
            if 'os' in fixture_file.name:
                await self.load_os(fixture_file)
            if 'screen_resolution' in fixture_file.name:
                await self.load_screen_resolutions(fixture_file)
            if 'shop' in fixture_file.name:
                await self.load_shop(fixture_file)
