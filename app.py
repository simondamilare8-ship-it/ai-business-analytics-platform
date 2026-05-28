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

from prophet import Prophet
from sklearn.cluster import KMeans

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

# ================= LOAD DATA =================
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

            if not username or not email or not password:
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

            cursor.execute("SELECT password FROM users WHERE username=?", (username,))
            result = cursor.fetchone()

            if result and check_password(password, result[0]):
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

    conn.close()
    st.stop()

# ================= AFTER LOGIN =================
user = st.session_state.user

st.sidebar.title(f"👤 Welcome {user}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

if st.sidebar.button("🗑 Clear Data (Soft)"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE sales SET status='deleted' WHERE username=?", (user,))
    conn.commit()
    conn.close()
    st.success("Moved to Trash")
    st.rerun()

menu = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Add Sale", "Analytics", "History", "Trash", "AI Upload"]
)

df = load_sales(user)

# ================= DASHBOARD =================
if menu == "Dashboard":

    st.title("📊 Dashboard")

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

        if len(monthly) > 1:
            x = np.arange(len(monthly))
            y = monthly.values

            model = np.polyfit(x, y, 1)
            st.info(f"Next month prediction: ₦{model[0]*(len(x)+1)+model[1]:,.2f}")

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
        cursor.execute("UPDATE sales SET status='active' WHERE username=?", (user,))
        conn.commit()
        conn.close()
        st.success("Restored")
        st.rerun()

    if st.button("Delete Forever"):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sales WHERE username=? AND status='deleted'", (user,))
        conn.commit()
        conn.close()
        st.success("Deleted permanently")
        st.rerun()

# ================= AI BRAIN =================
elif menu == "AI Upload":

    st.title("🧠 AI Business Brain (Forecast + Insights + Segmentation)")

    file = st.file_uploader("Upload Excel File", type=["xlsx"])

    if file:

        df_ai = pd.read_excel(file)
        st.subheader("📄 Data Preview")
        st.dataframe(df_ai)

        required = ["date", "product", "quantity", "cost_price", "selling_price"]

        if not all(col in df_ai.columns for col in required):
            st.error(f"Missing columns: {required}")

        else:
            # ================= CLEAN DATA =================
            df_ai["date"] = pd.to_datetime(df_ai["date"], errors="coerce")
            df_ai = df_ai.dropna(subset=["date"])

            df_ai["quantity"] = pd.to_numeric(df_ai["quantity"], errors="coerce").fillna(0)
            df_ai["cost_price"] = pd.to_numeric(df_ai["cost_price"], errors="coerce").fillna(0)
            df_ai["selling_price"] = pd.to_numeric(df_ai["selling_price"], errors="coerce").fillna(0)

            df_ai["profit"] = (df_ai["selling_price"] - df_ai["cost_price"]) * df_ai["quantity"]

            st.success("Data processed for AI Brain ✅")

            # =====================================================
            # 📊 1. BUSINESS SUMMARY
            # =====================================================
            st.subheader("📊 Business Summary")

            total_profit = df_ai["profit"].sum()
            total_qty = df_ai["quantity"].sum()
            product_count = df_ai["product"].nunique()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Profit", f"₦{total_profit:,.2f}")
            col2.metric("Total Quantity Sold", total_qty)
            col3.metric("Products", product_count)

            # =====================================================
            # 📈 2. FORECASTING (PROPhet SAFE)
            # =====================================================
            st.subheader("📈 Profit Forecast")

            from prophet import Prophet

            sales = df_ai.groupby("date")["profit"].sum().reset_index()
            sales.columns = ["ds", "y"]
            sales = sales.sort_values("ds")

            if len(sales) < 10:
                st.warning("Need at least 10 days of data for strong AI forecasting")
            else:
                model = Prophet()
                model.fit(sales)

                future = model.make_future_dataframe(periods=30)
                forecast = model.predict(future)

                st.line_chart(forecast[["ds", "yhat"]])

                st.success(
                    f"Next 30 days predicted profit: ₦{forecast['yhat'].tail(30).sum():,.2f}"
                )

            # =====================================================
            # 🧾 3. PRODUCT PERFORMANCE ANALYSIS
            # =====================================================
            st.subheader("🧾 Product Intelligence")

            product_stats = df_ai.groupby("product").agg({
                "quantity": "sum",
                "profit": "sum"
            }).reset_index()

            best = product_stats.sort_values("profit", ascending=False).head(5)
            worst = product_stats.sort_values("profit", ascending=True).head(5)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🔥 Top Products")
                st.dataframe(best)

            with col2:
                st.markdown("### ⚠️ Low Performing Products")
                st.dataframe(worst)

            st.bar_chart(product_stats.set_index("product")["profit"])

            # =====================================================
            # 👥 4. SEGMENTATION (KMEANS)
            # =====================================================
            st.subheader("👥 Smart Segmentation")

            from sklearn.cluster import KMeans

            cluster_data = df_ai.groupby("product").agg({
                "quantity": "sum",
                "profit": "sum"
            }).reset_index()

            if len(cluster_data) < 2:
                st.warning("Not enough data for segmentation")
            else:
                k = min(3, len(cluster_data))

                kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
                cluster_data["segment"] = kmeans.fit_predict(
                    cluster_data[["quantity", "profit"]]
                )

                st.dataframe(cluster_data)

                fig = px.scatter(
                    cluster_data,
                    x="quantity",
                    y="profit",
                    color="segment",
                    hover_name="product",
                    title="AI Product Clusters"
                )

                st.plotly_chart(fig, use_container_width=True)

            # =====================================================
            # 🧠 5. AI BUSINESS INSIGHTS ENGINE
            # =====================================================
            st.subheader("🧠 AI Insights")

            if not product_stats.empty:

                top_product = best.iloc[0]["product"]
                low_product = worst.iloc[0]["product"]

                st.success(f"💡 Focus more on '{top_product}' — it is your best performer.")

                st.warning(f"⚠️ Review '{low_product}' — it is underperforming.")

                if total_profit < 0:
                    st.error("Your business is currently making a loss. Review pricing strategy.")
                elif total_profit > 0:
                    st.info("Your business is profitable. Keep scaling 📈")