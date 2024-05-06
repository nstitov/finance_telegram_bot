import asyncio
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import bot.database.db_requests as db
from bot.database.db_models import Base, Category, Expense, User


async def main():
    engine = create_async_engine(
        "postgresql+asyncpg://nstitov@localhost/testdb", echo=True, future=True
    )

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        await db.add_user(session, 1, "Nikita")
    async with async_session() as session:
        user_info = await db.get_user_info(session, 1)
        async with session.begin():
            category_id = await db.add_category(session, 1, "Car")
            expense_id = await db.add_expense(session, "Wheels", category_id)
            await db.add_transaction(session, expense_id, 1, date.today(), 1, "-")


asyncio.run(main())
