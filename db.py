import sqlite3


_connection = None


def get_connection():
    """gets connection to file"""
    global _connection
    if _connection is None:
        _connection = sqlite3.connect('currencies.db')
    return _connection


def init_currency_db(force: bool = False):
    """creates currency_list db"""
    conn = get_connection()
    c = conn.cursor()
    if force:
        c.execute('DROP TABLE IF EXISTS currency_list')
    c.execute('''
        CREATE TABLE IF NOT EXISTS currency_list (
            currency   TEXT NOT NULL,
            value      TEXT NOT NULL
        )
    ''')
    conn.commit()


def add_list_of_currencies(list_of_currencies):
    """adds data to currency_list db"""
    conn = get_connection()
    c = conn.cursor()
    sqlite_insert_query = """INSERT INTO currency_list
                                     (currency, value)
                                     VALUES (?, ?);"""
    c.executemany(sqlite_insert_query, list_of_currencies)
    conn.commit()


def get_data_from_currency_bd():
    """gets currency name and its value from currency_list db"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM currency_list")
    return c.fetchall()


def init_timestamp_db(force: bool = False):
    """creates timestamp db"""
    conn = get_connection()
    c = conn.cursor()
    if force:
        c.execute('DROP TABLE IF EXISTS timestamp')
    c.execute('''
        CREATE TABLE IF NOT EXISTS timestamp (
            id         PRIMARY KEY,
            time       REAL DEFAULT 1 NOT NULL
        )
    ''')
    conn.commit()


def add_timestamp_to_db(timestamp):
    """adds first time to timestamp db"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO timestamp(time) VALUES(?);", (timestamp,))
    conn.commit()


def update_timestamp_in_db(timestamp):
    """updates time in timestamp db"""
    conn = get_connection()
    c = conn.cursor()
    # c.execute("INSERT INTO timestamp(time) VALUES(?);", (timestamp,))
    c.execute(f"UPDATE timestamp SET time={timestamp} WHERE id=1")
    conn.commit()


def get_data_from_timestamp_db():
    """gets timestamp from timestamp db"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT time FROM timestamp")
    return c.fetchone()
