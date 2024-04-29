import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_models import Category, Expense, Transaction, User

logger = logging.getLogger(__name__)


async def add_user(
    async_session: AsyncSession, telegram_id: int, user_name: str
) -> None:
    """
    Add user information to database.

    Args:
        async_session (AsyncSession): asynchronous session for connection with db
        telegram_id (int): user Telegram ID
        user_name (str): user Telegram name
    """
    try:
        async with async_session.begin():
            async_session.add(User(telegram_id=telegram_id, user_name=user_name))
            logger.info(f"User {telegram_id} was added to db.")
    except IntegrityError:
        logger.warning(f"Attempt to add an existing user: {telegram_id}.")


async def get_user_info(async_session: AsyncSession, telegram_id: int) -> User:
    """
    Get user information from database.

    Args:
        async_session (AsyncSession): asynchronous session for connection with db
        telegram_id (int): user Telegram ID

    Returns:
        Users: instance of User table class with information of required user
    """
    req = select(User).where(User.telegram_id == telegram_id)
    result = await async_session.execute(req)
    try:
        user_info = result.scalar_one()
        logger.info(f"Info for user {telegram_id} was got from db.")
        return user_info
    except NoResultFound:
        logger.warning(f"Info for user {telegram_id} wasn't found in db.")


async def add_category(
    async_session: AsyncSession,
    telegram_id: int,
    category_name: str,
) -> int:
    """
    Add new category to database.

    Args:
        async_session (AsyncSession): asynchronous session for connection with db
        telegram_id (int): user Telegram ID
        category_name (str): name of category

    Returns:
        int: category ID in database
    """
    user_info = await get_user_info(async_session, telegram_id)

    async with async_session.begin():
        async_session.add(
            Category(category_name=category_name, user_id=user_info.user_id)
        )
        logger.info(f"Category {category_name} for user {telegram_id} was added to db.")

    req = select(Category).order_by(Category.category_id.desc()).limit(1)
    result = await async_session.execute(req)
    try:
        category_info = result.scalar_one()
        return category_info.category_id
    except NoResultFound:
        logger.warning(f"Category {category_name} wasn't found in db.")


async def get_category_info(
    async_session: AsyncSession,
    telegram_id: int,
    category_name: str,
) -> Optional[Category]:
    """
    Get category info from database.

    Args:
        async_session (AsyncSession): asynchronous session for connection with db
        telegram_id (int): user Telegram ID
        category_name (str): name of category

    Returns:
        Category: instance of Category table class with required category info
    """
    req = (
        select(Category)
        .join(Category.user_id)
        .where(User.telegram_id == telegram_id)
        .where(Category.category_name == category_name)
    )
    result = await async_session.execute(req)
    try:
        category_info = result.scalar_one()
        logger.info(f"Info for category {category_name} was got from db.")
        return category_info
    except NoResultFound:
        logger.warning(f"Info for category {category_name} wasn't found in db.")


async def add_expense(
    async_session: AsyncSession,
    expense_name: str,
    category_id: int,
) -> int:
    """
    Add new expense to database.

    Args:
        async_session (AsyncSession): asynchronous session for connection with db
        expense_name (str) - name of new expense
        category_id (str) - category ID of new expense

    Returns:
        int: new expense ID in database
    """
    async with async_session.begin():
        async_session.add(Expense(expense_name=expense_name, category_id=category_id))
        logger.info(f"Expense {expense_name} was added to db.")

    req = select(Expense).order_by(Expense.category_id.desc()).limit(1)
    result = await async_session.execute(req)
    try:
        expense_info = result.scalar_one()
        return expense_info.expense_id
    except NoResultFound:
        logger.warning(f"Expense {expense_name} wasn't found in db.")


async def get_expense_info(
    async_session: AsyncSession, telegram_id: int, expense_name: str
) -> Optional[Expense]:
    """
    Get expense information from database.

    Args:
        async_session (AsyncSession): asynchronous session for connection with db
        telegram_id (int): user Telegram ID
        expense_name (str): name of expense

    Returns:
        Expense: instance of Expense table class with required expense info
    """
    req = (
        select(Expense)
        .join(Expense.category_id)
        .join(Category.user_id)
        .where(Expense.expense_name == expense_name)
        .where(User.telegram_id == telegram_id)
    )
    result = await async_session.execute(req)
    try:
        expense_info = result.scalar_one()
        logger.info(f"Info for expense {expense_name} was got from db.")
        return expense_info
    except NoResultFound:
        logger.warning(f"Info for expense {expense_name} wasn't found in db.")


async def get_expense_category_name(
    async_session: AsyncSession, telegram_id: int, expense_name: str
) -> Optional[str]:
    """Get expense category name from database.

    Args:
        async_session (AsyncSession): asynchronous session for connection with db
        telegram_id (int): user telegram ID
        expense_name (str): expense name for which need to request category name

    Returns:
        Optional[str]: required category name or None if category name for requiered
            expense wasn't found in db
    """
    req = (
        select(Category.category_name)
        .join(Expense.category_id)
        .join(User.user_id)
        .where(Expense.expense_name == expense_name)
        .where(User.telegram_id == telegram_id)
    )
    result = await async_session.execute(req)
    try:
        expense_category_name = result.scalar_one()
        logger.info(
            f"Category name for expense {expense_name} for user {telegram_id} was "
            f"got from db."
        )
        return expense_category_name
    except NoResultFound:
        logger.info(
            f"Category for expense {expense_name} for user {telegram_id} wasn't "
            f"found in db."
        )


async def get_all_user_categories(
    async_session: AsyncSession, telegram_id: int
) -> Optional[list[str]]:
    """
    Get all categories names for required user from database.

    Args:
        async_session (AsyncSession): asynchronous session for connection with db
        telegram_id (int): user Telegram ID

    Returns:
        list[str]: list of categories names for required user if existed else None
    """
    req = select(Category).join(Category.user_id).where(User.telegram_id == telegram_id)
    result = await async_session.execute(req)

    categories_lst = []
    try:
        for category_info in result.scalars().all():
            categories_lst.append(category_info.category_name)
        logger.info(
            f"{len(categories_lst)} categories for user {telegram_id} were found in db."
        )
    except NoResultFound:
        logger.info(f"Noone category for user {telegram_id} wasn't found ib db.")


async def add_transaction(
    async_session: AsyncSession,
    telegram_id: int,
    expense_name: str,
    category_name: str,
    cost: float | int,
    created_date: datetime,
    amount: int,
    comment: str,
) -> None:
    """
    Add new transaction to database. Also add new category and new expense to database
    if required.

    Args:
        async_session (AsyncSession): asynchronous session for connection with db
        telegram_id (int): user Telegram ID
        expense_name (str): name of expense
        category_name (str): name of expense category
        cost (float): cost of expense
        created_date (date): date of expense
        amount (int): amount of expense
        comment (str): comment for expense
    """
    category_info = await get_category_info(async_session, telegram_id, category_name)
    if category_info:
        category_id = category_info.category_id
    else:
        category_id = await add_category(async_session, telegram_id, category_name)
    expense_info = await get_expense_info(async_session, telegram_id, expense_name)
    if not expense_info or expense_info.category_id != category_id:
        expense_id = await add_expense(async_session, expense_name, category_id)
    else:
        expense_id = expense_info.expense_id

    async with async_session.begin():
        async_session.add(
            Transaction(
                expense_id=expense_id,
                cost=cost,
                created_date=created_date,
                amount=amount,
                comment=comment,
            )
        )
        logger.info(f"Transaction for user {telegram_id} was added to db.")
