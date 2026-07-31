import streamlit as st
import sqlite3
import os
import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="ExpenseIQ",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core Folders Setup
UPLOAD_BASE_DIR = os.path.join("data", "uploads")
os.makedirs(UPLOAD_BASE_DIR, exist_ok=True)
DB_PATH = os.path.join("data", "expenseiq.db")

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statements (
            statement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bank TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            upload_datetime TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- DATABASE HELPER FUNCTIONS ---
def add_user(first_name, last_name, email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
            (first_name, last_name, email, password)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user  

def save_statement_metadata(user_id, bank, orig_name, stored_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO statements (user_id, bank, original_filename, stored_filename, upload_datetime, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, bank, orig_name, stored_name, now_str, "Uploaded"))
    conn.commit()
    conn.close()

def get_user_statements(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT statement_id, bank, original_filename, upload_datetime, status, stored_filename 
        FROM statements WHERE user_id = ?
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_statement_from_db(statement_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM statements WHERE statement_id = ?", (statement_id,))
    conn.commit()
    conn.close()