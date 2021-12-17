import pytest
from sqlalchemy import func
from sqlalchemy.future import select

from app.models import ExampleModel
from app.tasks import example_task

pytestmark = pytest.mark.asyncio


async def test_creates_new_entry(session):
    await example_task()

    count = (await session.execute(select(func.count(ExampleModel.id)))).scalar()
    assert count == 1


async def test_creates_new_entry_as_many_times_as_task_called(session):
    for _ in range(3):
        await example_task()

    count = (await session.execute(select(func.count(ExampleModel.id)))).scalar()
    assert count == 3
