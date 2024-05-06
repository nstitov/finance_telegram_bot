from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.keyboards.cbdata import CategoriesCallbackFactory


def create_categories_keyboard(
    user_categories: list[str], add_new_category_text: str
) -> InlineKeyboardMarkup:
    """Create inline keyboard with available categories for user.

    Args:
        categories (list[str]): list with available categories
        add_new_category_text (str): text for button to add new category

    Returns:
        InlineKeyboardMarkup: markup of inline keyboard with available categories and
            button to add new category
    """
    keyboard = InlineKeyboardBuilder()
    for category in user_categories:
        keyboard.row(
            InlineKeyboardButton(
                text=category,
                callback_data=CategoriesCallbackFactory(category_name=category).pack(),
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
    """Create keyboard for transaction confirmation.

    Args:
        confirm_text (str): text for button to confirm transaction
        corrent_text (str): text for button to corrent transaction
        cancel_text (str): text for button to cancel transaction

    Returns:
        ReplyKeyboardMarkup: murkup of keyboard with buttons to manage transaction
    """
    confirm_keyboard = ReplyKeyboardBuilder()
    confirm_keyboard.row(
        KeyboardButton(text=confirm_text),
        KeyboardButton(text=correct_text),
        KeyboardButton(text=cancel_text),
        width=1,
    )
    return confirm_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)


def create_correct_transaction_keyboard(
    change_expense_name_button_text: str,
    change_category_button_text: str,
    change_cost_button_text: str,
    change_amount_button_text: str,
    change_created_date_button_text: str,
    change_comment_button_text: str,
) -> ReplyKeyboardMarkup:
    """Create keyboard for correction transaction.

    Args:
        change_expense_name_button_text (str): text for button to change expense name
        change_category_button_text (str): text for button to change category name
        change_cost_button_text (str): text for button to change expense cost
        change_amount_button_text (str): text for button to change amount of expense
        change_created_date_button_text (str): text for button to change date of expense
        change_comment_button_text (str): text for button to change comment for expense

    Returns:
        ReplyKeyboardMarkup: murkup of keyboard with button to correct transaction
    """
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
    return correct_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)
