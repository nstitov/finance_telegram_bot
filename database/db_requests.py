import logging
import sqlite3
from datetime import datetime
from typing import Any, Literal, Optional

from config_data.config import DATABASE_NAME

logger = logging.getLogger(__file__)


def add_user_to_db(telegram_id: int, user_name: str) -> None:
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
        logger.info("User added to database.")


def get_user_info_from_db(
    telegram_id: int,
) -> Optional[
    dict[Literal["user_id", "telegram_id", "user_name", "reg_date"], int | str]
]:
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
            logger.info("User info was got from database.")
            return user_info_dct
        logger.warning(f"User info for {telegram_id=} wasn't found in database.")


def add_category_to_db(telegram_id: int, category_name: str) -> None:
    user_info = get_user_info_from_db(telegram_id)
    category_id = get_category_id_from_db(user_info["user_id"], category_name)
    if not category_id:
        with sqlite3.connect(DATABASE_NAME) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO Categories (user_id, category_name) VALUES (?, ?)",
                (user_info["user_id"], category_name),
            )
            logger.info("User category added to database.")
    else:
        logger.warning(
            f"User category {category_name=} for {telegram_id=} has already added to "
            f"database."
        )


def get_category_id_from_db(telegram_id: int, category_name: str) -> Optional[int]:
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
            logger.info("Category id was got from database.")
            return category_id[0]

        logger.warning(
            f"Category id for {category_name=} and {telegram_id} wasn't found in "
            f"database."
        )


def add_expense_to_db(telegram_id: int, category_name: str, expense_name: str) -> None:
    category_id = get_category_id_from_db(telegram_id, category_name)
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Expenses (expense_name, category_id) VALUES (?, ?)",
            (expense_name, category_id),
        )
        logger.info("Expense added to database.")


def get_expense_category_name_from_db(
    telegram_id: int, expense_name: str
) -> Optional[dict]:
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """SELECT category_name
            FROM
            Expenses
            INNER JOIN Categories ON Expenses.category_id = Categories.category_id
            INNER JOIN Users ON Categories.user_id = Users.user_id
            WHERE expense_name=? AND telegram_id=?
            """,
            (expense_name, telegram_id),
        )
        category_name = cursor.fetchone()
        if category_name:
            logger.info("Expense category name was got from database.")
            return category_name[0]
        logger.info(
            f"Expense category name for required {expense_name=} and {telegram_id=} "
            f"wasn't found."
        )


def get_all_user_categories(telegram_id: int) -> Optional[list[str]]:
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT category_name
            FROM Categories
            INNER JOIN Users ON Categories.user_id = Users.user_id
            WHERE telegram_id=?
            """,
            (telegram_id,),
        )
        categories = [category[0] for category in cursor.fetchall()]

        if categories:
            logger.info(f"Categories names for user {telegram_id=} was got.")
            return categories
        logger.warning(f"Categories names for user {telegram_id=} wasn't found.")


# ---
def add_transaction_to_db(
    user_id: int,
    expense_id: int,
    cost: float,
    created_date: Optional[datetime] = None,
    amount: int = 1,
    comment: Optional[Any] = None,
):
    if not created_date:
        created_date = datetime.utcnow()
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO Transactions
            (user_id, expense_id, cost, created_date, amount, comment) VALUES
            (?, ?, ?, ?, ?, ?)
            """,
            (user_id, expense_id, cost, created_date, amount, comment),
        )
        logger.info("Transaction added to database.")


def get_expense_id(expense_name: str) -> Optional[int]:
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT expense_id FROM Expenses WHERE exspense_name=?", (expense_name,)
            )
            expense_id = cursor.fetchone()
            logger.info("Expense_id was got from database.")
            return expense_id
        except Exception:
            # TODO: Check Exception type if extense not found
            logger.exception("Exspense wasn't found in database.")
            return None


# def get_category_name(expense_name: str) -> Optional[int]:
#     with sqlite3.connect(DATABASE_NAME) as connection:
#         cursor = connection.cursor()
#         try:
#             pass


def get_user_id(telegram_id: int) -> Optional[int]:
    with sqlite3.connect(DATABASE_NAME) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT user_id FROM Users WHERE telegram_id=?", (telegram_id,)
            )
            telegram_id = cursor.fetchone()
            logger.info("User_id was got from database.")
        except Exception:
            # TODO: Check Exception type if user not found
            logger.exception("User wasn't found in database.")
            return None


def get_category_id(category_name: str) -> Optional[int]:
    with sqlite3.connect(DATABASE_NAME) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT category_id FROM Categories WHERE category_name=?",
                (category_name,),
            )
            category_id = cursor.fetchone()
            logger.info("Category_id was got from database.")
            return category_id
        except Exception:
            # TODO: Check Exception type if category not found
            logger.exception("Category wasn't found in database.")
