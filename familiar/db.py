import sqlite3
import pkg_resources

DB_FILENAME = pkg_resources.resource_filename(__name__, "data/quotes.db")
print(DB_FILENAME)
DB = sqlite3.connect(DB_FILENAME)
IntegrityError = sqlite3.IntegrityError


def run(cmd, *args):
    cursor = DB.cursor()
    cursor.execute(cmd, args)
    return cursor.fetchall()


def new_row(cmd, *args):
    cursor = DB.cursor()
    cursor.execute(cmd, args)
    rowid = cursor.lastrowid
    DB.commit()
    return rowid


def _check_table_exists(table_name):
    cmd = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    return bool(run(cmd, table_name))


def init_tables():
    if not _check_table_exists('quotes'):
        DB.execute("""
        CREATE TABLE quotes (
            id INTEGER NOT NULL PRIMARY KEY,
            quote TEXT NOT NULL,
            user TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """)


    if not _check_table_exists('commands'):
        DB.execute("""
        CREATE TABLE commands (
            name TEXT UNIQUE NOT NULL,
            response TEXT NOT NULL
        )
        """)

init_tables()