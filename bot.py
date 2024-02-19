import asyncio
import logging
import logging.config
import os

import yaml
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage

if not os.path.exists("Logs"):
    os.makedirs("Logs")

if __name__ == "__main__":
    with open("config_data/logging_config.yaml", "rt") as f:
        logging_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config)

from config_data.config import config
from handlers.command_handlers import router as default_commands_router
from handlers.user_hanlders import router as user_router
from keyboards.set_menu import set_main_menu
from lexicon.lexicon import translations
from middlewares.outer_middlewares import TranslatorMiddleware

logger = logging.getLogger("bot")


async def main():
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")

    dp = Dispatcher(storage=MemoryStorage(), _translations=translations)
    dp.message.filter(F.chat.type == "private")
    dp.message.outer_middleware(TranslatorMiddleware())
    dp.callback_query.outer_middleware(TranslatorMiddleware())

    dp.include_router(default_commands_router)
    dp.include_router(user_router)

    await set_main_menu(bot)

    print("Bot started.")
    await dp.start_polling(bot)


asyncio.run(main())
