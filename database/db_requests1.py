import logging
import sqlite3
from datetime import date, datetime
from typing import Literal, Optional

from config_data.config import DATABASE_NAME

logger = logging.getLogger(__name__)


def add_user_to_db(telegram_id: int, user_name: str) -> None:
    """
    Add user information to database.

    Args:
        telegram_id (int): user Telegram ID
        user_name (str): user Telegram name

    Returns:
    """
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO Users
            (telegram_id, user_name, reg_date) VALUES (?, ?, ?)
            """,
            (
                telegram_id,
                user_name,
                datetime.utcnow().replace(microsecond=0).isoformat(),
            ),
        )
        logger.info(f"User with Telegram ID {telegram_id} was added to database.")


def get_user_info_from_db(
    telegram_id: int,
) -> Optional[
    dict[Literal["user_id", "telegram_id", "user_name", "reg_date"], int | str]
]:
    """
    Get user information from database.

    Args:
        telegram_id (int): user Telegram ID

    Returns:
        dict[str, int | str]: dict with user information: user_id - user ID in database,
            telegram_id - Telegram ID, user_name - Telegram username and reg_date - date
            of user start bot if user was found in database, else None
    """
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE telegram_id=?", (telegram_id,))
        user_info = cursor.fetchone()
        if user_info:
            user_info_dct = {}
            user_info_dct["user_id"] = user_info[0]
            user_info_dct["telegram_id"] = user_info[1]
            user_info_dct["user_name"] = user_info[2]
            user_info_dct["reg_date"] = user_info[3]
            logger.info(
                f"Info for user with Telegram ID {telegram_id} was got from database."
            )
            return user_info_dct
        logger.warning(
            f"Info for user with Telegram ID {telegram_id} wasn't found in database."
        )


def add_category_to_db(telegram_id: int, category_name: str) -> int:
    """
    Add new category to database.

    Args:
        telegram_id (int): user Telegram ID
        category_name (str): name of category

    Returns:
        int: category ID in database
    """
    user_info = get_user_info_from_db(telegram_id)
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Categories (user_id, category_name) VALUES (?, ?)",
            (user_info["user_id"], category_name),
        )
        logger.info(
            f"Category {category_name} for user with Telegram ID {telegram_id} was "
            f"added to database."
        )
        cursor.execute(
            "SELECT category_id FROM Categories ORDER BY category_id DESC LIMIT 1"
        )
        return cursor.fetchone()[0]


def get_category_id_from_db(telegram_id: int, category_name: str) -> Optional[int]:
    """
    Get category ID from database.

    Args:
        telegram_id (int): user Telegram ID
        category_name (str): name of category

    Returns:
        int: category ID in database if category was found in database, else None
    """
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT category_id
            FROM Categories
            INNER JOIN Users ON Categories.user_id = Users.user_id
            WHERE telegram_id=? AND category_name=?
            """,
            (telegram_id, category_name),
        )
        category_id = cursor.fetchone()
        if category_id:
            logger.info(
                f"Category ID for category {category_name} for user with Telegram ID "
                f"{telegram_id} was got from database."
            )
            return category_id[0]

        logger.warning(
            f"Category ID for category {category_name} and telegram user with Telegram "
            f"ID {telegram_id} wasn't found in database."
        )


def add_expense_to_db(expense_name: str, category_id: int) -> int:
    """
    Add new expense to database.

    Args:
        expense_name (str) - name of new expense
        category_id (str) - category ID of new expense

    Returns:
        int: new expense ID in database
    """
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Expenses (expense_name, category_id) VALUES (?, ?)",
            (expense_name, category_id),
        )
        logger.info(
            f"Expense {expense_name} in category with ID {category_id} was added to "
            f"database."
        )
        cursor.execute(
            "SELECT expense_id FROM Expenses ORDER BY expense_id DESC LIMIT 1"
        )
        return cursor.fetchone()[0]


def get_expense_info_from_db(
    telegram_id: int, expense_name: str
) -> Optional[dict[Literal["expense_id", "category_name"], str | int]]:
    """
    Get expense information from database.

    Args:
        telegram_id (int): user Telegram ID
        expense_name (str): name of expense

    Returns:
        dict[str, str | int]: dict with expense information: expense_id - expense ID in
            database, category_name - name of expense category
    """
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT expense_id, category_name
            FROM Expenses
                INNER JOIN Categories ON Expenses.category_id = Categories.category_id
                INNER JOIN Users ON Categories.user_id = Users.user_id
            WHERE expense_name=? AND telegram_id=?
            ORDER BY expense_id
            """,
            (expense_name, telegram_id),
        )
        expense_info = cursor.fetchone()
        if expense_info:
            expense_info_dict = {}
            expense_info_dict["expense_id"] = expense_info[0]
            expense_info_dict["category_name"] = expense_info[1]
            logger.info(f"Expense info {expense_name} for user {telegram_id} was got.")
            return expense_info_dict
        logger.info(f"Expense info {expense_name} for user {telegram_id} wasn't found.")


def get_all_user_categories(telegram_id: int) -> Optional[list[str]]:
    """
    Get all categories names for required user from database.

    Args:
        telegram_id (int): user Telegram ID

    Returns:
        list[str]: list of categories names for required user if existed else None
    """
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT category_name
            FROM Categories INNER JOIN Users ON Categories.user_id = Users.user_id
            WHERE telegram_id=?
            """,
            (telegram_id,),
        )
        categories = [category[0] for category in cursor.fetchall()]

        if categories:
            logger.info(f"Category names for user {telegram_id} was got from db.")
            return categories
        logger.info(f"Category names for user {telegram_id} wasn't found in db.")


def add_transaction_to_db(
    telegram_id: int,
    expense_name: str,
    category_name: str,
    cost: float,
    created_date: str,
    amount: int,
    comment: str,
) -> None:
    """
    Add new transaction to database. Also add new category and new expense to database
    if required.

    Args:
        telegram_id (int): user Telegram ID
        expense_name (str): name of expense
        category_name (str): name of expense category
        cost (float): cost of expense
        created_date (date): date of expense
        amount (int): amount of expense
        comment (str): comment for expense

    Returns:
    """
    category_id = get_category_id_from_db(telegram_id, category_name)
    if not category_id:
        category_id = add_category_to_db(telegram_id, category_name)
    expense_info = get_expense_info_from_db(telegram_id, expense_name)
    if not expense_info or expense_info["category_name"] != category_name:
        expense_id = add_expense_to_db(expense_name, category_id)
    else:
        expense_id = expense_info["expense_id"]
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO Transactions
            (expense_id, cost, created_date, amount, comment) VALUES
            (?, ?, ?, ?, ?)
            """,
            (expense_id, cost, created_date, amount, comment),
        )
        logger.info(f"Transaction for user {telegram_id} was added to db.")
