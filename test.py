import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from database.models import Base
from database.requests import add_category, add_user, get_user_info


async def main():
    engine = create_async_engine(
        "postgresql+asyncpg://nstitov@localhost/testdb", echo=False, future=True
    )

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    result = await get_user_info(async_session, 11111)
    print(result.user_name, result.reg_date, sep="\n")
    await engine.dispose()


asyncio.run(main())
