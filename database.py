import psycopg2
import streamlit as st


def create_tables():

    conn = psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        port=st.secrets["DB_PORT"]
    )

    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)

    # CATEGORIES TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            category TEXT,
            subcategory TEXT,
            type TEXT
        );
    """)

    # ACCOUNTS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            account_name TEXT,
            account_type TEXT,
            opening_balance FLOAT,
            include_in_networth INTEGER
        );
    """)

    # TRANSACTIONS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            date DATE,
            type TEXT,
            category TEXT,
            subcategory TEXT,
            account INTEGER,
            amount FLOAT,
            signed_amount FLOAT,
            tag TEXT,
            notes TEXT,
            created_at TIMESTAMP
        );
    """)

    # BUDGETS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            category TEXT,
            monthly_budget FLOAT
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
