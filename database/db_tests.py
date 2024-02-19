import logging
import os
import sqlite3
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    logging.basicConfig(level=logging.INFO)

from db_init import init_database
from db_requests import *

init_database(DATABASE_NAME)

add_user_to_db(2, "Nikita")
add_category_to_db(474783927, "Машина")
get_category_id_from_db(1, "Машина")
add_expense_to_db(1, "Продукты", "Молоко")
categories = get_all_user_categories(2)
