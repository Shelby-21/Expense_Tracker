import sqlite3


def create_tables():

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()


    # USERS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)


    # CATEGORIES

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        category TEXT,
        subcategory TEXT,
        type TEXT,
        active INTEGER DEFAULT 1
    )
    """)


    # ACCOUNTS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        account_name TEXT,
        account_type TEXT,
        opening_balance REAL,
        include_in_networth INTEGER DEFAULT 1
    )
    """)


    # TRANSACTIONS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        type TEXT,
        category TEXT,
        subcategory TEXT,
        account INTEGER,
        amount REAL,
        signed_amount REAL,
        tag TEXT,
        notes TEXT,
        created_at TEXT
    )
    """)


    # BUDGET MASTER

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        category TEXT,
        monthly_budget REAL
    )
    """)


    conn.commit()
    conn.close()