import asyncio

import pytest
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from envparse import env as environment
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database


@pytest.fixture(scope="session", autouse=True)
def env():
    environment.read_envfile()

    return environment


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
async def engine(env):
    db_url = make_url(env("SQLALCHEMY_DATABASE_URI"))
    db_url = db_url.set(database=f"{db_url.database}_test")

    engine = create_async_engine(db_url)
    if not await database_exists(engine.url):
        await create_database(engine.url)

    yield engine

    await drop_database(engine.url)


@pytest.fixture(scope="session")
async def connection(engine):
    async with engine.connect() as connection:

        alembic_config = AlembicConfig("alembic.ini")
        alembic_config.attributes["connection"] = connection
        alembic_upgrade(alembic_config, "head")

        yield connection


@pytest.fixture
async def session(mocker, connection):
    transaction = await connection.begin()
    session = sessionmaker(class_=_AsyncSession)(bind=connection)

    mocker.patch("sqlalchemy.orm.session.sessionmaker.__call__", return_value=session)

    yield session

    session.close()
    await transaction.rollback()
