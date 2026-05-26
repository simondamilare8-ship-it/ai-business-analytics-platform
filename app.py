import bcrypt
import plotly.express as px
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import numpy as np
import smtplib
import random
import string

# ================= CONFIG =================
st.set_page_config("Business SaaS", layout="wide")

# ================= EMAIL CONFIG =================
EMAIL_SENDER = "simondamilare8@gmail.com"
EMAIL_PASSWORD = "dayq ehyw cbvf ltfd"  # Gmail App Password

# temporary reset storage (for demo)
if "reset_code" not in st.session_state:
    st.session_state.reset_code = None
if "reset_user" not in st.session_state:
    st.session_state.reset_user = None

# ================= DB =================
def get_db():
    return sqlite3.connect("business.db", check_same_thread=False)

def load_user_sales(user):
    conn = get_db()
    df = pd.read_sql_query(
        "SELECT * FROM sales WHERE user=? AND status='active'",
        conn,
        params=(user,)
    )
    conn.close()
    return df

# ================= SECURITY =================
def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

# ================= EMAIL FUNCTION =================
def send_email(receiver, subject, message):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        msg = f"Subject: {subject}\n\n{message}"
        server.sendmail(EMAIL_SENDER, receiver, msg)
        server.quit()
        return True
    except:
        return False

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================
# AUTH SYSTEM
# =====================================================
if st.session_state.user is None:

    st.title("🔐 Business SaaS Login")

    mode = st.radio(
        "Choose Option",
        ["Login", "Register", "Forgot Password"],
        key="auth_mode"
    )

    conn = get_db()
    cursor = conn.cursor()

    # =================================================
    # REGISTER
    # =================================================
    if mode == "Register":

        username = st.text_input("Username", key="r_user")
        password = st.text_input("Password", type="password", key="r_pass")
        email = st.text_input("Email", key="r_email")

        if st.button("Create Account"):

            try:
                hashed = hash_password(password)

                cursor.execute(
                    "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                    (username, hashed, email)
                )

                conn.commit()
                st.success("Account created successfully")

            except:
                st.error("User already exists")

    # =================================================
    # LOGIN
    # =================================================
    elif mode == "Login":

        username = st.text_input("Username", key="l_user")
        password = st.text_input("Password", type="password", key="l_pass")

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

    # =================================================
    # FORGOT PASSWORD (EMAIL RESET)
    # =================================================
    elif mode == "Forgot Password":

        username = st.text_input("Username", key="f_user")

        if st.button("Send Reset Code"):

            cursor.execute(
                "SELECT email FROM users WHERE username=?",
                (username,)
            )

            result = cursor.fetchone()

            if result:
                email = result[0]

                code = "".join(random.choices(string.digits, k=6))

                st.session_state.reset_code = code
                st.session_state.reset_user = username

                send_email(
                    email,
                    "Password Reset Code",
                    f"Your reset code is: {code}"
                )

                st.success("Reset code sent to your email")

            else:
                st.error("User not found")

        if st.session_state.reset_code:

            code_input = st.text_input("Enter Reset Code")
            new_pass = st.text_input("New Password", type="password")

            if st.button("Reset Password"):

                if code_input == st.session_state.reset_code:

                    hashed = hash_password(new_pass)

                    cursor.execute(
                        "UPDATE users SET password=? WHERE username=?",
                        (hashed, st.session_state.reset_user)
                    )

                    conn.commit()

                    st.success("Password updated successfully")

                    st.session_state.reset_code = None
                    st.session_state.reset_user = None

                else:
                    st.error("Invalid reset code")

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

# 👇 ADD THIS HERE
if st.sidebar.button("🗑 Clear Data (Soft)"):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sales
        SET status='deleted'
        WHERE user=?
    """, (user,))

    conn.commit()
    conn.close()

    st.success("Moved to Trash")
    st.rerun()

menu = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Add Sale", "Analytics", "History", "Trash"]
)

# 🔥 FIX: LOAD DATA HERE (THIS IS WHAT YOU ARE MISSING)
df = load_user_sales(user)
# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":

    st.title("📊 Dashboard")

    if df.empty:
        st.warning("No data yet")
    else:

        col1, col2, col3 = st.columns(3)

        col1.metric("Sales", len(df))
        col2.metric("Profit", f"₦{df['profit'].sum():,.2f}")
        col3.metric("Products", df["product"].nunique())

        product_profit = df.groupby("product")["profit"].sum().reset_index()

        st.plotly_chart(px.bar(product_profit, x="product", y="profit"))

        st.plotly_chart(px.pie(product_profit, names="product", values="profit"))

# =====================================================
# ADD SALE
# =====================================================
elif menu == "Add Sale":

    st.title("➕ Add Sale")

    product = st.text_input("Product", key="p1")
    quantity = st.number_input("Quantity", min_value=1)
    cost = st.number_input("Cost Price")
    selling = st.number_input("Selling Price")

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

        st.success("Saved successfully")

# =====================================================
# ANALYTICS
# =====================================================
elif menu == "Analytics":

    st.title("📊 Analytics")

    if not df.empty:

        df["date"] = pd.to_datetime(df["date"])
        monthly = df.groupby(df["date"].dt.to_period("M"))["profit"].sum()

        st.line_chart(monthly)

        x = np.arange(len(monthly))
        y = monthly.values

        if len(x) > 1:
            trend = np.polyfit(x, y, 1)
            st.info(f"Next month prediction: ₦{trend[0]*(len(x)+1)+trend[1]:,.2f}")
elif menu == "History":

    st.title("📅 Transaction History")

    # convert date column
    df["date"] = pd.to_datetime(df["date"])

    # ---------------- FILTER OPTIONS ----------------
    view_type = st.selectbox(
        "Select View",
        ["Daily", "Monthly", "Yearly"]
    )

    if view_type == "Daily":

        selected_date = st.date_input("Pick Date")

        filtered = df[df["date"].dt.date == selected_date]

    elif view_type == "Monthly":

        df["month"] = df["date"].dt.to_period("M")
        selected_month = st.selectbox("Select Month", df["month"].unique())

        filtered = df[df["date"].dt.to_period("M") == selected_month]

    else:  # Yearly

        df["year"] = df["date"].dt.year
        selected_year = st.selectbox("Select Year", df["year"].unique())

        filtered = df[df["date"].dt.year == selected_year]

    # ---------------- DISPLAY ----------------
    st.subheader("Transactions")

    st.dataframe(filtered)

    # ---------------- SUMMARY ----------------
    st.subheader("Summary")

    st.metric("Total Sales", len(filtered))
    st.metric("Total Profit", f"₦{filtered['profit'].sum():,.2f}" if not filtered.empty else "₦0")
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