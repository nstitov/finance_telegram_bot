import logging

from aiogram import Router
from aiogram.types import Message

router = Router()
logger = logging.getLogger(__name__)


@router.message()
async def process_random_update(message: Message, i18n: dict[str, str]):
    """Handler to answer random message without any command.

    Args:
        message (Message): update with message with incorrect transaction from user
        i18n (dict[str, str]): dict with lexicon depends on user language settings
    """
    logger.info(f"User {message.from_user.id} sent incorrect message.")
    await message.answer(text=i18n["incorrect_message"])
