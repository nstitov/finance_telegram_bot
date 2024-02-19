import os
from dataclasses import dataclass

from environs import Env

from database.db_init import init_database

DATABASE_NAME = "finance.db"

if not os.path.exists(DATABASE_NAME):
    init_database(DATABASE_NAME)


@dataclass(slots=True, frozen=True)
class TgBot:
    token: str


@dataclass(slots=True, frozen=True)
class Config:
    tg_bot: TgBot


env = Env()
env.read_env()
config = Config(tg_bot=TgBot(token=env("BOT_TOKEN")))
