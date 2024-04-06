import logging
from datetime import date

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from filters.filters import (
    IsCorrectAmountFilter,
    IsCorrectComment,
    IsCorrectCostFilter,
    IsCorrectCreatedDateFilter,
    IsCorrectExpenseNameFilter,
)
from handlers.command_handlers import FSMAddTransaction
from keyboards.kb_users import create_confirm_transaction_keyboard


class FSMChangeTransaction(StatesGroup):
    change_expense_name = State()
    change_category = State()
    change_cost = State()
    change_amount = State()
    change_created_date = State()
    change_comment = State()


router = Router()
logger = logging.getLogger(__name__)


@router.message(
    StateFilter(FSMChangeTransaction.change_expense_name), IsCorrectExpenseNameFilter()
)
async def process_change_expense_name_transaction(
    message: Message, i18n: dict[str, str], expense_name: str, state: FSMContext
):
    await state.update_data(expense_name=expense_name)
    logger.debug("Expense name is corrected.")
    transaction_data = await state.get_data()
    await state.set_state(FSMAddTransaction.confirm_transaction)
    await message.answer(
        text=i18n["transaction_info"].format(
            expense_name=transaction_data["expense_name"],
            category_name=transaction_data["category_name"],
            cost=transaction_data["cost"],
            amount=transaction_data["amount"],
            created_date=transaction_data["created_date"],
            comment=(
                transaction_data["comment"]
                if transaction_data["comment"]
                else i18n["transaction_without_comment"]
            ),
        ),
        reply_markup=create_confirm_transaction_keyboard(
            i18n["transaction_confirm_button"],
            i18n["transaction_correct_button"],
            i18n["transaction_cancel_button"],
        ),
    )


@router.message(StateFilter(FSMChangeTransaction.change_expense_name))
async def process_change_incorrect_expense_name_transaction(
    message: Message, i18n: dict[str, str]
):
    logger.debug("Expense name has incorrect format.")
    await message.answer(text=i18n["transaction_incorrect_expense_name"])


@router.message(StateFilter(FSMChangeTransaction.change_cost), IsCorrectCostFilter())
async def process_change_cost_transaction(
    message: Message, i18n: dict[str, str], cost: float, state: FSMContext
):
    await state.update_data(cost=cost)
    logger.debug("Cost is corrected.")
    transaction_data = await state.get_data()
    await state.set_state(FSMAddTransaction.confirm_transaction)
    await message.answer(
        text=i18n["transaction_info"].format(
            expense_name=transaction_data["expense_name"],
            category_name=transaction_data["category_name"],
            cost=transaction_data["cost"],
            amount=transaction_data["amount"],
            created_date=transaction_data["created_date"],
            comment=(
                transaction_data["comment"]
                if transaction_data["comment"]
                else i18n["transaction_without_comment"]
            ),
        ),
        reply_markup=create_confirm_transaction_keyboard(
            i18n["transaction_confirm_button"],
            i18n["transaction_correct_button"],
            i18n["transaction_cancel_button"],
        ),
    )


@router.message(StateFilter(FSMChangeTransaction.change_cost))
async def process_change_incorrect_cost_transaction(
    message: Message, i18n: dict[str, str]
):
    logger.debug("Cost has incorrect format.")
    await message.answer(text=i18n["transaction_incorrect_cost"])


@router.message(
    StateFilter(FSMChangeTransaction.change_amount), IsCorrectAmountFilter()
)
async def process_change_amount_transaction(
    message: Message, i18n: dict[str, str], amount: int, state: FSMContext
):
    await state.update_data(amount=amount)
    logger.debug("Amount is corrected.")
    transaction_data = await state.get_data()
    await state.set_state(FSMAddTransaction.confirm_transaction)
    await message.answer(
        text=i18n["transaction_info"].format(
            expense_name=transaction_data["expense_name"],
            category_name=transaction_data["category_name"],
            cost=transaction_data["cost"],
            amount=transaction_data["amount"],
            created_date=transaction_data["created_date"],
            comment=(
                transaction_data["comment"]
                if transaction_data["comment"]
                else i18n["transaction_without_comment"]
            ),
        ),
        reply_markup=create_confirm_transaction_keyboard(
            i18n["transaction_confirm_button"],
            i18n["transaction_correct_button"],
            i18n["transaction_cancel_button"],
        ),
    )


@router.message(StateFilter(FSMChangeTransaction.change_amount))
async def process_change_incorrect_amount_transaction(
    message: Message, i18n: dict[str, str]
):
    logger.debug("Amount has incorrect format.")
    await message.answer(text=i18n["transaction_incorrect_amount"])


@router.message(
    StateFilter(FSMChangeTransaction.change_created_date), IsCorrectCreatedDateFilter()
)
async def process_change_created_date_transaction(
    message: Message, i18n: dict[str, str], created_date: date, state: FSMContext
):
    await state.update_data(created_date=created_date.strftime("%d.%m.%Y"))
    logger.debug("Created date is corrected.")
    transaction_data = await state.get_data()
    await state.set_state(FSMAddTransaction.confirm_transaction)
    await message.answer(
        text=i18n["transaction_info"].format(
            expense_name=transaction_data["expense_name"],
            category_name=transaction_data["category_name"],
            cost=transaction_data["cost"],
            amount=transaction_data["amount"],
            created_date=transaction_data["created_date"],
            comment=(
                transaction_data["comment"]
                if transaction_data["comment"]
                else i18n["transaction_without_comment"]
            ),
        ),
        reply_markup=create_confirm_transaction_keyboard(
            i18n["transaction_confirm_button"],
            i18n["transaction_correct_button"],
            i18n["transaction_cancel_button"],
        ),
    )


@router.message(StateFilter(FSMChangeTransaction.change_created_date))
async def process_change_incorrect_created_date_transaction(
    message: Message, i18n: dict[str, str]
):
    logger.debug("Created date has incorrect format.")
    await message.answer(text=i18n["transaction_incorrect_created_date"])


@router.message(StateFilter(FSMChangeTransaction.change_comment), IsCorrectComment())
async def process_change_comment_transaction(
    message: Message, i18n: dict[str, str], comment: str, state: FSMContext
):
    await state.update_data(comment=comment)
    logger.debug("Comment is corrected.")
    transaction_data = await state.get_data()
    await state.set_state(FSMAddTransaction.confirm_transaction)
    await message.answer(
        text=i18n["transaction_info"].format(
            expense_name=transaction_data["expense_name"],
            category_name=transaction_data["category_name"],
            cost=transaction_data["cost"],
            amount=transaction_data["amount"],
            created_date=transaction_data["created_date"],
            comment=(
                transaction_data["comment"]
                if transaction_data["comment"]
                else i18n["transaction_without_comment"]
            ),
        ),
        reply_markup=create_confirm_transaction_keyboard(
            i18n["transaction_confirm_button"],
            i18n["transaction_correct_button"],
            i18n["transaction_cancel_button"],
        ),
    )


@router.message(StateFilter(FSMChangeTransaction.change_comment))
async def process_change_incorrect_comment_transaction(
    message: Message, i18n: dict[str, str]
):
    logger.info("Comment has incorrect format.")
    await message.answer(text=i18n["transaction_incorrect_comment"])
