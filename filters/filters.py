import re
from datetime import date
from typing import Literal

from aiogram.filters import BaseFilter
from aiogram.types import Message


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


class IsCorrectExpenseNameFilter(BaseFilter):
    async def __call__(self, message: Message) -> dict[Literal["expense_name"], str]:
        expense_name_pattern = r"[\w+\s]+"
        if re.fullmatch(expense_name_pattern, message.text) and len(message.text) < 50:
            return {"expense_name": message.text.strip().capitalize()}
        return False


class IsCorrectCostFilter(BaseFilter):
    async def __call__(self, message: Message) -> dict[Literal["cost"], float]:
        try:
            cost = float(message.text.replace(",", "."))
            return {"cost": cost}
        except:
            pass
        return False


class IsCorrectAmountFilter(BaseFilter):
    async def __call__(self, message: Message) -> dict[Literal["amount"], int]:
        if message.text.isdigit():
            return {"amount": int(message.text)}
        return False


class IsCorrectCreatedDateFilter(BaseFilter):
    async def __call__(self, message: Message) -> dict[Literal["created_date"] : date]:
        try:
            day, month, year = message.text.replace("-", ".").split(".")
            return {"created_date": date(int(year), int(month), int(day))}
        except:
            pass
        return False


class IsCorrectComment(BaseFilter):
    async def __call__(self, message: Message) -> dict[Literal["comment"] : str]:
        if len(message.text) < 50:
            return {"comment": message.text}
        return False
