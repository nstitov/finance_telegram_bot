import logging
from datetime import date

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

import bot.database.db_requests as db
from bot.filters.filters import IsCorrectCategoryName, IsCorrectTransaction
from bot.handlers.change_transaction_handlers import FSMChangeTransaction
from bot.handlers.command_handlers import FSMAddTransaction
from bot.keyboards.cbdata import CategoriesCallbackFactory
from bot.keyboards.kb_users import (
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
    async_session: AsyncSession,
    state: FSMContext,
    expense_name: str,
    cost: float,
):
    """Handler to handle correct transaction. Depends on expense existing in database
    pass state to confirmation state or adding new expense state.

    Args:
        message (Message): update with message with correct transaction from user
        i18n (dict[str, str]): dict with lexicon depends on user language settings
        async_session (AsyncSession): asynchronous session for connection with db
        state (FSMContext): Finite State Machine for user with user state and
            transaction data
        expense_name (str): name of expense received from message handled by filter
        cost (float): cost of expense received from message handled by filter
    """
    user_info = await db.get_user_info(async_session, message.from_user.id)
    expense_category_info = await db.get_expense_category_info(
        async_session,
        expense_name,
        user_info.user_id,
    )

    created_date = date.today()
    if not expense_category_info:
        await state.update_data(
            local_user_id=user_info.user_id,
            expense_name=expense_name,
            cost=cost,
            created_date=created_date.isoformat(),
            amount=1,
            comment="-",
        )

        await state.set_state(FSMAddTransaction.add_new_expense)
        logger.info(
            f"Expense {expense_name} for user #{user_info.user_id} wasn't found in db."
        )
        user_categories = await db.get_all_user_categories(
            async_session,
            user_info.user_id,
        )
        await message.answer(
            text=i18n["transaction_no_expense"],
            reply_markup=create_categories_keyboard(
                user_categories,
                i18n["transaction_add_new_category_callback"],
            ),
        )
    else:
        await state.update_data(
            local_user_id=user_info.user_id,
            expense_name=expense_name,
            expense_id=expense_category_info.expense_id,
            category_name=expense_category_info.category_name,
            cost=cost,
            created_date=created_date.isoformat(),
            amount=1,
            comment="-",
        )
        await state.set_state(FSMAddTransaction.confirm_transaction)
        logger.info(
            f"Expense {expense_name} for user #{user_info.user_id} was found in db."
        )
        await message.answer(
            text=i18n["transaction_info"].format(
                expense_name=expense_name,
                category_name=expense_category_info.category_name,
                cost=cost,
                amount=1,
                created_date=created_date.strftime("%d.%m.%Y"),
                comment="-",
            ),
            reply_markup=create_confirm_transaction_keyboard(
                i18n["transaction_confirm_button"],
                i18n["transaction_correct_button"],
                i18n["transaction_cancel_button"],
            ),
        )


@router.message(StateFilter(FSMAddTransaction.fill_transaction))
async def process_incorrect_transaction(message: Message, i18n: dict[str, str]):
    """Handler to handle message with incorrect transaction format.

    Args:
        message (Message): update with message with incorrect transaction from user
        i18n (dict[str, str]): dict with lexicon depends on user language settings
    """
    logger.info(f"User {message.from_user.id} passed transaction in incorrect format.")
    await message.answer(
        text=i18n["transaction_incorrect_format"] + i18n["transaction_pattern"]
    )


@router.callback_query(
    StateFilter(FSMAddTransaction.add_new_expense), CategoriesCallbackFactory.filter()
)
async def process_add_expense(
    callback: CallbackQuery,
    i18n: dict[str, str],
    async_session: AsyncSession,
    state: FSMContext,
):
    """Handler to handle choice of category for new expense. If user chose existed
    category add extense to this category and pass user to confirmation state, else user
    chose add new category pass user to adding new category state.

    Args:
        callback (CallbackQuery): update with callback with category name
        i18n (dict[str, str]): dict with lexicon depends on user language settings
        async_session (AsyncSession): asynchronous session for connection with db
        state (FSMContext): Finite State Machine for user with user state and
            transaction data
    """
    transaction_data = await state.get_data()
    local_user_id = transaction_data["local_user_id"]
    expense_name = transaction_data["expense_name"]

    category_name = callback.data.split(":")[-1]
    if category_name == i18n["transaction_add_new_category_callback"]:
        await state.set_state(FSMAddTransaction.add_new_category)
        logger.info(
            f"User {local_user_id} chose to add new category for {expense_name}."
        )
        await callback.message.answer(text=i18n["transaction_add_new_category"])
    else:
        category_info = await db.get_category_info(
            async_session,
            local_user_id,
            category_name,
        )
        await state.update_data(
            category_name=category_name,
            category_id=category_info.category_id,
        )
        await state.set_state(FSMAddTransaction.confirm_transaction)
        logger.info(
            f"User {local_user_id} added {expense_name} to {category_name} category."
        )
        await callback.message.answer(
            text=i18n["transaction_expense_added"].format(
                expense_name=expense_name,
                category_name=category_name,
            )
            + i18n["transaction_info"].format(
                expense_name=expense_name,
                category_name=category_name,
                cost=transaction_data["cost"],
                amount=transaction_data["amount"],
                created_date=date.fromisoformat(
                    transaction_data["created_date"]
                ).strftime("%d.%m.%Y"),
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
    message: Message,
    i18n: dict[str, str],
    async_session: AsyncSession,
    state: FSMContext,
):
    """Handler to confirm, change or cancel transaction. Depends on pressed button
    handler will confirm transaction (add to db) and pass user to fill new transaction
    state, pass user to correct transaction state or cancel transaction and pass user to
    fill new transaction state.

    Args:
        message (Message): update with message with correct transaction from user
        i18n (dict[str, str]): dict with lexicon depends on user language settings
        async_session (AsyncSession): asynchronous session for connection with db
        state (FSMContext): Finite State Machine for user with user state and
            transaction data
    """
    transaction_data = await state.get_data()
    local_user_id = transaction_data["local_user_id"]

    if message.text == i18n["transaction_confirm_button"]:
        expense_id = transaction_data.get("expense_id", None)
        if not expense_id:
            category_id = transaction_data.get("category_id", None)
            if not category_id:
                category_id = await db.add_category(
                    async_session,
                    transaction_data["local_user_id"],
                    transaction_data["category_name"],
                )
            expense_id = await db.add_expense(
                async_session,
                transaction_data["expense_name"],
                category_id,
            )

        await db.add_transaction(
            async_session=async_session,
            user_id=local_user_id,
            expense_id=expense_id,
            cost=transaction_data["cost"],
            created_date=date.fromisoformat(transaction_data["created_date"]),
            amount=transaction_data["amount"],
            comment=transaction_data["comment"],
        )
        await async_session.commit()
        await state.clear()
        await state.set_state(FSMAddTransaction.fill_transaction)
        logger.info(f"User #{local_user_id} transaction was added to db.")
        await message.answer(
            text=i18n["transaction_added"] + i18n["transaction_pattern"],
            reply_markup=ReplyKeyboardRemove(),
        )
    elif message.text == i18n["transaction_correct_button"]:
        await state.set_state(FSMAddTransaction.correct_transaction)
        logger.info(f"User #{local_user_id} sent request to change transaction.")
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
        await state.clear()
        await state.set_state(FSMAddTransaction.fill_transaction)
        logger.info(f"User #{local_user_id} canceled current transaction.")
        await message.answer(
            text=i18n["transaction_canceled"] + i18n["transaction_pattern"],
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        logger.info(f"User #{local_user_id} sent something else instead button reply.")
        await message.answer(
            text=i18n["transaction_confirm_error"], reply_markup=ReplyKeyboardRemove()
        )


@router.message(
    StateFilter(FSMAddTransaction.add_new_category), IsCorrectCategoryName()
)
async def process_correct_category_name_transaction(
    message: Message,
    i18n: dict[str, str],
    async_session: AsyncSession,
    state: FSMContext,
    category_name: str,
):
    """Handler to add new category for user. If user sent non-existed category handler
    add this category to db, else handler ask user to send name of new category.

    Args:
        message (Message): update with message with correct transaction from user
        i18n (dict[str, str]): dict with lexicon depends on user language settings
        async_session (AsyncSession): asynchronous session for connection with db
        state (FSMContext): Finite State Machine for user with user state and
            transaction data
        category_name (str): name on new category
    """
    transaction_data = await state.get_data()
    local_user_id = transaction_data["local_user_id"]
    expense_name = transaction_data["expense_name"]

    user_categories = await db.get_all_user_categories(async_session, local_user_id)
    if category_name in user_categories:
        logger.info(
            f"User #{local_user_id} tried to add existed category {category_name}."
        )
        await message.answer(
            text=i18n["transaction_existed_category"]
            + i18n["transaction_add_new_category"]
        )
    else:
        await state.update_data(category_name=category_name)
        await state.set_state(FSMAddTransaction.confirm_transaction)

        logger.info(f"User {local_user_id} added new category {category_name}.")
        await message.answer(
            text=i18n["transaction_category_added"].format(category_name=category_name)
            + i18n["transaction_expense_added"].format(
                expense_name=expense_name,
                category_name=category_name,
            )
            + i18n["transaction_info"].format(
                expense_name=expense_name,
                category_name=category_name,
                cost=transaction_data["cost"],
                amount=transaction_data["amount"],
                created_date=date.fromisoformat(
                    transaction_data["created_date"]
                ).strftime("%d.%m.%Y"),
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
    message: Message, i18n: dict[str, str], state: FSMContext
):
    """Handler to handle message with incorrect category name format.

    Args:
        message (Message): update with message with incorrect category name from user
        i18n (dict[str, str]): dict with lexicon depends on user language settings
    """
    logger.info(
        f"User {message.from_user.id} passed category name in incorrect format."
    )
    await message.answer(
        text=i18n["transaction_incorrect_category_name"]
        + i18n["transaction_add_new_category"]
    )


@router.message(StateFilter(FSMAddTransaction.correct_transaction))
async def process_change_transaction_info(
    message: Message,
    i18n: dict[str, str],
    async_session: AsyncSession,
    state: FSMContext,
):
    """Handler to change transaction data. Depends on pressed button handler will change
    expense name, expense category, cost, amount, created date or comment.

    Args:
        message (Message): update with message with correct transaction from user
        i18n (dict[str, str]): dict with lexicon depends on user language settings
        async_session (AsyncSession): asynchronous session for connection with db
        state (FSMContext): Finite State Machine for user with user state and
            transaction data
    """
    transaction_data = await state.get_data()
    local_user_id = transaction_data["local_user_id"]

    if message.text == i18n["transaction_correct_expense_name_button"]:
        await state.set_state(FSMChangeTransaction.change_expense_name)
        logger.info(f"User #{local_user_id} sent request to correct expense name.")
        await message.answer(
            text=i18n["transaction_change_expense_name"],
            reply_markup=ReplyKeyboardRemove(),
        )
    elif message.text == i18n["transaction_correct_category_button"]:
        await state.set_state(FSMAddTransaction.add_new_expense)
        logger.info(f"User #{local_user_id} sent request to correct category.")
        user_categories = await db.get_all_user_categories(async_session, local_user_id)
        await message.answer(
            text=i18n["transaction_change_category"],
            reply_markup=create_categories_keyboard(
                user_categories,
                i18n["transaction_add_new_category_callback"],
            ),
        )
    elif message.text == i18n["transaction_correct_cost_button"]:
        await state.set_state(FSMChangeTransaction.change_cost)
        logger.info(f"User #{local_user_id} sent request to correct cost.")
        await message.answer(
            text=i18n["transaction_change_cost"], reply_markup=ReplyKeyboardRemove()
        )
    elif message.text == i18n["transaction_correct_amount_button"]:
        await state.set_state(FSMChangeTransaction.change_amount)
        logger.info(f"User #{local_user_id} sent request to correct amount.")
        await message.answer(
            text=i18n["transaction_change_amount"], reply_markup=ReplyKeyboardRemove()
        )
    elif message.text == i18n["transaction_correct_created_date_button"]:
        await state.set_state(FSMChangeTransaction.change_created_date)
        logger.info(f"User #{local_user_id} sent request to correct created_date.")
        await message.answer(
            text=i18n["transaction_change_created_date"],
            reply_markup=ReplyKeyboardRemove(),
        )
    elif message.text == i18n["transaction_correct_comment_button"]:
        await state.set_state(FSMChangeTransaction.change_comment)
        logger.info(f"User #{local_user_id} sent request to correct comment.")
        await message.answer(
            text=i18n["transaction_change_comment"], reply_markup=ReplyKeyboardRemove()
        )
