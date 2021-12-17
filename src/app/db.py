from contextlib import asynccontextmanager

from envparse import env
from sqlalchemy.ext import asyncio as sa_asyncio
from sqlalchemy.orm import sessionmaker

env.read_envfile()


engine = sa_asyncio.create_async_engine(
    env("SQLALCHEMY_DATABASE_URI"), pool_recycle=1800
)
AsyncSession = sessionmaker(bind=engine, class_=sa_asyncio.AsyncSession)


@asynccontextmanager
async def session_scope():
    """Provide a transactional scope around a series of operations."""
    async_session = AsyncSession()
    try:
        yield async_session
        await async_session.commit()
    except Exception:
        await async_session.rollback()
        raise
    finally:
        await async_session.close()
