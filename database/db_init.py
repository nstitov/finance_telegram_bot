import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

categories = [
    "Продукты",
    "Кафе",
    "Рестораны",
    "Жильё",
    "Дорога",
    "Машина",
    "Счета",
    "Образование",
    "Здоровье",
    "Игры",
    "Подарки",
    "Одежда",
    "Досуг",
    "Долг",
    "Путешествия",
    "Электроника",
]


def init_database(database_name: Path) -> None:
    """Create initial required table into database."""
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL UNIQUE,
            user_name TEXT,
            reg_date TEXT
        )
        """
        )
        logger.info("Users table was exsisted or created.")

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category_name TEXT,
            FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE
        )
        """
        )
        logger.info("Categories table was exsisted or created.")

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Expenses (
            expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_name TEXT,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES Categories (id) ON DELETE CASCADE
        )
        """
        )
        logger.info("Expenses table was exsisted or created.")

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_id INTEGER,
            cost REAL NOT NULL,
            created_date TEXT,
            amount INTEGER DEFAULT 1,
            comment TEXT DEFAULT NULL,
            FOREIGN KEY (expense_id) REFERENCES Expences (id) ON DELETE CASCADE
        )
        """
        )
        logger.info("Transaction table was exsisted or created.")


if __name__ == "__main__":
    init_database()
