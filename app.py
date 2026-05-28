import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import bcrypt
import smtplib
import random
import string
import plotly.express as px
from datetime import datetime

# ================= CONFIG =================
st.set_page_config(page_title="Business SaaS", layout="wide")

# ================= EMAIL CONFIG =================
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]

# ================= SESSION STATE =================
for key in ["user", "reset_code", "reset_user"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ================= DATABASE =================
DB_PATH = "business.db"

def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # ❗ DO NOT DROP TABLES (this was breaking your login)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
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

init_db()

# ================= LOAD SALES =================
def load_sales(username):
    conn = get_db()
    df = pd.read_sql_query(
        "SELECT * FROM sales WHERE username=? AND status='active'",
        conn,
        params=(username,)
    )
    conn.close()
    return df

# ================= SECURITY =================
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ================= EMAIL =================
def send_email(to, subject, message):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        msg = f"Subject: {subject}\n\n{message}"
        server.sendmail(EMAIL_SENDER, to, msg)
        server.quit()
        return True
    except:
        return False

# ================= AUTH =================
if st.session_state.user is None:

    st.title("🔐 Business SaaS Login")

    mode = st.radio("Choose Option", ["Login", "Register", "Forgot Password"])

    conn = get_db()
    cursor = conn.cursor()

    # ---------------- REGISTER ----------------
    if mode == "Register":

        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Create Account"):

            if not username or not password or not email:
                st.warning("Fill all fields")

            elif password != confirm:
                st.warning("Passwords do not match")

            else:
                cursor.execute("SELECT username FROM users WHERE username=?", (username,))
                if cursor.fetchone():
                    st.error("Username already exists")
                else:
                    hashed = hash_password(password)
                    cursor.execute(
                        "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                        (username, hashed, email)
                    )
                    conn.commit()
                    st.success("Account created successfully!")

    # ---------------- LOGIN ----------------
    elif mode == "Login":

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if not username or not password:
                st.warning("Enter login details")
            else:
                cursor.execute("SELECT password FROM users WHERE username=?", (username,))
                result = cursor.fetchone()

                if result and check_password(password, result[0]):
                    st.session_state.user = username
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    # ---------------- RESET PASSWORD ----------------
    elif mode == "Forgot Password":

        username = st.text_input("Username")

        if st.button("Send Code"):

            cursor.execute("SELECT email FROM users WHERE username=?", (username,))
            user = cursor.fetchone()

            if user:
                code = "".join(random.choices(string.digits, k=6))
                st.session_state.reset_code = code
                st.session_state.reset_user = username

                send_email(user[0], "Reset Code", f"Your code: {code}")
                st.success("Reset code sent")
            else:
                st.error("User not found")

        if st.session_state.reset_code:

            code_input = st.text_input("Enter Code")
            new_pass = st.text_input("New Password", type="password")

            if st.button("Reset Password"):

                if code_input == st.session_state.reset_code:

                    hashed = hash_password(new_pass)

                    cursor.execute(
                        "UPDATE users SET password=? WHERE username=?",
                        (hashed, st.session_state.reset_user)
                    )

                    conn.commit()

                    st.success("Password updated")
                    st.session_state.reset_code = None
                    st.session_state.reset_user = None

                else:
                    st.error("Wrong code")

    conn.close()
    st.stop()

# ================= AFTER LOGIN =================
user = st.session_state.user

st.sidebar.title(f"Welcome {user}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

if st.sidebar.button("🗑 Clear Data (Soft)"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE sales SET status='deleted' WHERE username=?",
        (user,)
    )
    conn.commit()
    conn.close()
    st.success("Moved to Trash")
    st.rerun()

menu = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Add Sale", "Analytics", "History", "Trash"]
)

df = load_sales(user)

# ================= DASHBOARD =================
if menu == "Dashboard":

    st.title("Dashboard")

    if df.empty:
        st.warning("No data yet")
    else:
        c1, c2, c3 = st.columns(3)

        c1.metric("Sales", len(df))
        c2.metric("Profit", f"₦{df['profit'].sum():,.2f}")
        c3.metric("Products", df["product"].nunique())

        summary = df.groupby("product")["profit"].sum().reset_index()

        st.plotly_chart(px.bar(summary, x="product", y="profit"), use_container_width=True)

# ================= ADD SALE =================
elif menu == "Add Sale":

    st.title("Add Sale")

    product = st.text_input("Product")
    qty = st.number_input("Quantity", min_value=1)
    cost = st.number_input("Cost Price")
    sell = st.number_input("Selling Price")

    if st.button("Save"):

        profit = (sell - cost) * qty
        date = datetime.now().strftime("%Y-%m-%d")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sales (username, product, quantity, cost_price, selling_price, profit, date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
        """, (user, product, qty, cost, sell, profit, date))

        conn.commit()
        conn.close()

        st.success("Saved successfully")

# ================= ANALYTICS =================
elif menu == "Analytics":

    st.title("Analytics")

    if not df.empty:

        df["date"] = pd.to_datetime(df["date"])
        monthly = df.groupby(df["date"].dt.to_period("M"))["profit"].sum()

        st.line_chart(monthly)

        x = np.arange(len(monthly))
        y = monthly.values

        if len(x) > 1:
            trend = np.polyfit(x, y, 1)
            st.info(f"Next month: ₦{trend[0]*(len(x)+1)+trend[1]:,.2f}")

# ================= HISTORY =================
elif menu == "History":

    st.title("History")

    if df.empty:
        st.warning("No history")
    else:

        df["date"] = pd.to_datetime(df["date"])

        option = st.selectbox("View", ["Daily", "Monthly", "Yearly"])

        if option == "Daily":
            d = st.date_input("Pick date")
            filtered = df[df["date"].dt.date == d]

        elif option == "Monthly":
            df["month"] = df["date"].dt.to_period("M")
            m = st.selectbox("Month", df["month"].unique())
            filtered = df[df["date"].dt.to_period("M") == m]

        else:
            df["year"] = df["date"].dt.year
            y = st.selectbox("Year", df["year"].unique())
            filtered = df[df["date"].dt.year == y]

        st.dataframe(filtered)
        st.metric("Total", len(filtered))
        st.metric("Profit", f"₦{filtered['profit'].sum():,.2f}")

# ================= TRASH =================
elif menu == "Trash":

    st.title("Trash")

    conn = get_db()
    trash = pd.read_sql_query(
        "SELECT * FROM sales WHERE username=? AND status='deleted'",
        conn,
        params=(user,)
    )
    conn.close()

    st.dataframe(trash)

    if st.button("Restore All"):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sales SET status='active' WHERE username=?",
            (user,)
        )
        conn.commit()
        conn.close()
        st.success("Restored")
        st.rerun()

    if st.button("Delete Forever"):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM sales WHERE username=? AND status='deleted'",
            (user,)
        )
        conn.commit()
        conn.close()
        st.success("Deleted permanently")
        st.rerun()