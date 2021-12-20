from app.db import session_scope
from app.models import ExampleModel


async def example_task(*args):
    async with session_scope() as session:
        session.add(ExampleModel())
