from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class TranslatorMiddleware(BaseMiddleware):
    """Middleware to get lexicon dict depends on user telegram language settings."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User = data.get("event_from_user")

        if not user:
            return await handler(event, data)

        user_lang = user.language_code
        translations: dict = data.get("_translations")

        i18n = translations.get(user_lang)
        if not i18n:
            data["i18n"] = translations[translations["default"]]
        else:
            data["i18n"] = i18n

        return await handler(event, data)


class DbSessionMiddleware(BaseMiddleware):
    """Middleware to create session to database connection from session pool and
    transmit session to handler."""

    # TODO: add flags for handlers which required session to transmit session not to all
    # handlers

    def __init__(self, sessions_pool: async_sessionmaker[AsyncSession]):
        super().__init__()
        self.sessions_pool = sessions_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.sessions_pool() as session:
            data["session"] = session
            return await handler(event, data)
