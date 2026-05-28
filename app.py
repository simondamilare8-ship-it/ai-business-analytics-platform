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
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]  # Gmail App Password

# ================= SESSION DEFAULTS =================
if "reset_code" not in st.session_state:
    st.session_state.reset_code = None
if "reset_user" not in st.session_state:
    st.session_state.reset_user = None
if "user" not in st.session_state:
    st.session_state.user = None

# ================= DB =================
def get_db():
    return sqlite3.connect("business.db", check_same_thread=False)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            cost_price REAL NOT NULL,
            selling_price REAL NOT NULL,
            profit REAL NOT NULL,
            date TEXT NOT NULL,
            status TEXT DEFAULT 'active'
        )
    """)
    conn.commit()
    conn.close()

# Run DB init on every startup
init_db()

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
    except Exception as e:
        st.error(f"Email error: {e}")
        return False

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
        email = st.text_input("Email", key="r_email")
        password = st.text_input("Password", type="password", key="r_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="r_confirm")

        if st.button("Create Account"):

            if username.strip() == "" or password.strip() == "" or email.strip() == "":
                st.warning("All fields are required.")

            elif password != confirm_password:
                st.warning("Passwords do not match.")

            else:
                # ✅ Check if username already exists BEFORE inserting
                cursor.execute("SELECT id FROM users WHERE username=?", (username,))
                existing_user = cursor.fetchone()

                # ✅ Also check if email already exists
                cursor.execute("SELECT id FROM users WHERE email=?", (email,))
                existing_email = cursor.fetchone()

                if existing_user:
                    st.error("❌ Username already exists. Please choose a different username.")

                elif existing_email:
                    st.error("❌ Email already registered. Please use a different email or login.")

                else:
                    hashed = hash_password(password)
                    cursor.execute(
                        "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                        (username, hashed, email)
                    )
                    conn.commit()
                    st.success("✅ Account created successfully! You can now login.")

    # =================================================
    # LOGIN
    # =================================================
    elif mode == "Login":

        username = st.text_input("Username", key="l_user")
        password = st.text_input("Password", type="password", key="l_pass")

        if st.button("Login"):

            if username.strip() == "" or password.strip() == "":
                st.warning("Please enter your username and password.")
            else:
                cursor.execute(
                    "SELECT password FROM users WHERE username=?",
                    (username,)
                )
                result = cursor.fetchone()

                if result and check_password(password, result[0]):
                    st.session_state.user = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    # =================================================
    # FORGOT PASSWORD (EMAIL RESET)
    # =================================================
    elif mode == "Forgot Password":

        username = st.text_input("Username", key="f_user")

        if st.button("Send Reset Code"):

            if username.strip() == "":
                st.warning("Please enter your username.")
            else:
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

                    sent = send_email(
                        email,
                        "Password Reset Code",
                        f"Your reset code is: {code}\n\nThis code is valid for this session only."
                    )

                    if sent:
                        st.success("✅ Reset code sent to your email.")
                    else:
                        st.error("Failed to send email. Check your email config.")
                else:
                    st.error("Username not found.")

        if st.session_state.reset_code:

            code_input = st.text_input("Enter Reset Code", key="reset_code_input")
            new_pass = st.text_input("New Password", type="password", key="new_pass")
            confirm_new = st.text_input("Confirm New Password", type="password", key="confirm_new")

            if st.button("Reset Password"):

                if new_pass != confirm_new:
                    st.warning("Passwords do not match.")

                elif code_input == st.session_state.reset_code:
                    hashed = hash_password(new_pass)
                    cursor.execute(
                        "UPDATE users SET password=? WHERE username=?",
                        (hashed, st.session_state.reset_user)
                    )
                    conn.commit()
                    st.success("✅ Password updated successfully. You can now login.")
                    st.session_state.reset_code = None
                    st.session_state.reset_user = None
                else:
                    st.error("Invalid reset code.")

    conn.close()
    st.stop()

# =====================================================
# AFTER LOGIN
# =====================================================
user = st.session_state.user

st.sidebar.title(f"👤 Welcome, {user}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

if st.sidebar.button("🗑 Clear Data (Soft Delete)"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE sales SET status='deleted' WHERE user=?
    """, (user,))
    conn.commit()
    conn.close()
    st.success("Moved to Trash.")
    st.rerun()

menu = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Add Sale", "Analytics", "History", "Trash"]
)

# Load active sales for this user
df = load_user_sales(user)

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":

    st.title("📊 Dashboard")

    if df.empty:
        st.warning("No sales data yet. Go to 'Add Sale' to get started.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sales", len(df))
        col2.metric("Total Profit", f"₦{df['profit'].sum():,.2f}")
        col3.metric("Unique Products", df["product"].nunique())

        product_profit = df.groupby("product")["profit"].sum().reset_index()

        st.plotly_chart(px.bar(product_profit, x="product", y="profit", title="Profit by Product"), use_container_width=True)
        st.plotly_chart(px.pie(product_profit, names="product", values="profit", title="Profit Share"), use_container_width=True)

# =====================================================
# ADD SALE
# =====================================================
elif menu == "Add Sale":

    st.title("➕ Add Sale")

    product = st.text_input("Product Name", key="p1")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    cost = st.number_input("Cost Price (₦)", min_value=0.0, format="%.2f")
    selling = st.number_input("Selling Price (₦)", min_value=0.0, format="%.2f")

    if st.button("Save Sale"):

        if product.strip() == "":
            st.warning("Please enter a product name.")
        elif selling < cost:
            st.warning("⚠️ Selling price is less than cost price. You will make a loss.")
        else:
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

            st.success(f"✅ Sale saved! Profit: ₦{profit:,.2f}")

# =====================================================
# ANALYTICS
# =====================================================
elif menu == "Analytics":

    st.title("📈 Analytics")

    if df.empty:
        st.warning("No data to analyse yet.")
    else:
        df["date"] = pd.to_datetime(df["date"])
        monthly = df.groupby(df["date"].dt.to_period("M"))["profit"].sum()

        st.subheader("Monthly Profit Trend")
        st.line_chart(monthly)

        x = np.arange(len(monthly))
        y = monthly.values

        if len(x) > 1:
            trend = np.polyfit(x, y, 1)
            prediction = trend[0] * (len(x) + 1) + trend[1]
            st.info(f"📌 Predicted next month profit: ₦{prediction:,.2f}")
        else:
            st.info("Add more months of data to see profit predictions.")

# =====================================================
# HISTORY
# =====================================================
elif menu == "History":

    st.title("📅 Transaction History")

    if df.empty:
        st.warning("No transaction history yet.")
    else:
        df["date"] = pd.to_datetime(df["date"])

        view_type = st.selectbox("Select View", ["Daily", "Monthly", "Yearly"])

        if view_type == "Daily":
            selected_date = st.date_input("Pick Date")
            filtered = df[df["date"].dt.date == selected_date]

        elif view_type == "Monthly":
            df["month"] = df["date"].dt.to_period("M")
            month_options = df["month"].unique().tolist()
            selected_month = st.selectbox("Select Month", month_options)
            filtered = df[df["date"].dt.to_period("M") == selected_month]

        else:  # Yearly
            df["year"] = df["date"].dt.year
            year_options = df["year"].unique().tolist()
            selected_year = st.selectbox("Select Year", year_options)
            filtered = df[df["date"].dt.year == selected_year]

        st.subheader("Transactions")
        st.dataframe(filtered, use_container_width=True)

        st.subheader("Summary")
        col1, col2 = st.columns(2)
        col1.metric("Total Sales", len(filtered))
        col2.metric("Total Profit", f"₦{filtered['profit'].sum():,.2f}" if not filtered.empty else "₦0.00")

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

    if trash.empty:
        st.info("Trash is empty.")
    else:
        st.dataframe(trash, use_container_width=True)

        if st.button("♻️ Restore All"):
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sales SET status='active' WHERE user=? AND status='deleted'",
                (user,)
            )
            conn.commit()
            conn.close()
            st.success("All records restored.")
            st.rerun()

        if st.button("🗑 Delete Permanently"):
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM sales WHERE user=? AND status='deleted'",
                (user,)
            )
            conn.commit()
            conn.close()
            st.success("Permanently deleted.")
            st.rerun()