from contextlib import asynccontextmanager

from envparse import env
from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

env.read_envfile()

engine = create_async_engine(env("SQLALCHEMY_DATABASE_URI"), pool_recycle=1800)

AsyncSession = sessionmaker(bind=engine, class_=_AsyncSession)


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
