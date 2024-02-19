from datetime import date
from typing import Literal

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.db_requests import (
    add_category_to_db,
    add_expense_to_db,
    get_expense_category_name_from_db,
)
from filters.filters import IsCorrectCategoryName, IsCorrectTransaction
from handlers.command_handlers import FSMAddTransaction
from keyboards.cbdata import CategoriesCallbackFactory
from keyboards.kb_users import (
    create_categories_keyboard,
    create_confirm_transaction_keyboard,
)

router = Router()


@router.message(StateFilter(FSMAddTransaction.fill_transaction))
@router.message(IsCorrectTransaction())
async def process_correct_transaction(
    message: Message,
    i18n: dict[str, str],
    state: FSMContext,
    expense_name: str,
    cost: float,
):
    created_date = date.today().isoformat()
    await state.update_data(
        expense_name=expense_name,
        cost=cost,
        created_date=created_date,
        amount=1,
        comment=None,
    )

    category_name = get_expense_category_name_from_db(
        message.from_user.id,
        expense_name,
    )
    if not category_name:
        await state.set_state(FSMAddTransaction.add_new_expense)
        await message.answer(
            text=i18n["transaction_no_expense"],
            reply_markup=create_categories_keyboard(
                message.from_user.id, i18n["transaction_add_new_category_callback"]
            ),
        )
    else:
        await state.set_state(FSMAddTransaction.confirm_transaction)
        await message.answer(
            text=i18n["transaction_info"].format(
                expense_name=expense_name,
                category_name=category_name,
                cost=cost,
                amount=1,
                created_date=created_date,
                comment="",
            ),
            reply_markup=create_confirm_transaction_keyboard(
                i18n["transaction_confirm"],
                i18n["transaction_correct"],
                i18n["transaction_cancel"],
            ),
        )


@router.message(StateFilter(FSMAddTransaction.fill_transaction))
async def process_incorrect_transaction(message: Message, i18n: dict[str, str]):
    await message.answer(text=i18n["transaction_incorrect_format"])


@router.callback_query(StateFilter(FSMAddTransaction.add_new_expense))
@router.callback_query(CategoriesCallbackFactory.filter())
async def process_add_expense_category(
    callback: CallbackQuery, i18n: dict[str, str], state: FSMContext
):
    category_name = callback.data.split(":")[-1]
    if category_name == i18n["transaction_add_new_category_callback"]:
        await state.set_state(FSMAddTransaction.add_new_category)
        await callback.message.answer(text=i18n["transaction_add_new_category"])
    else:
        transaction_data = await state.get_data()

        add_expense_to_db(
            callback.from_user.id,
            category_name,
            transaction_data["expense_name"],
        )
        await state.set_state(FSMAddTransaction.confirm_transaction)
        await callback.message.answer(
            text=i18n["transaction_expense_added"].format(
                expense_name=transaction_data["expense_name"],
                category_name=category_name,
            )
            + i18n["transaction_info"].format(
                expense_name=transaction_data["expense_name"],
                category_name=category_name,
                cost=transaction_data["cost"],
                amount=transaction_data["amount"],
                created_date=transaction_data["created_date"],
                comment=transaction_data["comment"],
            ),
            reply_markup=create_confirm_transaction_keyboard(
                i18n["transaction_confirm"],
                i18n["transaction_correct"],
                i18n["transaction_cancel"],
            ),
        )
    await callback.answer()


@router.message(StateFilter(FSMAddTransaction.add_new_category))
@router.message(IsCorrectCategoryName())
async def process_correct_category_name_transaction(
    message: Message, i18n: dict[str, str], state: FSMContext, category_name: str
):
    add_category_to_db(message.from_user.id, category_name)
    transaction_data = await state.get_data()
    add_expense_to_db(
        message.from_user.id, category_name, transaction_data["expense_name"]
    )
    await state.set_state(FSMAddTransaction.confirm_transaction)
    await message.answer(
        text=i18n["transaction_category_added"]
        + i18n["transaction_expense_added"]
        + i18n["transaction_info"].format(
            expense_name=transaction_data["expense_name"],
            category_name=category_name,
            cost=transaction_data["cost"],
            amount=transaction_data["amount"],
            created_date=transaction_data["created_date"],
            comment=transaction_data["comment"],
        ),
        reply_markup=create_confirm_transaction_keyboard(
            i18n["confirm_transaction"],
            i18n["correct_transaction"],
            i18n["cancel_transaction"],
        ),
    )


@router.message(StateFilter(FSMAddTransaction.add_new_category))
async def process_incorrect_category_name_transaction(
    message: Message, i18n: dict[str, str]
):
    await message.answer(
        text=i18n["transaction_incorrect_category_name"]
        + i18n["transaction_add_new_category"]
    )
