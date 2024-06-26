import asyncio
import logging
import logging.config

from aiogram import Bot, Dispatcher, F
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.config_data.configreader import config
from bot.database.db_models import Base
from bot.handlers.change_transaction_handlers import router as change_transaction_router
from bot.handlers.command_handlers import router as default_commands_router
from bot.handlers.ignore_handlers import router as ignore_router
from bot.handlers.transactions_handlers import router as transactions_router
from bot.keyboards.set_menu import set_main_menu
from bot.lexicon.lexicon import translations
from bot.middlewares.outer_middlewares import DbSessionMiddleware, TranslatorMiddleware

logger = logging.getLogger("bot")


async def main():
    engine = create_async_engine(config.postgres_dsn, future=True, echo=False)
    db_pool = async_sessionmaker(engine, expire_on_commit=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    if config.bot_fsm_storage == "redis":
        dp = Dispatcher(
            storage=RedisStorage.from_url(config.redis_dsn),
            _translations=translations,
        )
    else:
        dp = Dispatcher(storage=MemoryStorage(), _translations=translations)

    dp.message.filter(F.chat.type == "private")

    dp.message.outer_middleware(DbSessionMiddleware(db_pool))
    dp.message.outer_middleware(TranslatorMiddleware())
    dp.callback_query.outer_middleware(DbSessionMiddleware(db_pool))
    dp.callback_query.outer_middleware(TranslatorMiddleware())

    dp.include_router(default_commands_router)
    dp.include_router(transactions_router)
    dp.include_router(change_transaction_router)
    dp.include_router(ignore_router)

    await set_main_menu(bot)

    print("Bot started.")
    await dp.start_polling(bot)
    print("Bot finished.")


asyncio.run(main())
