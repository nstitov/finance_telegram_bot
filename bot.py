import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config_data.config import config
from handlers.change_transaction_handlers import router as change_transaction_router
from handlers.command_handlers import router as default_commands_router
from handlers.ignore_handlers import router as ignore_router
from handlers.transactions_handlers import router as transactions_router
from keyboards.set_menu import set_main_menu
from lexicon.lexicon import translations
from middlewares.outer_middlewares import TranslatorMiddleware

logger = logging.getLogger("bot")


async def main():
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    dp = Dispatcher(storage=MemoryStorage(), _translations=translations)
    dp.message.filter(F.chat.type == "private")
    dp.message.outer_middleware(TranslatorMiddleware())
    dp.callback_query.outer_middleware(TranslatorMiddleware())

    dp.include_router(default_commands_router)
    dp.include_router(transactions_router)
    dp.include_router(change_transaction_router)
    dp.include_router(ignore_router)

    await set_main_menu(bot)

    print("Bot started.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    import __init__

    asyncio.run(main())
