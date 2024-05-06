from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, User

from bot.database.db_requests import get_user_info


class GetUserIDMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        """Middleware to get local user ID from database."""
        user: User = data.get("event_from_user")
        user_info = await get_user_info(data["async_session"], user.id)
        if not user_info:
            await event.answer(text="Сначала необходимо отправить боту команду /start")
        else:
            data["local_user_id"] = user_info.user_id
            return await handler(event, data)
