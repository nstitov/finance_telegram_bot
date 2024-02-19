import re
from typing import Literal

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message


class IsCorrectTransaction(BaseFilter):
    async def __call__(
        self, message: Message
    ) -> bool | dict[Literal["expense_name", "cost"], str | float]:
        transaction_pattern = r"[\w+\s]+?\d+[.,]?\d*?"
        if re.fullmatch(transaction_pattern, message.text):
            *expense_name, cost = message.text.split()
            cost = float(cost.replace(",", "."))
            transaction = {
                "expense_name": " ".join(expense_name).capitalize(),
                "cost": cost,
            }
            return transaction
        return False


class IsCorrectCategoryName(BaseFilter):
    async def __call__(self, message: Message) -> dict[Literal["category_name"], str]:
        category_pattern = r"[\w+\s]+"
        if re.fullmatch(category_pattern, message.text) and len(message.text) < 50:
            return {"category_name": message.text.strip().capitalize()}
        return False
