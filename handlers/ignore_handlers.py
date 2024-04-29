import logging

from aiogram import Router
from aiogram.types import Message

router = Router()
logger = logging.getLogger(__name__)


@router.message()
async def process_random_update(message: Message, i18n: dict[str, str]):
    logger.info(f"User {message.from_user.id} sent incorrect message.")
    await message.answer(text=i18n["incorrect_message"])
