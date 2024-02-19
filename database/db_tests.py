import logging
import os
import sqlite3
import sys
from datetime import date

if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    logging.basicConfig(level=logging.INFO)

from db_init import init_database
from db_requests import *

init_database(DATABASE_NAME)

add_transaction_to_db(474783927, "Молоко", "Продукты", 100, date.today(), 1, None)
