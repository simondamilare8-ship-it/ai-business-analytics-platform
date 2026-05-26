import sqlite3

DB_NAME = "business.db"


# =========================
# CONNECT DATABASE
# =========================
def get_connection():
    return sqlite3.connect(DB_NAME)


# =========================
# INITIALIZE TABLE SAFELY
# =========================
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT,
            amount REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            deleted_at TEXT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully")


# =========================
# ADD COLUMN SAFELY (for old DBs)
# =========================
def add_missing_columns():
    conn = get_connection()
    cursor = conn.cursor()

    # Helper function to check column existence
    def column_exists(column_name):
        cursor.execute("PRAGMA table_info(sales)")
        columns = [col[1] for col in cursor.fetchall()]
        return column_name in columns

    try:
        if not column_exists("status"):
            cursor.execute("ALTER TABLE sales ADD COLUMN status TEXT DEFAULT 'active'")
            print("status column added")

        if not column_exists("deleted_at"):
            cursor.execute("ALTER TABLE sales ADD COLUMN deleted_at TEXT NULL")
            print("deleted_at column added")

    except Exception as e:
        print("Migration error:", e)

    conn.commit()
    conn.close()


# =========================
# SOFT DELETE FUNCTION
# =========================
def soft_delete(record_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sales
        SET status = 'deleted',
            deleted_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (record_id,))

    conn.commit()
    conn.close()


# =========================
# RESTORE FUNCTION (NEW)
# =========================
def restore_record(record_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sales
        SET status = 'active',
            deleted_at = NULL
        WHERE id = ?
    """, (record_id,))

    conn.commit()
    conn.close()


# =========================
# FETCH DATA
# =========================
def fetch_active():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sales WHERE status = 'active'")
    data = cursor.fetchall()

    conn.close()
    return data


def fetch_deleted():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sales WHERE status = 'deleted'")
    data = cursor.fetchall()

    conn.close()
    return data


# =========================
# RUN SETUP
# =========================
init_db()
add_missing_columns()