import pytest

from app.db import session_scope

pytestmark = pytest.mark.asyncio


async def test_engine_configured(env):
    async with session_scope() as session:
        assert str(session.bind.engine.url) == env("SQLALCHEMY_DATABASE_URI")
