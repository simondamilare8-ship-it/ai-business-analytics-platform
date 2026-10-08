import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import bcrypt
import smtplib
import plotly.express as px
import plotly.graph_objects as go

from datetime import datetime
from io import BytesIO
import re


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Growth Network",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL STYLES
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Instrument+Serif:ital@0;1&display=swap');
:root{--white:#fff;--bg:#f5f7ff;--card:#fff;--border:#e4e9f7;--purple:#6c63ff;--purple-light:#ede9ff;--purple-dark:#4b44cc;--teal:#00c9a7;--teal-light:#e0faf5;--gold:#f5a623;--red:#ff5c72;--text:#1a1f36;--text-muted:#6b7280;--text-soft:#9ca3af;--shadow-sm:0 2px 8px rgba(108,99,255,.08);--shadow-md:0 6px 24px rgba(108,99,255,.13);--radius:16px;--radius-sm:10px}
html,body,[class*="css"],.stApp{font-family:'Plus Jakarta Sans',sans-serif!important;background:var(--bg)!important;color:var(--text)!important}
[data-testid="stHeader"]{background:transparent!important;height:0!important}[data-testid="stDecoration"],[data-testid="stToolbar"],footer,#MainMenu{display:none!important}
[data-testid="stSidebar"]{background:var(--white)!important;border-right:1px solid var(--border)!important;box-shadow:4px 0 24px rgba(108,99,255,.06)!important}[data-testid="stSidebar"] *{color:var(--text)!important}
.main .block-container{background:transparent!important;padding:2rem 2.5rem 3rem!important;max-width:1440px!important}
.gn-page-header{margin-bottom:2rem}.gn-page-title{font-family:'Instrument Serif',serif;font-size:2.4rem;font-weight:400;font-style:italic;color:var(--text);line-height:1.15;margin:0 0 .2rem}.gn-page-title span{background:linear-gradient(135deg,var(--purple),var(--teal));-webkit-background-clip:text;-webkit-text-fill-color:transparent}.gn-page-sub{font-size:.88rem;color:var(--text-muted)}
[data-testid="metric-container"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;padding:1.5rem 1.6rem!important;box-shadow:var(--shadow-sm)!important}[data-testid="metric-container"]:hover{box-shadow:var(--shadow-md)!important;transform:translateY(-3px)}[data-testid="metric-container"] label{font-size:.72rem!important;font-weight:700!important;text-transform:uppercase!important;letter-spacing:.1em!important;color:var(--text-muted)!important}[data-testid="stMetricValue"]{font-size:1.9rem!important;font-weight:800!important;color:var(--purple)!important}
.stButton>button{background:linear-gradient(135deg,var(--purple),var(--purple-dark))!important;color:#fff!important;font-weight:700!important;border:none!important;border-radius:var(--radius-sm)!important;padding:.6rem 1.5rem!important;box-shadow:0 4px 12px rgba(108,99,255,.28)!important}.stButton>button:hover{transform:translateY(-2px)!important}
.stTextInput input,.stNumberInput input,[data-baseweb="input"] input{background:var(--bg)!important;border:1.5px solid var(--border)!important;border-radius:var(--radius-sm)!important;color:var(--text)!important}[data-baseweb="select"]>div:first-child{background:var(--bg)!important;border:1.5px solid var(--border)!important;border-radius:var(--radius-sm)!important}
.stDataFrame,[data-testid="stDataFrame"]{border-radius:var(--radius)!important;overflow:hidden!important;border:1px solid var(--border)!important;box-shadow:var(--shadow-sm)!important}[data-testid="stFileUploadDropzone"]{background:var(--bg)!important;border:2px dashed var(--border)!important;border-radius:var(--radius)!important}hr{border-color:var(--border)!important}
.gn-brand{display:flex;align-items:center;gap:.5rem;padding:0 0 1.4rem;border-bottom:1px solid var(--border);margin-bottom:1.2rem}.gn-brand-icon{width:36px;height:36px;background:linear-gradient(135deg,var(--purple),var(--teal));border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.1rem}.gn-brand-name{font-size:1.05rem;font-weight:800}.gn-brand-sub{font-size:.68rem;color:var(--text-soft)!important}.gn-user-pill{background:var(--purple-light);border-radius:var(--radius-sm);padding:.7rem 1rem;margin-bottom:1.2rem;display:flex;align-items:center;gap:.6rem}.gn-user-avatar{width:30px;height:30px;background:linear-gradient(135deg,var(--purple),var(--purple-dark));border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.8rem;color:white!important;font-weight:700}.gn-user-name{font-size:.82rem;font-weight:700;color:var(--purple)!important}.gn-user-role{font-size:.68rem;color:var(--text-muted)!important}.gn-empty{background:var(--card);border:1.5px dashed var(--border);border-radius:var(--radius);padding:3rem 2rem;text-align:center;color:var(--text-muted)}.gn-empty-icon{font-size:2.5rem}.gn-form-card{background:var(--white);border:1px solid var(--border);border-radius:var(--radius);padding:2rem;box-shadow:var(--shadow-sm)}.gn-preview{background:linear-gradient(135deg,var(--purple-light),var(--teal-light));border:1.5px solid var(--border);border-radius:var(--radius);padding:1.2rem 1.5rem;margin-top:1rem;display:flex;gap:2rem;flex-wrap:wrap}.gn-preview-item label{font-size:.68rem!important;font-weight:700!important;text-transform:uppercase!important;color:var(--text-muted)!important}.gn-preview-item .val{font-size:1.3rem;font-weight:800;color:var(--purple)}.gn-preview-item .profit{color:var(--teal)}.gn-sep{font-size:.7rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;color:var(--text-soft);border-bottom:1px solid var(--border);padding-bottom:.4rem;margin:2rem 0 1.2rem}
</style>
""", unsafe_allow_html=True)


# ============================================================
# CHART SETTINGS
# ============================================================

CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(245,247,255,0.6)",
    font=dict(family="Plus Jakarta Sans", color="#6b7280", size=12),
    margin=dict(l=10, r=10, t=45, b=10),
)

PALETTE = ["#6c63ff", "#00c9a7", "#f5a623", "#ff5c72", "#a78bfa", "#34d399"]

EMAIL_SENDER = st.secrets.get("EMAIL_SENDER", "")
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", "")

for key in ["user", "reset_code", "reset_user", "cleaned_data", "clean_stats", "mapped_data", "mapping_info"]:
    if key not in st.session_state:
        st.session_state[key] = None


# ============================================================
# DATABASE
# ============================================================

DB_PATH = "business.db"


def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            product TEXT,
            quantity REAL,
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


def load_sales(username):
    conn = get_db()
    df = pd.read_sql_query(
        "SELECT * FROM sales WHERE username=? AND status='active'",
        conn,
        params=(username,),
    )
    conn.close()
    return df


# ============================================================
# SECURITY / EMAIL
# ============================================================

def hash_pw(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_pw(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


def send_email(to, subject, body):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to, f"Subject: {subject}\n\n{body}")
        server.quit()
        return True
    except Exception:
        return False


# ============================================================
# FILE HELPERS
# ============================================================

def read_uploaded_file(uploaded_file):
    filename = uploaded_file.name.lower()
    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if filename.endswith(".xlsx"):
        return pd.read_excel(uploaded_file, engine="openpyxl")
    raise ValueError("Unsupported file format. Please upload CSV or XLSX.")


def dataframe_to_csv(data):
    return data.to_csv(index=False).encode("utf-8-sig")


# ============================================================
# SMART COLUMN DETECTION
# ============================================================

COLUMN_ALIASES = {
    "date": [
        "date", "sale date", "sales date", "transaction date", "invoice date",
        "order date", "purchase date", "payment date", "created date", "datetime",
        "timestamp", "day", "date sold", "sold date", "trans date", "posting date"
    ],
    "product": [
        "product", "product name", "product_name", "item", "item name", "item_name",
        "item description", "description", "product description", "service", "service name",
        "service type", "goods", "stock item", "sku description", "particulars", "name"
    ],
    "quantity": [
        "quantity", "qty", "qtty", "units", "unit sold", "units sold", "units_sold",
        "number sold", "no sold", "no of items", "number of items", "pieces", "pcs",
        "volume", "count", "items sold", "sales quantity"
    ],
    "cost_price": [
        "cost", "cost price", "cost_price", "unit cost", "unit_cost", "buying price",
        "buying_price", "purchase price", "purchase_price", "purchase cost", "purchase_amount",
        "purchasing price", "expense per unit", "cost per unit", "landed cost", "cogs"
    ],
    "selling_price": [
        "selling price", "selling_price", "sale price", "sale_price", "unit price", "unit_price",
        "selling amount", "selling_amount", "price", "retail price", "sales price", "amount per unit"
    ],
    "revenue": [
        "revenue", "sales", "sales amount", "sales_amount", "total sales", "total_sales",
        "turnover", "income", "income amount", "amount paid", "amount received", "total amount",
        "total amount paid", "gross sales", "net sales", "sales value", "transaction value",
        "order value", "invoice total", "amount"
    ],
    "profit": [
        "profit", "net profit", "gross profit", "profit amount", "profit_amount", "gain",
        "earnings", "net earnings", "gross earnings", "margin amount", "gross margin", "net gain"
    ],
}


def normalize_heading(value):
    text = str(value).strip().lower()
    text = text.replace("₦", " naira ")
    text = text.replace("#", " number ")
    text = re.sub(r"[\n\r\t]+", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def heading_score(column, aliases, target):
    c = normalize_heading(column)
    if c == target:
        return 100
    if c in [normalize_heading(a) for a in aliases]:
        return 95

    c_tokens = set(c.split())
    best = 0
    for alias in aliases:
        a = normalize_heading(alias)
        a_tokens = set(a.split())
        if not a_tokens:
            continue
        overlap = len(c_tokens & a_tokens) / len(a_tokens)
        if a in c or c in a:
            overlap = max(overlap, 0.82)
        best = max(best, overlap * 80)

    keyword_groups = {
        "date": ["date", "day", "time", "timestamp"],
        "product": ["product", "item", "service", "description", "goods"],
        "quantity": ["qty", "quantity", "units", "pieces", "pcs", "count", "number"],
        "cost_price": ["cost", "buying", "purchase", "cogs", "expense"],
        "selling_price": ["selling", "sale", "retail", "unit price"],
        "revenue": ["revenue", "sales", "income", "turnover", "amount", "received", "paid"],
        "profit": ["profit", "gain", "earnings", "margin"]
    }
    if any(k in c for k in keyword_groups.get(target, [])):
        best = max(best, 45)
    return best


def detect_business_columns(df):
    """Detect likely business columns without requiring fixed Excel headings."""
    columns = list(df.columns)
    candidates = {key: [] for key in COLUMN_ALIASES}

    for target, aliases in COLUMN_ALIASES.items():
        for col in columns:
            score = heading_score(col, aliases, target)
            if score >= 40:
                candidates[target].append((col, round(score, 1)))
        candidates[target].sort(key=lambda x: x[1], reverse=True)

    mapping = {}
    used = set()
    for target in ["date", "product", "quantity", "cost_price", "selling_price", "revenue", "profit"]:
        for col, score in candidates[target]:
            if col not in used and score >= 60:
                mapping[target] = col
                used.add(col)
                break

    # Validate likely date column using actual values if detection was weak.
    if "date" not in mapping:
        best_col, best_score = None, 0
        for col in columns:
            parsed = pd.to_datetime(df[col], errors="coerce")
            score = parsed.notna().mean() * 70
            if score > best_score:
                best_col, best_score = col, score
        if best_col is not None and best_score >= 55:
            mapping["date"] = best_col

    # Validate likely numeric columns by checking whether values are numeric.
    numeric_targets = ["quantity", "cost_price", "selling_price", "revenue", "profit"]
    for target in numeric_targets:
        if target not in mapping:
            best_col, best_score = None, 0
            for col in columns:
                if col in used:
                    continue
                converted = pd.to_numeric(
                    df[col].astype(str).str.replace(",", "", regex=False).str.replace("₦", "", regex=False),
                    errors="coerce"
                )
                numeric_ratio = converted.notna().mean()
                score = numeric_ratio * 55
                if score > best_score:
                    best_col, best_score = col, score
            if best_col is not None and best_score >= 45:
                # Do not automatically assign a generic numeric column to every financial field.
                if target == "quantity" or len([x for x in mapping.values() if x == best_col]) == 0:
                    mapping[target] = best_col
                    used.add(best_col)

    return mapping, candidates


def mapping_confidence(mapping, candidates):
    result = {}
    for target, source in mapping.items():
        score = 0
        for col, s in candidates.get(target, []):
            if col == source:
                score = s
                break
        if score >= 90:
            label = "High"
        elif score >= 70:
            label = "Medium"
        else:
            label = "Review"
        result[target] = (label, score)
    return result


def apply_column_mapping(df, mapping):
    """Create a standardized analytical view while preserving all original columns."""
    out = df.copy()
    rename_map = {source: target for target, source in mapping.items() if source and source in out.columns}
    out = out.rename(columns=rename_map)

    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"], errors="coerce")

    for col in ["quantity", "cost_price", "selling_price", "revenue", "profit"]:
        if col in out.columns:
            out[col] = pd.to_numeric(
                out[col].astype(str).str.replace(",", "", regex=False).str.replace("₦", "", regex=False).str.strip(),
                errors="coerce"
            )

    if "product" in out.columns:
        out["product"] = out["product"].astype(str).str.strip()

    # Revenue can be calculated from unit price and quantity.
    if "revenue" not in out.columns and {"selling_price", "quantity"}.issubset(out.columns):
        out["revenue"] = out["selling_price"] * out["quantity"]

    # Cost can be calculated from cost per unit and quantity when present.
    if "total_cost" not in out.columns and {"cost_price", "quantity"}.issubset(out.columns):
        out["total_cost"] = out["cost_price"] * out["quantity"]

    # Profit: prefer supplied profit; otherwise derive it.
    if "profit" not in out.columns and {"revenue", "total_cost"}.issubset(out.columns):
        out["profit"] = out["revenue"] - out["total_cost"]
    elif "profit" not in out.columns and {"selling_price", "cost_price", "quantity"}.issubset(out.columns):
        out["profit"] = (out["selling_price"] - out["cost_price"]) * out["quantity"]

    if "revenue" in out.columns:
        out["margin_percent"] = np.where(
            out["revenue"] != 0,
            (out.get("profit", pd.Series(0, index=out.index)) / out["revenue"]) * 100,
            np.nan,
        )

    return out


def smart_mapping_ui(raw_df, key_prefix="mapping"):
    """Display detection results and let user correct ambiguous mappings."""
    detected, candidates = detect_business_columns(raw_df)
    confidence = mapping_confidence(detected, candidates)

    st.markdown('<div class="gn-sep">Smart Column Detection</div>', unsafe_allow_html=True)
    st.info("Growth Network automatically identified the most likely business fields. Review or change any mapping before analysis.")

    target_labels = {
        "date": "📅 Date",
        "product": "🏷 Product / Service",
        "quantity": "📦 Quantity",
        "cost_price": "💰 Unit Cost",
        "selling_price": "💵 Unit Selling Price",
        "revenue": "📈 Revenue / Sales Amount",
        "profit": "🟢 Profit"
    }

    options = ["— Not available —"] + list(raw_df.columns)
    mapping = {}
    cols = st.columns(2)
    targets = list(target_labels.keys())

    for i, target in enumerate(targets):
        with cols[i % 2]:
            default_source = detected.get(target)
            default_index = options.index(default_source) if default_source in options else 0
            confidence_text = ""
            if target in confidence:
                confidence_text = f" ({confidence[target][0]} confidence)"
            selected = st.selectbox(
                target_labels[target] + confidence_text,
                options,
                index=default_index,
                key=f"{key_prefix}_{target}"
            )
            if selected != "— Not available —":
                mapping[target] = selected

    return mapping


# ============================================================
# DATA CLEANING ENGINE
# ============================================================

def clean_business_data(data, mapping=None):
    """Clean flexible business data. No fixed Excel headings are required."""
    df_clean = data.copy()
    original_rows = len(df_clean)

    # Remove empty columns/rows.
    df_clean = df_clean.dropna(axis=1, how="all")
    df_clean = df_clean.dropna(how="all")
    empty_rows_removed = original_rows - len(df_clean)

    duplicate_count = int(df_clean.duplicated().sum())
    df_clean = df_clean.drop_duplicates().copy()

    if mapping is None:
        mapping, _ = detect_business_columns(df_clean)

    standardized = apply_column_mapping(df_clean, mapping)

    stats = {
        "original_rows": original_rows,
        "empty_rows_removed": int(empty_rows_removed),
        "duplicates_removed": duplicate_count,
        "invalid_dates": 0,
        "invalid_numeric": 0,
        "invalid_quantity": 0,
        "missing_product": 0,
        "clean_rows": 0,
    }

    # Date is useful but not mandatory for general business analysis.
    if "date" in standardized.columns:
        stats["invalid_dates"] = int(standardized["date"].isna().sum())
        standardized = standardized.dropna(subset=["date"]).copy()
        standardized["date"] = standardized["date"].dt.strftime("%Y-%m-%d")

    if "product" in standardized.columns:
        standardized["product"] = standardized["product"].replace({"nan": "Unknown", "None": "Unknown"}).fillna("Unknown")
        standardized["product"] = standardized["product"].astype(str).str.strip()
        stats["missing_product"] = int((standardized["product"] == "").sum())
        standardized.loc[standardized["product"] == "", "product"] = "Unknown"

    numeric_cols = [c for c in ["quantity", "cost_price", "selling_price", "revenue", "profit", "total_cost"] if c in standardized.columns]
    if numeric_cols:
        before = standardized[numeric_cols].isna().sum().sum()
        for col in numeric_cols:
            standardized[col] = pd.to_numeric(standardized[col], errors="coerce")
        stats["invalid_numeric"] = int(before)

    if "quantity" in standardized.columns:
        invalid_qty = int((standardized["quantity"] <= 0).fillna(False).sum())
        stats["invalid_quantity"] = invalid_qty
        standardized = standardized[(standardized["quantity"].isna()) | (standardized["quantity"] > 0)].copy()

    # Remove rows that are entirely unusable after conversion.
    usable_fields = [c for c in ["date", "product", "quantity", "revenue", "profit"] if c in standardized.columns]
    if usable_fields:
        standardized = standardized.dropna(how="all", subset=usable_fields)

    # Recalculate derived fields where enough information exists.
    if "revenue" not in standardized.columns and {"selling_price", "quantity"}.issubset(standardized.columns):
        standardized["revenue"] = standardized["selling_price"] * standardized["quantity"]
    if "total_cost" not in standardized.columns and {"cost_price", "quantity"}.issubset(standardized.columns):
        standardized["total_cost"] = standardized["cost_price"] * standardized["quantity"]
    if "profit" not in standardized.columns:
        if {"revenue", "total_cost"}.issubset(standardized.columns):
            standardized["profit"] = standardized["revenue"] - standardized["total_cost"]
        elif {"selling_price", "cost_price", "quantity"}.issubset(standardized.columns):
            standardized["profit"] = (standardized["selling_price"] - standardized["cost_price"]) * standardized["quantity"]

    if {"revenue", "profit"}.issubset(standardized.columns):
        standardized["margin_percent"] = np.where(
            standardized["revenue"] != 0,
            standardized["profit"] / standardized["revenue"] * 100,
            np.nan
        )

    standardized = standardized.reset_index(drop=True)
    stats["clean_rows"] = len(standardized)
    return standardized, stats, mapping


# ============================================================
# REPORT ENGINE
# ============================================================

def prepare_report(df, period):
    report_df = df.copy()
    if report_df.empty:
        return pd.DataFrame()

    if "date" not in report_df.columns:
        return pd.DataFrame()

    report_df["date"] = pd.to_datetime(report_df["date"], errors="coerce")
    report_df = report_df.dropna(subset=["date"])

    if "quantity" not in report_df.columns:
        report_df["quantity"] = 1
    report_df["quantity"] = pd.to_numeric(report_df["quantity"], errors="coerce").fillna(0)

    if "revenue" not in report_df.columns:
        if {"selling_price", "quantity"}.issubset(report_df.columns):
            report_df["revenue"] = report_df["selling_price"] * report_df["quantity"]
        else:
            report_df["revenue"] = 0

    if "profit" not in report_df.columns:
        if "cost_price" in report_df.columns and "selling_price" in report_df.columns:
            report_df["profit"] = (report_df["selling_price"] - report_df["cost_price"]) * report_df["quantity"]
        else:
            report_df["profit"] = 0

    if period == "Daily":
        report_df["Period"] = report_df["date"].dt.strftime("%Y-%m-%d")
    elif period == "Weekly":
        week_start = report_df["date"] - pd.to_timedelta(report_df["date"].dt.weekday, unit="D")
        report_df["Period"] = week_start.dt.strftime("%Y-%m-%d")
    elif period == "Monthly":
        report_df["Period"] = report_df["date"].dt.to_period("M").astype(str)
    else:
        report_df["Period"] = report_df["date"].dt.year.astype(str)

    result = report_df.groupby("Period").agg(
        Transactions=(report_df.columns[0], "count"),
        Quantity=("quantity", "sum"),
        Revenue=("revenue", "sum"),
        Profit=("profit", "sum"),
    ).reset_index()
    result["Margin %"] = np.where(result["Revenue"] != 0, result["Profit"] / result["Revenue"] * 100, 0)
    return result


# ============================================================
# PDF REPORT
# ============================================================

def create_pdf_report(report_data, report_title, start_date, end_date):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    except ImportError:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Growth Network", styles["Title"]),
        Paragraph(report_title, styles["Heading2"]),
        Paragraph(f"Period: {start_date} to {end_date}", styles["Normal"]),
        Spacer(1, 15),
    ]

    total_revenue = report_data["Revenue"].sum() if "Revenue" in report_data else 0
    total_profit = report_data["Profit"].sum() if "Profit" in report_data else 0
    total_quantity = report_data["Quantity"].sum() if "Quantity" in report_data else 0
    transactions = report_data["Transactions"].sum() if "Transactions" in report_data else 0

    summary = [
        ["Metric", "Value"],
        ["Transactions", f"{transactions:,.0f}"],
        ["Units Sold", f"{total_quantity:,.2f}"],
        ["Revenue", f"₦{total_revenue:,.2f}"],
        ["Profit", f"₦{total_profit:,.2f}"],
    ]
    table = Table(summary, colWidths=[2.5 * inch, 2.5 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6c63ff")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), .5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    elements.extend([table, Spacer(1, 15)])

    if not report_data.empty:
        pdf_df = report_data.copy().head(200)
        for col in pdf_df.columns:
            if pd.api.types.is_numeric_dtype(pdf_df[col]):
                pdf_df[col] = pdf_df[col].round(2)
        table_data = [list(pdf_df.columns)] + pdf_df.astype(str).values.tolist()
        detail = Table(table_data, repeatRows=1)
        detail.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6c63ff")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), .25, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(detail)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# ============================================================
# DATABASE IMPORT OF CLEANED DATA
# ============================================================

def import_cleaned_sales(username, cleaned_df):
    required = {"product", "quantity", "cost_price", "selling_price", "profit", "date"}
    if not required.issubset(cleaned_df.columns):
        return 0, 0

    conn = get_db()
    cur = conn.cursor()
    inserted = 0
    skipped = 0

    existing = cur.execute(
        "SELECT product, quantity, cost_price, selling_price, date FROM sales WHERE username=?",
        (username,)
    ).fetchall()
    existing_keys = set(tuple(x) for x in existing)

    for _, row in cleaned_df.iterrows():
        date_value = pd.to_datetime(row["date"], errors="coerce")
        if pd.isna(date_value):
            skipped += 1
            continue
        key = (
            str(row["product"]),
            float(row["quantity"]),
            float(row["cost_price"]),
            float(row["selling_price"]),
            date_value.strftime("%Y-%m-%d")
        )
        if key in existing_keys:
            skipped += 1
            continue
        cur.execute(
            """
            INSERT INTO sales(username, product, quantity, cost_price, selling_price, profit, date, status)
            VALUES(?,?,?,?,?,?,?,'active')
            """,
            (username, key[0], key[1], key[2], key[3], float(row["profit"]), key[4])
        )
        existing_keys.add(key)
        inserted += 1

    conn.commit()
    conn.close()
    return inserted, skipped


# ============================================================
# AUTH
# ============================================================

if st.session_state.user is None:
    _, mid, _ = st.columns([1, 1.55, 1])
    with mid:
        st.markdown('<div style="text-align:center;padding-top:3rem">📈</div>', unsafe_allow_html=True)
        st.markdown("<div style=\"font-family:'Instrument Serif',serif;font-style:italic;font-size:1.75rem;text-align:center\">Growth Network</div>", unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;color:#6b7280;margin-bottom:1.5rem">Your intelligent business companion</div>', unsafe_allow_html=True)
        mode = st.radio("", ["Login", "Register", "Forgot Password"], horizontal=True, label_visibility="collapsed")
        conn = get_db()
        cur = conn.cursor()

        if mode == "Register":
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            if st.button("Create My Account →", use_container_width=True):
                if not username or not email or not password:
                    st.warning("Please fill all fields.")
                elif len(password) < 6:
                    st.warning("Password must be at least 6 characters.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                else:
                    cur.execute("SELECT id FROM users WHERE username=?", (username,))
                    if cur.fetchone():
                        st.error("Username already exists.")
                    else:
                        cur.execute("INSERT INTO users(username,password,email) VALUES(?,?,?)", (username, hash_pw(password), email))
                        conn.commit()
                        st.success("Account created successfully. You can now log in.")
        elif mode == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Sign In →", use_container_width=True):
                cur.execute("SELECT password FROM users WHERE username=?", (username,))
                row = cur.fetchone()
                if row and verify_pw(password, row[0]):
                    st.session_state.user = username
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")
        else:
            st.info("Please contact your administrator to reset your password.")
        conn.close()
    st.stop()


# ============================================================
# MAIN APP
# ============================================================

user = st.session_state.user
df = load_sales(user)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("""
    <div class="gn-brand"><div class="gn-brand-icon">📈</div><div><div class="gn-brand-name">Growth Network</div><div class="gn-brand-sub">Business Intelligence</div></div></div>
    """, unsafe_allow_html=True)
    initials = user[:2].upper()
    st.markdown(f'<div class="gn-user-pill"><div class="gn-user-avatar">{initials}</div><div><div class="gn-user-name">{user}</div><div class="gn-user-role">Business Owner</div></div></div>', unsafe_allow_html=True)

    menu = st.radio("Navigation", [
        "📊  Dashboard", "➕  Add Sale", "📈  Analytics", "🗂  History",
        "📊  Reports", "📥  Export Sales", "🧹  Data Cleaning", "🗑  Trash", "🧠  AI Brain"
    ], label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    with c2:
        if st.button("🗑 Clear", use_container_width=True):
            conn = get_db(); cur = conn.cursor()
            cur.execute("UPDATE sales SET status='deleted' WHERE username=?", (user,))
            conn.commit(); conn.close()
            st.success("Moved to Trash")
            st.rerun()

    if not df.empty:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="gn-sep">Quick Stats</div>', unsafe_allow_html=True)
        st.markdown(f'''<div style="font-size:.8rem;color:var(--text-muted);line-height:2">💰 Total Profit: <b style="color:var(--teal)">₦{df["profit"].sum():,.0f}</b><br>📦 Sales: <b style="color:var(--purple)">{len(df)}</b><br>🏷 Products: <b style="color:var(--gold)">{df["product"].nunique()}</b></div>''', unsafe_allow_html=True)


# ============================================================
# DASHBOARD
# ============================================================

if "Dashboard" in menu:
    st.markdown('<div class="gn-page-header"><div class="gn-page-title">Good day, <span>let\'s grow.</span></div><div class="gn-page-sub">Here\'s your business overview at a glance</div></div>', unsafe_allow_html=True)
    if df.empty:
        st.markdown('<div class="gn-empty"><div class="gn-empty-icon">📭</div><b>No sales data yet.</b><br>Go to <b>Add Sale</b> to record your first transaction.</div>', unsafe_allow_html=True)
    else:
        total_profit = df["profit"].sum()
        total_revenue = (df["selling_price"] * df["quantity"]).sum()
        avg_margin = np.where(total_revenue != 0, total_profit / total_revenue * 100, 0)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Sales", len(df)); c2.metric("Net Profit", f"₦{total_profit:,.0f}"); c3.metric("Revenue", f"₦{total_revenue:,.0f}"); c4.metric("Avg Margin", f"{avg_margin:.1f}%")
        st.markdown('<div class="gn-sep">Performance Charts</div>', unsafe_allow_html=True)
        left, right = st.columns([3, 2])
        with left:
            summary = df.groupby("product").agg(profit=("profit", "sum"), sales=("id", "count")).reset_index().sort_values("profit", ascending=False)
            fig = px.bar(summary, x="product", y="profit", color="profit", color_continuous_scale=["#ede9ff", "#6c63ff"], title="Profit by Product", text_auto=".2s")
            fig.update_layout(**CHART); st.plotly_chart(fig, use_container_width=True)
        with right:
            pie = df.groupby("product")["profit"].sum().reset_index()
            fig2 = px.pie(pie, names="product", values="profit", title="Profit Share", color_discrete_sequence=PALETTE, hole=.45)
            fig2.update_layout(**CHART); st.plotly_chart(fig2, use_container_width=True)
        st.markdown('<div class="gn-sep">Recent Transactions</div>', unsafe_allow_html=True)
        recent = df.sort_values("date", ascending=False).head(10)
        display = recent[["date", "product", "quantity", "cost_price", "selling_price", "profit"]].rename(columns={"date":"Date", "product":"Product", "quantity":"Qty", "cost_price":"Cost (₦)", "selling_price":"Price (₦)", "profit":"Profit (₦)"})
        st.dataframe(display, use_container_width=True, hide_index=True)


# ============================================================
# ADD SALE
# ============================================================

elif "Add Sale" in menu:
    st.markdown('<div class="gn-page-header"><div class="gn-page-title">Record a <span>new sale</span></div><div class="gn-page-sub">Fill in the details below to log a transaction</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="gn-form-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: product = st.text_input("Product Name", placeholder="e.g. Ankara Fabric")
    with col2: qty = st.number_input("Quantity", min_value=1.0, value=1.0, step=1.0)
    col3, col4 = st.columns(2)
    with col3: cost = st.number_input("Cost Price (₦)", min_value=0.0, step=100.0)
    with col4: sell = st.number_input("Selling Price (₦)", min_value=0.0, step=100.0)
    if cost > 0 and sell > 0:
        proj_profit = (sell - cost) * qty; revenue = sell * qty; margin = (sell - cost) / sell * 100
        st.markdown(f'<div class="gn-preview"><div class="gn-preview-item"><label>Revenue</label><div class="val">₦{revenue:,.0f}</div></div><div class="gn-preview-item"><label>Profit</label><div class="val profit">₦{proj_profit:,.0f}</div></div><div class="gn-preview-item"><label>Margin</label><div class="val">{margin:.1f}%</div></div><div class="gn-preview-item"><label>Total Cost</label><div class="val">₦{cost*qty:,.0f}</div></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("💾 Save Sale", use_container_width=True):
        if not product.strip(): st.warning("Please enter a product name.")
        else:
            profit_val = (sell - cost) * qty; date_str = datetime.now().strftime("%Y-%m-%d")
            conn = get_db(); cur = conn.cursor()
            cur.execute("INSERT INTO sales(username,product,quantity,cost_price,selling_price,profit,date,status) VALUES(?,?,?,?,?,?,?,'active')", (user, product.strip(), qty, cost, sell, profit_val, date_str))
            conn.commit(); conn.close(); st.success(f"Sale saved! Profit: ₦{profit_val:,.2f}"); st.balloons()


# ============================================================
# ANALYTICS
# ============================================================

elif "Analytics" in menu:
    st.markdown('<div class="gn-page-header"><div class="gn-page-title">Business <span>Analytics</span></div><div class="gn-page-sub">Trends, performance and business growth</div></div>', unsafe_allow_html=True)
    if df.empty:
        st.warning("No data to analyse yet.")
    else:
        temp = df.copy(); temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
        temp["revenue"] = temp["selling_price"] * temp["quantity"]
        monthly = temp.groupby(temp["date"].dt.to_period("M")).agg(profit=("profit","sum"), sales=("id","count"), revenue=("revenue","sum")).reset_index()
        monthly["date_str"] = monthly["date"].astype(str)
        c1,c2,c3=st.columns(3)
        c1.metric("Best Month Profit", f"₦{monthly['profit'].max():,.0f}")
        c2.metric("Average Monthly Profit", f"₦{monthly['profit'].mean():,.0f}")
        if len(monthly)>1:
            x=np.arange(len(monthly)); m,b=np.polyfit(x,monthly["profit"].values,1); forecast=m*len(x)+b
            c3.metric("Next Month Forecast", f"₦{forecast:,.0f}")
        else: c3.metric("Next Month Forecast", "More data needed")
        fig=px.line(monthly,x="date_str",y="profit",markers=True,title="Monthly Profit Trend"); fig.update_layout(**CHART); st.plotly_chart(fig,use_container_width=True)
        fig2=px.bar(monthly,x="date_str",y="sales",title="Monthly Sales Volume"); fig2.update_layout(**CHART); st.plotly_chart(fig2,use_container_width=True)


# ============================================================
# HISTORY
# ============================================================

elif "History" in menu:
    st.markdown('<div class="gn-page-header"><div class="gn-page-title">Transaction <span>History</span></div><div class="gn-page-sub">Browse and filter your past sales</div></div>', unsafe_allow_html=True)
    if df.empty: st.warning("No history yet.")
    else:
        temp=df.copy(); temp["date"]=pd.to_datetime(temp["date"],errors="coerce")
        option=st.selectbox("Filter by",["Daily","Weekly","Monthly","Yearly"])
        if option=="Daily":
            d=st.date_input("Pick a date"); filtered=temp[temp["date"].dt.date==d]
        elif option=="Weekly":
            temp["_week"]=temp["date"].dt.to_period("W"); selected=st.selectbox("Select Week",sorted(temp["_week"].unique(),reverse=True)); filtered=temp[temp["_week"]==selected]
        elif option=="Monthly":
            temp["_month"]=temp["date"].dt.to_period("M"); selected=st.selectbox("Select Month",sorted(temp["_month"].unique(),reverse=True)); filtered=temp[temp["_month"]==selected]
        else:
            temp["_year"]=temp["date"].dt.year; selected=st.selectbox("Select Year",sorted(temp["_year"].unique(),reverse=True)); filtered=temp[temp["_year"]==selected]
        revenue=(filtered["selling_price"]*filtered["quantity"]).sum(); c1,c2,c3=st.columns(3); c1.metric("Transactions",len(filtered)); c2.metric("Revenue",f"₦{revenue:,.0f}"); c3.metric("Profit",f"₦{filtered['profit'].sum():,.0f}")
        st.dataframe(filtered[["date","product","quantity","cost_price","selling_price","profit"]],use_container_width=True,hide_index=True)


# ============================================================
# REPORTS
# ============================================================

elif "Reports" in menu:
    st.markdown('<div class="gn-page-header"><div class="gn-page-title">Sales <span>Reports</span></div><div class="gn-page-sub">Generate daily, weekly, monthly and yearly business reports</div></div>', unsafe_allow_html=True)
    if df.empty: st.warning("You need sales data before generating a report.")
    else:
        period=st.selectbox("Report Type",["Daily","Weekly","Monthly","Yearly"])
        report=prepare_report(df,period)
        if report.empty: st.warning("No dated sales data available for this report.")
        else:
            total_transactions=report["Transactions"].sum(); total_quantity=report["Quantity"].sum(); total_revenue=report["Revenue"].sum(); total_profit=report["Profit"].sum()
            c1,c2,c3,c4=st.columns(4); c1.metric("Transactions",f"{total_transactions:,.0f}"); c2.metric("Units Sold",f"{total_quantity:,.0f}"); c3.metric("Revenue",f"₦{total_revenue:,.2f}"); c4.metric("Profit",f"₦{total_profit:,.2f}")
            st.markdown('<div class="gn-sep">Report Table</div>',unsafe_allow_html=True); st.dataframe(report,use_container_width=True,hide_index=True)
            fig=px.bar(report,x="Period",y="Profit",title=f"{period} Profit Report",text_auto=".2s"); fig.update_layout(**CHART); st.plotly_chart(fig,use_container_width=True)
            csv_data=dataframe_to_csv(report); st.download_button("📥 Download Report as CSV",csv_data,f"{period.lower()}_sales_report.csv","text/csv",use_container_width=True)
            dates=pd.to_datetime(df["date"],errors="coerce"); min_date=dates.min().strftime("%Y-%m-%d"); max_date=dates.max().strftime("%Y-%m-%d")
            pdf_data=create_pdf_report(report,f"{period} Sales Report",min_date,max_date)
            if pdf_data: st.download_button("📄 Download Report as PDF",pdf_data,f"{period.lower()}_sales_report.pdf","application/pdf",use_container_width=True)
            else: st.info("PDF export requires reportlab in requirements.txt.")


# ============================================================
# EXPORT SALES
# ============================================================

elif "Export Sales" in menu:
    st.markdown('<div class="gn-page-header"><div class="gn-page-title">Export <span>Sales Data</span></div><div class="gn-page-sub">Download your recorded transactions as CSV</div></div>',unsafe_allow_html=True)
    if df.empty: st.warning("No sales data available.")
    else:
        export_df=df.copy(); export_df["Revenue"]=export_df["selling_price"]*export_df["quantity"]
        export_df=export_df[["date","product","quantity","cost_price","selling_price","Revenue","profit"]].rename(columns={"date":"Date","product":"Product","quantity":"Quantity","cost_price":"Cost Price","selling_price":"Selling Price","profit":"Profit"})
        st.dataframe(export_df,use_container_width=True,hide_index=True)
        st.download_button("📥 Download All Sales as CSV",dataframe_to_csv(export_df),f"growth_network_sales_{datetime.now().strftime('%Y%m%d')}.csv","text/csv",use_container_width=True)
        st.success(f"{len(export_df):,} transactions ready for export.")


# ============================================================
# DATA CLEANING
# ============================================================

elif "Data Cleaning" in menu:
    st.markdown('<div class="gn-page-header"><div class="gn-page-title">🧹 Data <span>Cleaning</span></div><div class="gn-page-sub">Clean almost any business Excel or CSV structure before analysis</div></div>',unsafe_allow_html=True)
    st.info("Upload CSV or Excel data. Growth Network detects your headings automatically, preserves additional columns, cleans values and calculates missing Revenue/Profit fields when possible.")
    file=st.file_uploader("Upload Business Data",type=["csv","xlsx"],key="cleaning_upload")
    if file:
        try:
            raw_data=read_uploaded_file(file)
            st.markdown('<div class="gn-sep">Original Data</div>',unsafe_allow_html=True); st.dataframe(raw_data.head(20),use_container_width=True,hide_index=True); st.write(f"Original rows: **{len(raw_data):,}** | Columns: **{len(raw_data.columns):,}**")
            mapping=smart_mapping_ui(raw_data,"clean")
            if st.button("🧹 Clean & Prepare Data",use_container_width=True):
                cleaned,stats,used_mapping=clean_business_data(raw_data,mapping)
                st.session_state.cleaned_data=cleaned; st.session_state.clean_stats=stats; st.session_state.mapping_info=used_mapping
                if cleaned.empty: st.error("No usable rows remained after cleaning. Check your column mapping and source data.")
                else: st.success("Data cleaning completed successfully.")
        except Exception as e: st.error(f"Unable to read file: {e}")

    if st.session_state.cleaned_data is not None:
        cleaned=st.session_state.cleaned_data; stats=st.session_state.clean_stats
        st.markdown('<div class="gn-sep">Cleaning Results</div>',unsafe_allow_html=True)
        c1,c2,c3,c4,c5=st.columns(5); c1.metric("Original Rows",stats["original_rows"]); c2.metric("Clean Rows",stats["clean_rows"]); c3.metric("Duplicates Removed",stats["duplicates_removed"]); c4.metric("Invalid Dates",stats["invalid_dates"]); c5.metric("Empty Rows Removed",stats["empty_rows_removed"])
        st.dataframe(cleaned,use_container_width=True,hide_index=True)
        st.download_button("📥 Download Cleaned CSV",dataframe_to_csv(cleaned),"growth_network_cleaned_data.csv","text/csv",use_container_width=True)
        st.markdown('<div class="gn-sep">Optional Database Import</div>',unsafe_allow_html=True)
        if {"date","product","quantity","cost_price","selling_price","profit"}.issubset(cleaned.columns):
            st.caption("The database importer uses the standardized fields and skips duplicate transactions already in your account.")
            if st.button("📥 Import Cleaned Sales into Growth Network",use_container_width=True):
                inserted,skipped=import_cleaned_sales(user,cleaned); st.success(f"Imported {inserted:,} new transactions. Skipped {skipped:,} duplicates/invalid rows."); st.rerun()
        else:
            st.warning("This dataset does not contain enough standardized fields for direct sales-database import. You can still download the cleaned file.")


# ============================================================
# TRASH
# ============================================================

elif "Trash" in menu:
    st.markdown('<div class="gn-page-header"><div class="gn-page-title">🗑 <span>Trash</span></div><div class="gn-page-sub">Restore or permanently delete transactions</div></div>',unsafe_allow_html=True)
    conn=get_db(); trash=pd.read_sql_query("SELECT * FROM sales WHERE username=? AND status='deleted'",conn,params=(user,)); conn.close()
    if trash.empty: st.markdown('<div class="gn-empty"><div class="gn-empty-icon">✨</div>Trash is empty.</div>',unsafe_allow_html=True)
    else:
        st.dataframe(trash,use_container_width=True,hide_index=True); c1,c2=st.columns(2)
        with c1:
            if st.button("♻️ Restore All",use_container_width=True):
                conn=get_db(); cur=conn.cursor(); cur.execute("UPDATE sales SET status='active' WHERE username=?",(user,)); conn.commit(); conn.close(); st.success("All records restored."); st.rerun()
        with c2:
            if st.button("🗑 Delete Forever",use_container_width=True):
                conn=get_db(); cur=conn.cursor(); cur.execute("DELETE FROM sales WHERE username=? AND status='deleted'",(user,)); conn.commit(); conn.close(); st.success("Records permanently deleted."); st.rerun()


# ============================================================
# AI BRAIN
# ============================================================

elif "AI" in menu:
    st.markdown('<div class="gn-page-header"><div class="gn-page-title">🧠 AI <span>Business Brain</span></div><div class="gn-page-sub">Upload almost any business spreadsheet for forecasting, segmentation and intelligent insights</div></div>',unsafe_allow_html=True)
    st.info("You are no longer restricted to headings such as date, product, quantity, cost_price and selling_price. Upload your spreadsheet and Growth Network will detect the relevant columns.")
    file=st.file_uploader("Upload Excel or CSV",type=["xlsx","csv"],key="ai_upload")
    if file:
        try: df_ai_raw=read_uploaded_file(file)
        except Exception as e: st.error(f"Unable to read file: {e}"); st.stop()

        st.markdown('<div class="gn-sep">Data Preview</div>',unsafe_allow_html=True); st.dataframe(df_ai_raw.head(20),use_container_width=True,hide_index=True)
        mapping=smart_mapping_ui(df_ai_raw,"ai")
        if st.button("🧠 Prepare Data for AI Analysis",use_container_width=True):
            cleaned,stats,used_mapping=clean_business_data(df_ai_raw,mapping)
            st.session_state.mapped_data=cleaned; st.session_state.mapping_info=used_mapping
            if cleaned.empty: st.error("No usable data was found. Review your mapping.")
            else: st.success(f"Prepared {len(cleaned):,} rows for AI analysis.")

    if st.session_state.mapped_data is not None:
        df_ai=st.session_state.mapped_data.copy()
        if df_ai.empty: st.stop()
        st.markdown('<div class="gn-sep">Detected Business Structure</div>',unsafe_allow_html=True)
        mapping_display=pd.DataFrame({"Standard Field":list(st.session_state.mapping_info.keys()),"Original Excel Heading":list(st.session_state.mapping_info.values())})
        st.dataframe(mapping_display,use_container_width=True,hide_index=True)

        # Flexible metrics.
        has_profit="profit" in df_ai.columns
        has_revenue="revenue" in df_ai.columns
        has_qty="quantity" in df_ai.columns
        has_product="product" in df_ai.columns
        has_date="date" in df_ai.columns

        if has_profit: total_profit=pd.to_numeric(df_ai["profit"],errors="coerce").fillna(0).sum()
        else: total_profit=0
        if has_revenue: total_revenue=pd.to_numeric(df_ai["revenue"],errors="coerce").fillna(0).sum()
        elif {"selling_price","quantity"}.issubset(df_ai.columns): total_revenue=(df_ai["selling_price"]*df_ai["quantity"]).sum()
        else: total_revenue=0
        total_qty=pd.to_numeric(df_ai["quantity"],errors="coerce").fillna(0).sum() if has_qty else 0
        product_count=df_ai["product"].nunique() if has_product else 0

        st.markdown('<div class="gn-sep">Business Summary</div>',unsafe_allow_html=True)
        metric_cols=st.columns(4)
        metric_cols[0].metric("Rows",f"{len(df_ai):,}")
        metric_cols[1].metric("Revenue",f"₦{total_revenue:,.2f}" if total_revenue else "Not available")
        metric_cols[2].metric("Profit",f"₦{total_profit:,.2f}" if has_profit else "Not available")
        metric_cols[3].metric("Products",f"{product_count:,}" if has_product else "Not available")

        if not has_profit and not has_revenue:
            st.warning("This file does not contain a recognizable Revenue or Profit field. The app can still clean and display the data, but financial forecasting needs a financial measure.")

        # Forecasting
        st.markdown('<div class="gn-sep">AI Profit / Revenue Forecast</div>',unsafe_allow_html=True)
        if not has_date:
            st.warning("No date column was detected, so time-series forecasting is unavailable. You can still use product and financial analysis.")
        else:
            forecast_measure="profit" if has_profit else ("revenue" if has_revenue else None)
            if forecast_measure is None:
                st.warning("No usable Profit or Revenue column is available for forecasting.")
            else:
                ts=df_ai.groupby("date")[forecast_measure].sum().reset_index().rename(columns={"date":"ds",forecast_measure:"y"}).sort_values("ds")
                unique_days=len(ts)
                if unique_days<2:
                    st.warning("Only one unique date was found. A real time-series forecast cannot be reliably trained from one date. Add more historical dates.")
                else:
                    if unique_days<10: st.warning(f"Only {unique_days} unique dates are available. Treat this forecast as an early estimate; more history improves reliability.")
                    try:
                        from prophet import Prophet
                        with st.spinner("AI is analysing your business history..."):
                            model=Prophet(daily_seasonality=False,weekly_seasonality=unique_days>=14,yearly_seasonality=False)
                            model.fit(ts)
                            future=model.make_future_dataframe(periods=30)
                            forecast=model.predict(future)
                        fig=go.Figure()
                        fig.add_trace(go.Scatter(x=forecast["ds"],y=forecast["yhat_upper"],line=dict(width=0),showlegend=False))
                        fig.add_trace(go.Scatter(x=forecast["ds"],y=forecast["yhat_lower"],fill="tonexty",line=dict(width=0),name="Confidence"))
                        fig.add_trace(go.Scatter(x=forecast["ds"],y=forecast["yhat"],mode="lines",name="AI Forecast",line=dict(color="#6c63ff",width=3)))
                        fig.add_trace(go.Scatter(x=ts["ds"],y=ts["y"],mode="markers",name="Actual",marker=dict(color="#00c9a7",size=6)))
                        fig.update_layout(title=f"30-Day {forecast_measure.title()} Forecast",**CHART); st.plotly_chart(fig,use_container_width=True)
                        future_30=forecast.tail(30)["yhat"].sum()
                        st.success(f"Projected {forecast_measure} for the next 30 days: ₦{future_30:,.2f}") if future_30>=0 else st.error(f"Projected negative {forecast_measure}: ₦{future_30:,.2f}")
                    except ImportError:
                        st.warning("Prophet is not installed. Add `prophet` to requirements.txt to enable the AI time-series forecast. The rest of the AI Brain remains available.")
                    except Exception as e:
                        st.warning(f"Forecast could not be generated: {e}")

        # Product intelligence
        st.markdown('<div class="gn-sep">Product / Service Intelligence</div>',unsafe_allow_html=True)
        if not has_product:
            st.info("No product/service column was detected, so product-level intelligence is unavailable.")
        else:
            agg={}
            if has_qty: agg["quantity"]=("quantity","sum")
            if has_profit: agg["profit"]=("profit","sum")
            if has_revenue: agg["revenue"]=("revenue","sum")
            agg["transactions"]=(df_ai.columns[0],"count")
            pstats=df_ai.groupby("product").agg(**agg).reset_index()
            sort_col="profit" if has_profit else ("revenue" if has_revenue else "transactions")
            pstats=pstats.sort_values(sort_col,ascending=False)
            col1,col2=st.columns(2)
            with col1: st.markdown("**🔥 Top Products / Services**"); st.dataframe(pstats.head(5),use_container_width=True,hide_index=True)
            with col2: st.markdown("**⚠️ Products / Services to Review**"); st.dataframe(pstats.tail(5),use_container_width=True,hide_index=True)
            fig_p=px.bar(pstats.head(20),x="product",y=sort_col,color=sort_col,title=f"Top Product/Service by {sort_col.title()}",text_auto=".2s"); fig_p.update_layout(**CHART); st.plotly_chart(fig_p,use_container_width=True)

            # Segmentation
            st.markdown('<div class="gn-sep">AI Product Segmentation</div>',unsafe_allow_html=True)
            features=[c for c in ["quantity","revenue","profit"] if c in pstats.columns]
            if len(pstats)<2 or not features:
                st.warning("At least 2 products/services and one numeric performance field are needed for segmentation.")
            else:
                from sklearn.cluster import KMeans
                from sklearn.preprocessing import StandardScaler
                seg=pstats[["product"]+features].copy().fillna(0)
                k=min(3,len(seg)); X=StandardScaler().fit_transform(seg[features])
                km=KMeans(n_clusters=k,n_init=10,random_state=42); seg["Cluster"]=km.fit_predict(X)
                ranking=seg.groupby("Cluster")[features].mean().mean(axis=1).sort_values(ascending=False)
                names=["⭐ Star Performer","📊 Growth Product","📉 Needs Attention"]; labels={cluster:names[min(i,2)] for i,cluster in enumerate(ranking.index)}
                seg["Segment"]=seg["Cluster"].map(labels)
                x_feature="quantity" if "quantity" in seg.columns else features[0]; y_feature="profit" if "profit" in seg.columns else features[-1]
                fig_cl=px.scatter(seg,x=x_feature,y=y_feature,color="Segment",hover_name="product",title="AI Product / Service Segments",labels={x_feature:x_feature.title(),y_feature:y_feature.title()})
                fig_cl.update_layout(**CHART); st.plotly_chart(fig_cl,use_container_width=True); st.dataframe(seg,use_container_width=True,hide_index=True)

        # Recommendations
        st.markdown('<div class="gn-sep">AI Recommendations</div>',unsafe_allow_html=True)
        if has_product and 'pstats' in locals() and not pstats.empty:
            best=str(pstats.iloc[0]["product"]); weakest=str(pstats.iloc[-1]["product"])
            c1,c2=st.columns(2)
            with c1: st.success(f'💡 **Scale "{best}"**\n\nThis is currently the strongest item by {sort_col}. Consider increasing stock, marketing and visibility.')
            with c2: st.warning(f'⚠️ **Review "{weakest}"**\n\nThis item is currently weakest by {sort_col}. Consider repricing, bundling or reducing stock.')
        if has_profit and has_revenue:
            margin=(total_profit/total_revenue*100) if total_revenue else 0
            if total_profit<0: st.error("🔴 Overall loss detected. Costs are exceeding revenue.")
            elif margin<10: st.warning(f"🟡 Low-margin warning. Overall margin is {margin:.1f}%.")
            else: st.info(f"📈 Business is profitable with an overall margin of {margin:.1f}%.")

        st.markdown('<div class="gn-sep">Prepared Data Export</div>',unsafe_allow_html=True)
        st.download_button("📥 Download AI-Prepared CSV",dataframe_to_csv(df_ai),"growth_network_ai_prepared_data.csv","text/csv",use_container_width=True)