import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import database.db_requests as db
from database.db_models import Base, Category, Expense, User


async def main():
    engine = create_async_engine(
        "postgresql+asyncpg://nstitov@localhost/testdb", echo=True, future=True
    )

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        await db.add_user(session, 1, "Nikita")
        user_info = await db.get_user_info(session, 1)
    async with async_session() as session:
        category_id = await db.add_category(session, 1, "Products")
    async with async_session() as session:
        expense_id = await db.add_expense(session, "Milk", category_id)
    async with async_session() as session:
        req = (
            select(Expense.expense_id, Category.category_id, Category.category_name)
            .join(Expense.category)
            .join(Category.user)
            .where(Expense.expense_name == "Milk")
            .where(User.telegram_id == 1)
        )
        result = await session.execute(req)
        for a in result.all():
            b, c, d = a
        pass


asyncio.run(main())
