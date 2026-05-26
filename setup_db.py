import sqlite3

conn = sqlite3.connect("business.db")
cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    plan TEXT DEFAULT 'free'
)
""")

# SALES TABLE (USER-ISOLATED)
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    product TEXT,
    quantity INTEGER,
    cost_price REAL,
    selling_price REAL,
    profit REAL,
    date TEXT,
    status TEXT DEFAULT 'active'
)
""")

conn.commit()
conn.close()

print("Database ready for SaaS")