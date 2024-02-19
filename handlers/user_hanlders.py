import logging
from datetime import date

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from database.db_requests import add_transaction_to_db, get_expense_info_from_db
from filters.filters import IsCorrectCategoryName, IsCorrectTransaction
from handlers.command_handlers import FSMAddTransaction
from keyboards.cbdata import CategoriesCallbackFactory
from keyboards.kb_users import (
    create_categories_keyboard,
    create_confirm_transaction_keyboard,
)

router = Router()
logger = logging.getLogger(__name__)


@router.message(StateFilter(FSMAddTransaction.fill_transaction))
@router.message(IsCorrectTransaction())
async def process_correct_transaction(
    message: Message,
    i18n: dict[str, str],
    state: FSMContext,
    expense_name: str,
    cost: float,
):
    created_date = date.today()
    await state.update_data(
        expense_name=expense_name,
        cost=cost,
        created_date=created_date,
        amount=1,
        comment=None,
    )

    expense_info = get_expense_info_from_db(
        message.from_user.id,
        expense_name,
    )
    if not expense_info:
        await state.set_state(FSMAddTransaction.add_new_expense)
        logger.info(
            f"There is no expense {expense_name} in the database. FSM was transformed "
            f"to {await state.get_state()} state."
        )
        await message.answer(
            text=i18n["transaction_no_expense"],
            reply_markup=create_categories_keyboard(
                message.from_user.id, i18n["transaction_add_new_category_callback"]
            ),
        )
    else:
        await state.update_data(category_name=expense_info["category_name"])
        await state.set_state(FSMAddTransaction.confirm_transaction)
        logger.info(
            f"There is expense {expense_name} in the database. FSM was transformed to "
            f"{await state.get_state()} state."
        )
        await message.answer(
            text=i18n["transaction_info"].format(
                expense_name=expense_name,
                category_name=expense_info["category_name"],
                cost=cost,
                amount=1,
                created_date=created_date,
                comment="",
            ),
            reply_markup=create_confirm_transaction_keyboard(
                i18n["transaction_confirm_button"],
                i18n["transaction_correct_button"],
                i18n["transaction_cancel_button"],
            ),
        )


@router.message(StateFilter(FSMAddTransaction.fill_transaction))
async def process_incorrect_transaction(message: Message, i18n: dict[str, str]):
    logger.info("Transaction was sent in incorrect format.")
    await message.answer(text=i18n["transaction_incorrect_format"])


@router.callback_query(StateFilter(FSMAddTransaction.add_new_expense))
@router.callback_query(CategoriesCallbackFactory.filter())
async def process_add_expense(
    callback: CallbackQuery, i18n: dict[str, str], state: FSMContext
):
    category_name = callback.data.split(":")[-1]
    if category_name == i18n["transaction_add_new_category_callback"]:
        await state.set_state(FSMAddTransaction.add_new_category)
        logger.info(
            f"Request to set new category was sent. FSM was transformed to "
            f"{await state.get_state()} state."
        )
        await callback.message.answer(text=i18n["transaction_add_new_category"])
    else:
        transaction_data = await state.get_data()
        logger.info(
            f"Category was defined for new expense. FSM was transformed to "
            f"{await state.get_state()} state."
        )

        await state.update_data(category_name=category_name)
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
                i18n["transaction_confirm_button"],
                i18n["transaction_correct_button"],
                i18n["transaction_cancel_button"],
            ),
        )
    await callback.answer()


@router.message(StateFilter(FSMAddTransaction.confirm_transaction))
async def process_confirm_transaction(
    message: Message, i18n: dict[str, str], state: FSMContext
):
    if message.text == i18n["transaction_confirm_button"]:
        transaction_data = await state.get_data()
        add_transaction_to_db(
            telegram_id=message.from_user.id,
            expense_name=transaction_data["expense_name"],
            cost=transaction_data["cost"],
            created_date=transaction_data["created_date"],
            amount=transaction_data["amount"],
            comment=transaction_data["comment"],
        )
        await state.set_state(FSMAddTransaction.fill_transaction)
        logger.info(
            f"Transaction was confirmed and sent to database. FSM was transformed to "
            f"{await state.get_state()} state."
        )
        await message.answer(
            text=i18n["transaction_added"] + i18n["transaction_pattern"],
            reply_markup=ReplyKeyboardRemove(),
        )
    elif message.text == i18n["transaction_correct_button"]:
        pass
    elif message.text == i18n["transaction_cancel_button"]:
        await state.set_state(FSMAddTransaction.fill_transaction)
        logger.info(
            f"Transaction was canceled. FSM was transformed to "
            f"{await state.get_state()} state."
        )
        await message.answer(
            text=i18n["transaction_canceled"] + i18n["transaction_pattern"],
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        logger.info(
            "Instead of confirm/cancel/correct transaction was sent something else."
        )
        await message.answer(
            text=i18n["transaction_confirm_error"], reply_markup=ReplyKeyboardRemove()
        )


@router.message(StateFilter(FSMAddTransaction.add_new_category))
@router.message(IsCorrectCategoryName())
async def process_correct_category_name_transaction(
    message: Message, i18n: dict[str, str], state: FSMContext, category_name: str
):
    transaction_data = await state.get_data()
    await state.update_data(category_name=category_name)
    await state.set_state(FSMAddTransaction.confirm_transaction)
    logger.info(
        f"New category was defined for new expense. FSM was transformed to "
        f"{await state.get_state()} state."
    )
    await message.answer(
        text=i18n["transaction_category_added"].format(category_name=category_name)
        + i18n["transaction_expense_added"].format(
            expense_name=transaction_data["expense_name"], category_name=category_name
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
            i18n["transaction_confirm_button"],
            i18n["transaction_correct_button"],
            i18n["transaction_cancel_button"],
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
