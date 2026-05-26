import sqlite3

conn = sqlite3.connect("business.db")
cursor = conn.cursor()

# wipe only users table (recommended)
cursor.execute("DELETE FROM users")

conn.commit()
conn.close()

print("Users table reset successfully")