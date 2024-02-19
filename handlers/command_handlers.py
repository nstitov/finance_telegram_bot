import logging

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.types import Message

from database.db_requests import add_user_to_db

router = Router()
logger = logging.getLogger(__name__)


class FSMAddTransaction(StatesGroup):
    fill_transaction = State()
    confirm_transaction = State()
    correct_transaction = State()
    add_new_expense = State()
    add_new_category = State()


@router.message(Command("start"), StateFilter(default_state))
async def process_start_command(message: Message, i18n: dict[str, str]):
    logger.info(f"User {message.from_user.full_name} sent /start command.")
    add_user_to_db(
        message.from_user.id,
        message.from_user.first_name,
    )
    await message.answer(text=i18n["/start"])


@router.message(Command("cancel"), StateFilter(default_state))
async def process_cancel_command(message: Message, i18n: dict[str, str]):
    await message.answer(text=i18n["/cancel_disaprove"])


@router.message(Command("cancel"), ~StateFilter(default_state))
async def process_cancel_command_state(
    message: Message, i18n: dict[str, str], state: FSMContext
):
    logger.info(
        f"User {message.from_user.full_name} sent /cancel command from "
        f"{await state.get_state()} state."
    )
    await state.clear()
    await message.answer(text=i18n["/cancel_approve"])


@router.message(Command("add_transactions"), StateFilter(default_state))
async def process_add_transaction_command(
    message: Message, i18n: dict[str, str], state: FSMContext
):
    logger.info(
        f"User {message.from_user.full_name} was moved to transaction adding mode."
    )
    await state.set_state(FSMAddTransaction().fill_transaction)
    await message.answer(text=i18n["transaction_pattern"])
