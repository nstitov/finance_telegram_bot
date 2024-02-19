import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path

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


@dataclass
class Transaction:
    expense_name: str
    cost: float
    amount: int = 2
    create_date: date = date.today()
    comment: str = ""


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


if __name__ == "__main__":
    init_database()
