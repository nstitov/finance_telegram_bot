import logging
from datetime import date

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

import database.db_requests as db
from filters.filters import IsCorrectCategoryName, IsCorrectTransaction
from handlers.change_transaction_handlers import FSMChangeTransaction
from handlers.command_handlers import FSMAddTransaction
from keyboards.cbdata import CategoriesCallbackFactory
from keyboards.kb_users import (
    create_categories_keyboard,
    create_confirm_transaction_keyboard,
    create_correct_transaction_keyboard,
)

router = Router()
logger = logging.getLogger(__name__)


@router.message(StateFilter(FSMAddTransaction.fill_transaction), IsCorrectTransaction())
async def process_correct_transaction(
    message: Message,
    i18n: dict[str, str],
    state: FSMContext,
    async_session: AsyncSession,
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

    expense_category_name = await db.get_expense_category_name(
        async_session,
        message.from_user.id,
        expense_name,
    )
    if not expense_category_name:
        await state.set_state(FSMAddTransaction.add_new_expense)
        logger.info(
            f"Expense {expense_name} wasn't in db. New FSM state is "
            f"{await state.get_state()}."
        )
        user_categories = await db.get_all_user_categories(
            async_session, message.from_user.id
        )
        await message.answer(
            text=i18n["transaction_no_expense"],
            reply_markup=create_categories_keyboard(
                user_categories,
                i18n["transaction_add_new_category_callback"],
            ),
        )
    else:
        await state.update_data(category_name=expense_category_name)
        await state.set_state(FSMAddTransaction.confirm_transaction)
        logger.info(
            f"Expense {expense_name} was found in db. New FSM state is "
            f"{await state.get_state()}."
        )
        await message.answer(
            text=i18n["transaction_info"].format(
                expense_name=expense_name,
                category_name=expense_category_name,
                cost=cost,
                amount=1,
                created_date=created_date.strftime("%d.%m.%Y"),
                comment=i18n["transaction_without_comment"],
            ),
            reply_markup=create_confirm_transaction_keyboard(
                i18n["transaction_confirm_button"],
                i18n["transaction_correct_button"],
                i18n["transaction_cancel_button"],
            ),
        )


@router.message(StateFilter(FSMAddTransaction.fill_transaction))
async def process_incorrect_transaction(message: Message, i18n: dict[str, str]):
    logger.debug("Transaction has incorrect format.")
    await message.answer(
        text=i18n["transaction_incorrect_format"] + i18n["transaction_pattern"]
    )


@router.callback_query(
    StateFilter(FSMAddTransaction.add_new_expense), CategoriesCallbackFactory.filter()
)
async def process_add_expense(
    callback: CallbackQuery, i18n: dict[str, str], state: FSMContext
):
    category_name = callback.data.split(":")[-1]
    if category_name == i18n["transaction_add_new_category_callback"]:
        await state.set_state(FSMAddTransaction.add_new_category)
        logger.info(f"Adding new category. New FSM state is {await state.get_state()}.")
        await callback.message.answer(text=i18n["transaction_add_new_category"])
    else:
        logger.info(
            f"Expense was added to category. New FSM state is "
            f"{await state.get_state()}."
        )

        await state.update_data(category_name=category_name)
        await state.set_state(FSMAddTransaction.confirm_transaction)
        transaction_data = await state.get_data()
        await callback.message.answer(
            text=i18n["transaction_expense_added"].format(
                expense_name=transaction_data["expense_name"],
                category_name=transaction_data["category_name"],
            )
            + i18n["transaction_info"].format(
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
    await callback.answer()


@router.message(StateFilter(FSMAddTransaction.confirm_transaction))
async def process_confirm_transaction(
    message: Message,
    i18n: dict[str, str],
    state: FSMContext,
    async_session: AsyncSession,
):
    if message.text == i18n["transaction_confirm_button"]:
        transaction_data = await state.get_data()
        await db.add_transaction(
            async_session=async_session,
            telegram_id=message.from_user.id,
            expense_name=transaction_data["expense_name"],
            category_name=transaction_data["category_name"],
            cost=transaction_data["cost"],
            created_date=transaction_data["created_date"],
            amount=transaction_data["amount"],
            comment=transaction_data["comment"],
        )
        await state.set_state(FSMAddTransaction.fill_transaction)
        logger.info(
            f"Transaction was sent to db. New FSM state is {await state.get_state()}."
        )
        await message.answer(
            text=i18n["transaction_added"] + i18n["transaction_pattern"],
            reply_markup=ReplyKeyboardRemove(),
        )
    elif message.text == i18n["transaction_correct_button"]:
        await state.set_state(FSMAddTransaction.correct_transaction)
        logger.info(
            f"Request to correct transaction was got. New FSM state is "
            f"{await state.get_state()}."
        )
        await message.answer(
            text=i18n["transaction_correct"],
            reply_markup=create_correct_transaction_keyboard(
                i18n["transaction_correct_expense_name_button"],
                i18n["transaction_correct_category_button"],
                i18n["transaction_correct_cost_button"],
                i18n["transaction_correct_amount_button"],
                i18n["transaction_correct_created_date_button"],
                i18n["transaction_correct_comment_button"],
            ),
        )
    elif message.text == i18n["transaction_cancel_button"]:
        await state.set_state(FSMAddTransaction.fill_transaction)
        logger.info(
            f"Transaction was canceled. New FSM state is {await state.get_state()}."
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


@router.message(
    StateFilter(FSMAddTransaction.add_new_category), IsCorrectCategoryName()
)
async def process_correct_category_name_transaction(
    message: Message, i18n: dict[str, str], state: FSMContext, category_name: str
):
    await state.update_data(category_name=category_name)
    await state.set_state(FSMAddTransaction.confirm_transaction)
    transaction_data = await state.get_data()
    logger.info(
        f"New category was defined. New FSM state is {await state.get_state()}."
    )
    await message.answer(
        text=i18n["transaction_category_added"].format(category_name=category_name)
        + i18n["transaction_expense_added"].format(
            expense_name=transaction_data["expense_name"], category_name=category_name
        )
        + i18n["transaction_info"].format(
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


@router.message(StateFilter(FSMAddTransaction.add_new_category))
async def process_incorrect_category_name_transaction(
    message: Message, i18n: dict[str, str]
):
    await message.answer(
        text=i18n["transaction_incorrect_category_name"]
        + i18n["transaction_add_new_category"]
    )


@router.message(StateFilter(FSMAddTransaction.correct_transaction))
async def process_change_transaction_info(
    message: Message,
    i18n: dict[str, str],
    state: FSMContext,
    async_session: AsyncSession,
):
    if message.text == i18n["transaction_correct_expense_name_button"]:
        await state.set_state(FSMChangeTransaction.change_expense_name)
        logger.info(
            f"Request to correct expense name. New FSM state is "
            f"{await state.get_state()}."
        )
        await message.answer(
            text=i18n["transaction_change_expense_name"],
            reply_markup=ReplyKeyboardRemove(),
        )
    elif message.text == i18n["transaction_correct_category_button"]:
        await state.set_state(FSMAddTransaction.add_new_expense)
        logger.info(
            f"Request to correct category. New FSM state is {await state.get_state()}."
        )
        user_categories = await db.get_all_user_categories(
            async_session, message.from_user.id
        )
        await message.answer(
            text=i18n["transaction_change_category"],
            reply_markup=create_categories_keyboard(
                user_categories,
                i18n["transaction_add_new_category_callback"],
            ),
        )
    elif message.text == i18n["transaction_correct_cost_button"]:
        await state.set_state(FSMChangeTransaction.change_cost)
        logger.info(
            f"Request to correct cost. New FSM state is {await state.get_state()}."
        )
        await message.answer(
            text=i18n["transaction_change_cost"], reply_markup=ReplyKeyboardRemove()
        )
    elif message.text == i18n["transaction_correct_amount_button"]:
        await state.set_state(FSMChangeTransaction.change_amount)
        logger.info(
            f"Request to correct amount. New FSM state is {await state.get_state()}."
        )
        await message.answer(
            text=i18n["transaction_change_amount"], reply_markup=ReplyKeyboardRemove()
        )
    elif message.text == i18n["transaction_correct_created_date_button"]:
        await state.set_state(FSMChangeTransaction.change_created_date)
        logger.info(
            f"Request to correct created_date. New FSM state is "
            f"{await state.get_state()}."
        )
        await message.answer(
            text=i18n["transaction_change_created_date"],
            reply_markup=ReplyKeyboardRemove(),
        )
    elif message.text == i18n["transaction_correct_comment_button"]:
        await state.set_state(FSMChangeTransaction.change_comment)
        logger.info(
            f"Request to correct comment. New FSM state is {await state.get_state()}."
        )
        await message.answer(
            text=i18n["transaction_change_comment"], reply_markup=ReplyKeyboardRemove()
        )
