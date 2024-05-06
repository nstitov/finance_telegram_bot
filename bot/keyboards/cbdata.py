from aiogram.filters.callback_data import CallbackData


class CategoriesCallbackFactory(CallbackData, prefix="add_category"):
    category_name: str
