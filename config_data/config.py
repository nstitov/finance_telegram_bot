from dataclasses import dataclass

from environs import Env


@dataclass(slots=True, frozen=True)
class TgBot:
    token: str
    storage: str


@dataclass(slots=True, frozen=True)
class Database:
    postgres_dsn: str


@dataclass(slots=True, frozen=True)
class Redis:
    redis_dsn: str


@dataclass(slots=True, frozen=True)
class Config:
    tg_bot: TgBot
    db: Database
    redis: Redis


env = Env()
env.read_env()
config = Config(
    tg_bot=TgBot(
        token=env("BOT_TOKEN"),
        storage=env("BOT_FSM_STORAGE"),
    ),
    db=Database(postgres_dsn=env("POSTGRES_DSN")),
    redis=Redis(redis_dsn=env("REDIS_DSN")),
)
