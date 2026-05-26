import bcrypt
import plotly.express as px
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import numpy as np

# ---------------- CONFIG ----------------
st.set_page_config("Business SaaS", layout="wide")

# ---------------- DB ----------------
def get_db():
    conn = sqlite3.connect("business.db", check_same_thread=False)
    return conn

def load_user_sales(user):
    conn = get_db()
    df = pd.read_sql_query(
        "SELECT * FROM sales WHERE user=? AND status='active'",
        conn,
        params=(user,)
    )
    conn.close()
    return df

# ---------------- SECURITY (FIXED) ----------------
def hash_password(password):
    # store as STRING (safe for SQLite)
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

def check_password(password, hashed):
    # convert back to bytes before checking
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================
# LOGIN / REGISTER
# =====================================================
if st.session_state.user is None:

    st.title("🔐 Business SaaS Login")

    mode = st.radio("Choose Option", ["Login", "Register"], key="auth_mode")

    username = st.text_input("Username", key="auth_user")
    password = st.text_input("Password", type="password", key="auth_pass")

    conn = get_db()
    cursor = conn.cursor()

    # ---------------- LOGIN ----------------
    if mode == "Login":

        if st.button("Login"):

            cursor.execute(
                "SELECT password FROM users WHERE username=?",
                (username,)
            )

            result = cursor.fetchone()

            if result and check_password(password, result[0]):
                st.session_state.user = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    # ---------------- REGISTER ----------------
    else:

        if st.button("Create Account"):

            try:
                hashed_password = hash_password(password)

                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_password)
                )

                conn.commit()
                st.success("Account created successfully")

            except:
                st.error("Username already exists")

    conn.close()
    st.stop()

# =====================================================
# AFTER LOGIN
# =====================================================
user = st.session_state.user

st.sidebar.title(f"Welcome {user}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

menu = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Add Sale", "Analytics", "Trash"]
)

df = load_user_sales(user)

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":

    st.title("📊 Business Analytics Dashboard")

    if df.empty:
        st.warning("No data yet")
    else:

        total_sales = len(df)
        total_profit = df["profit"].sum()
        total_products = df["product"].nunique()

        col1, col2, col3 = st.columns(3)

        col1.metric("Sales", total_sales)
        col2.metric("Profit", f"₦{total_profit:,.2f}")
        col3.metric("Products", total_products)

        st.subheader("📈 Profit by Product")

        product_profit = df.groupby("product")["profit"].sum().reset_index()

        st.plotly_chart(
            px.bar(product_profit, x="product", y="profit"),
            use_container_width=True
        )

        st.subheader("🥧 Product Share")

        st.plotly_chart(
            px.pie(product_profit, names="product", values="profit"),
            use_container_width=True
        )

        st.dataframe(product_profit)

# =====================================================
# ADD SALE
# =====================================================
elif menu == "Add Sale":

    st.title("➕ Add Sale")

    product = st.text_input("Product", key="product_input")
    quantity = st.number_input("Quantity", min_value=1, key="qty_input")
    cost = st.number_input("Cost Price", key="cost_input")
    selling = st.number_input("Selling Price", key="selling_input")

    if st.button("Save Sale"):

        profit = (selling - cost) * quantity
        date = datetime.now().strftime("%Y-%m-%d")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO sales (user, product, quantity, cost_price, selling_price, profit, date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
        """, (user, product, quantity, cost, selling, profit, date))

        conn.commit()
        conn.close()

        st.success(f"Saved! Profit: ₦{profit}")

# =====================================================
# ANALYTICS
# =====================================================
elif menu == "Analytics":

    st.title("📊 Analytics")

    if df.empty:
        st.warning("No data")
    else:

        df["date"] = pd.to_datetime(df["date"])
        monthly = df.groupby(df["date"].dt.to_period("M"))["profit"].sum()

        st.line_chart(monthly)

        st.subheader("🤖 Prediction")

        x = np.arange(len(monthly))
        y = monthly.values

        if len(x) > 1:
            trend = np.polyfit(x, y, 1)
            prediction = trend[0]*(len(x)+1) + trend[1]

            st.info(f"Next month: ₦{prediction:,.2f}")

# =====================================================
# TRASH
# =====================================================
elif menu == "Trash":

    st.title("🗑️ Deleted Records")

    conn = get_db()
    trash = pd.read_sql_query(
        "SELECT * FROM sales WHERE user=? AND status='deleted'",
        conn,
        params=(user,)
    )
    conn.close()

    st.dataframe(trash)

    restore_id = st.number_input("Restore ID", min_value=1)

    if st.button("Restore"):

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE sales
        SET status='active'
        WHERE id=? AND user=?
        """, (restore_id, user))

        conn.commit()
        conn.close()

        st.success("Restored")