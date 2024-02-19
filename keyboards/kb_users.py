from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from database.db_requests import get_all_user_categories
from keyboards.cbdata import CategoriesCallbackFactory


def create_categories_keyboard(
    telegram_id: int, add_new_category_text: str
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    user_categories = get_all_user_categories(telegram_id)
    if user_categories:
        for category in user_categories:
            keyboard.row(
                InlineKeyboardButton(
                    text=category,
                    callback_data=CategoriesCallbackFactory(
                        category_name=category
                    ).pack(),
                ),
                width=4,
            )
    keyboard.row(
        InlineKeyboardButton(
            text=add_new_category_text,
            callback_data=CategoriesCallbackFactory(
                category_name=add_new_category_text
            ).pack(),
        ),
        width=1,
    )
    return keyboard.as_markup()


def create_confirm_transaction_keyboard(
    confirm_text: str, correct_text: str, cancel_text: str
) -> ReplyKeyboardMarkup:
    confirm_keyboard = ReplyKeyboardBuilder()
    confirm_keyboard.row(
        KeyboardButton(text=confirm_text),
        KeyboardButton(text=correct_text),
        KeyboardButton(text=cancel_text),
        width=1,
    )
    return confirm_keyboard.as_markup()


def create_correct_transaction_keyboard(
    change_expense_name_button_text: str,
    change_category_button_text: str,
    change_cost_button_text: str,
    change_amount_button_text: str,
    change_created_date_button_text: str,
    change_comment_button_text: str,
) -> ReplyKeyboardMarkup:
    correct_keyboard = ReplyKeyboardBuilder()
    correct_keyboard.row(
        KeyboardButton(text=change_expense_name_button_text),
        KeyboardButton(text=change_category_button_text),
        KeyboardButton(text=change_cost_button_text),
        KeyboardButton(text=change_amount_button_text),
        KeyboardButton(text=change_created_date_button_text),
        KeyboardButton(text=change_comment_button_text),
        width=2,
    )
    return correct_keyboard.as_markup()
