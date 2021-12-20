from arq import cron
from arq.connections import RedisSettings
from envparse import env

from app.tasks import example_task

env.read_envfile()


class ExampleWorkerSettings:
    functions = [example_task]
    redis_settings = RedisSettings.from_dsn(env("ARQ_BACKEND"))
    cron_jobs = [cron(example_task)]
