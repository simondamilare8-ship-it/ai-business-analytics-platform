import sqlite3

conn = sqlite3.connect("business.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM users")
conn.commit()
conn.close()