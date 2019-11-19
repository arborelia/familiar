import sqlite3
import pkg_resources

DB_FILENAME = pkg_resources.resource_filename("data/quotes.db")
DB = sqlite3.connect(DB_FILENAME)


def run(cmd, *args):
    cursor = DB.cursor()
    cursor.execute(cmd, args)
    return cursor.fetchall()


def new_row(cmd, *args):
    cursor = DB.cursor()
    cursor.execute(cmd, args)
    return cursor.lastrowid


def _check_table_exists(table_name):
    cmd = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    return bool(_results_for(cmd))


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
        name TEXT NOT NULL,
        response TEXT NOT NULL
    )
    """)