import asyncio

import pytest
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from envparse import env as environment
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext import asyncio as sa_asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text


@pytest.fixture(scope="session", autouse=True)
def env():
    environment.read_envfile()

    return environment


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
def test_db_url(env):
    db_url = make_url(env("SQLALCHEMY_DATABASE_URI"))
    return db_url.set(database=f"{db_url.database}_test")


@pytest.fixture(scope="session")
def sys_db_url(test_db_url):
    """
    Template DB (postgres, sys1 or sys0).
    Use it only to create temporal DB for testing.
    """
    return test_db_url.set(database="postgres")


@pytest.fixture(scope="session")
async def create_db_if_not_exists(test_db_url, sys_db_url, event_loop):
    sys_connectable = create_async_engine(sys_db_url, isolation_level="AUTOCOMMIT")
    async with sys_connectable.connect() as sys_connection:
        exists = await sys_connection.scalar(
            text(
                f"SELECT 1 FROM pg_database WHERE " f"datname='{test_db_url.database}'"
            )
        )
        if not exists:
            await sys_connection.execute(
                text(
                    f'CREATE DATABASE "{test_db_url.database}" '
                    f'OWNER "{test_db_url.username}"'
                )
            )


@pytest.fixture(scope="session")
def get_engine(test_db_url, create_db_if_not_exists):
    return lambda: create_async_engine(test_db_url)


@pytest.fixture(scope="session")
def run_migrations(get_engine):
    """
    Run online migrations from env.py file.
    This method has its own event loop under the hood.
    """

    alembic_config = AlembicConfig("alembic.ini")
    alembic_config.attributes["engine"] = get_engine()
    alembic_upgrade(alembic_config, "head")


@pytest.fixture(scope="session")
async def connection(get_engine):
    """
    Run online migrations from env.py file.
    This method has its own event loop under the hood.
    """

    async with get_engine().connect() as connect:
        yield connect


@pytest.fixture
async def session(mocker, connection, run_migrations):
    transaction = await connection.begin()
    session = sessionmaker(class_=sa_asyncio.AsyncSession)(bind=connection)

    mocker.patch("sqlalchemy.orm.session.sessionmaker.__call__", return_value=session)

    yield session

    await session.close()
    await transaction.rollback()
