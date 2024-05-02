from dataclasses import dataclass
from datetime import datetime
from typing import List

from sqlalchemy import BigInteger, DateTime, ForeignKey, func, null
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_table"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    user_name: Mapped[str]
    reg_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now()
    )

    categories: Mapped[List["Category"]] = relationship(
        back_populates="user", cascade="all, delete"
    )


class Category(Base):
    __tablename__ = "category_table"

    category_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_name: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.user_id"))

    user: Mapped["User"] = relationship(back_populates="categories")
    expenses: Mapped[List["Expense"]] = relationship(
        back_populates="category", cascade="all, delete"
    )


class Expense(Base):
    __tablename__ = "expense_table"

    expense_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    expense_name: Mapped[str]
    category_id: Mapped[int] = mapped_column(ForeignKey("category_table.category_id"))

    category: Mapped["Category"] = relationship(back_populates="expenses")
    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="expense", cascade="all, delete"
    )


class Transaction(Base):
    __tablename__ = "transaction_table"

    transaction_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    expense_id: Mapped[int] = mapped_column(ForeignKey("expense_table.expense_id"))
    cost: Mapped[float] = mapped_column(nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    amount: Mapped[int] = mapped_column(default=1)
    comment: Mapped[str] = mapped_column(server_default=null())

    expense: Mapped["Expense"] = relationship(back_populates="transactions")


@dataclass(slots=True, frozen=True)
class ExpenseCategory:
    expense_name: str
    expense_id: int
    category_name: str
    category_id: int
