import sqlite3

conn = sqlite3.connect("business.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE sales ADD COLUMN date TEXT")
    print("Date column added successfully")
except Exception as e:
    print(e)

conn.commit()
conn.close()