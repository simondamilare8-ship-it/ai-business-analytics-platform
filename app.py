import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import bcrypt
import smtplib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ──────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Growth Network",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
#  GLOBAL STYLES
# ──────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ─────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Instrument+Serif:ital@0;1&display=swap');

/* ── Palette ──────────────────────────────── */
:root {
  --white:        #ffffff;
  --bg:           #f5f7ff;
  --card:         #ffffff;
  --border:       #e4e9f7;
  --purple:       #6c63ff;
  --purple-light: #ede9ff;
  --purple-dark:  #4b44cc;
  --teal:         #00c9a7;
  --teal-light:   #e0faf5;
  --gold:         #f5a623;
  --gold-light:   #fff4e0;
  --red:          #ff5c72;
  --red-light:    #fff0f2;
  --text:         #1a1f36;
  --text-muted:   #6b7280;
  --text-soft:    #9ca3af;
  --shadow-sm:    0 2px 8px rgba(108,99,255,0.08);
  --shadow-md:    0 6px 24px rgba(108,99,255,0.13);
  --shadow-lg:    0 16px 48px rgba(108,99,255,0.18);
  --radius:       16px;
  --radius-sm:    10px;
}

/* ── Reset / Base ─────────────────────────── */
html, body, [class*="css"], .stApp {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
}

/* kill default Streamlit chrome */
[data-testid="stHeader"]     { background: transparent !important; height: 0 !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stToolbar"]    { display: none !important; }
footer                        { display: none !important; }
#MainMenu                     { display: none !important; }

/* ── Sidebar ──────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--white) !important;
  border-right: 1px solid var(--border) !important;
  box-shadow: 4px 0 24px rgba(108,99,255,0.06) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Main container ───────────────────────── */
.main .block-container {
  background: transparent !important;
  padding: 2rem 2.5rem 3rem !important;
  max-width: 1440px !important;
}

/* ── Page header ──────────────────────────── */
.gn-page-header {
  margin-bottom: 2rem;
}
.gn-page-title {
  font-family: 'Instrument Serif', serif;
  font-size: 2.4rem;
  font-weight: 400;
  font-style: italic;
  color: var(--text);
  line-height: 1.15;
  margin: 0 0 0.2rem 0;
}
.gn-page-title span {
  background: linear-gradient(135deg, var(--purple), var(--teal));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.gn-page-sub {
  font-size: 0.88rem;
  color: var(--text-muted);
  font-weight: 400;
  letter-spacing: 0.01em;
}

/* ── Metric cards ─────────────────────────── */
[data-testid="metric-container"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 1.5rem 1.6rem !important;
  box-shadow: var(--shadow-sm) !important;
  transition: box-shadow 0.25s, transform 0.25s;
}
[data-testid="metric-container"]:hover {
  box-shadow: var(--shadow-md) !important;
  transform: translateY(-3px);
}
[data-testid="metric-container"] label {
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.1em !important;
  color: var(--text-muted) !important;
}
[data-testid="stMetricValue"] {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 1.9rem !important;
  font-weight: 800 !important;
  color: var(--purple) !important;
}
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* ── Buttons ──────────────────────────────── */
.stButton > button {
  background: linear-gradient(135deg, var(--purple), var(--purple-dark)) !important;
  color: #fff !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.85rem !important;
  letter-spacing: 0.03em !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  padding: 0.6rem 1.5rem !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 4px 12px rgba(108,99,255,0.28) !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 24px rgba(108,99,255,0.38) !important;
  filter: brightness(1.06) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Inputs ───────────────────────────────── */
.stTextInput input,
.stNumberInput input,
[data-baseweb="input"] input {
  background: var(--bg) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 0.9rem !important;
  padding: 0.55rem 0.85rem !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput input:focus,
.stNumberInput input:focus {
  border-color: var(--purple) !important;
  box-shadow: 0 0 0 3px var(--purple-light) !important;
  outline: none !important;
}

/* Labels */
.stTextInput > label, .stNumberInput > label,
.stSelectbox > label, .stDateInput > label,
.stFileUploader > label, .stRadio > label {
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  color: var(--text-muted) !important;
  margin-bottom: 0.3rem !important;
}

/* Selectbox */
[data-baseweb="select"] > div:first-child {
  background: var(--bg) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
}

/* ── Dataframe ────────────────────────────── */
.stDataFrame, [data-testid="stDataFrame"] {
  border-radius: var(--radius) !important;
  overflow: hidden !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stDataFrame"] thead th {
  background: var(--bg) !important;
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.07em !important;
  color: var(--text-muted) !important;
}

/* ── Alerts ───────────────────────────────── */
[data-testid="stAlert"] {
  border-radius: var(--radius-sm) !important;
  border: none !important;
  font-size: 0.88rem !important;
}

/* ── File uploader ────────────────────────── */
[data-testid="stFileUploadDropzone"] {
  background: var(--bg) !important;
  border: 2px dashed var(--border) !important;
  border-radius: var(--radius) !important;
}
[data-testid="stFileUploadDropzone"]:hover {
  border-color: var(--purple) !important;
  background: var(--purple-light) !important;
}

/* ── Divider ──────────────────────────────── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Scrollbar ────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--purple); }

/* ── Sidebar brand ────────────────────────── */
.gn-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 0 1.4rem 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.2rem;
}
.gn-brand-icon {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--purple), var(--teal));
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}
.gn-brand-name {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--text) !important;
  letter-spacing: -0.01em;
}
.gn-brand-sub {
  font-size: 0.68rem;
  color: var(--text-soft) !important;
  font-weight: 500;
}

/* ── Sidebar user pill ────────────────────── */
.gn-user-pill {
  background: var(--purple-light);
  border-radius: var(--radius-sm);
  padding: 0.7rem 1rem;
  margin-bottom: 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.gn-user-avatar {
  width: 30px; height: 30px;
  background: linear-gradient(135deg, var(--purple), var(--purple-dark));
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.8rem;
  color: white !important;
  font-weight: 700;
  flex-shrink: 0;
}
.gn-user-name {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--purple) !important;
}
.gn-user-role {
  font-size: 0.68rem;
  color: var(--text-muted) !important;
}

/* ── Info / empty state box ───────────────── */
.gn-empty {
  background: var(--card);
  border: 1.5px dashed var(--border);
  border-radius: var(--radius);
  padding: 3rem 2rem;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.9rem;
}
.gn-empty-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }

/* ── Stat pill (inline badge) ─────────────── */
.gn-pill {
  display: inline-block;
  padding: 0.25rem 0.7rem;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 700;
}
.gn-pill-green { background: var(--teal-light); color: #007a67; }
.gn-pill-red   { background: var(--red-light);  color: #c0002a; }
.gn-pill-gold  { background: var(--gold-light);  color: #a06800; }

/* ── Login page ───────────────────────────── */
.gn-login-wrap {
  min-height: 88vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.gn-login-card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 3rem 2.8rem;
  box-shadow: var(--shadow-lg);
  width: 100%;
}
.gn-login-logo {
  text-align: center;
  margin-bottom: 0.3rem;
}
.gn-login-logo-icon {
  display: inline-flex;
  width: 54px; height: 54px;
  background: linear-gradient(135deg, var(--purple), var(--teal));
  border-radius: 16px;
  align-items: center; justify-content: center;
  font-size: 1.6rem;
  box-shadow: 0 8px 20px rgba(108,99,255,0.3);
  margin-bottom: 0.8rem;
}
.gn-login-title {
  font-family: 'Instrument Serif', serif;
  font-style: italic;
  font-size: 1.75rem;
  color: var(--text);
  text-align: center;
  margin-bottom: 0.2rem;
}
.gn-login-tagline {
  text-align: center;
  color: var(--text-muted);
  font-size: 0.83rem;
  margin-bottom: 1.8rem;
}
.gn-section-label {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin: 1.5rem 0 0.6rem 0;
}

/* ── Summary row cards ────────────────────── */
.gn-summary-card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.4rem 1.5rem;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s, transform 0.2s;
}
.gn-summary-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-3px);
}
.gn-card-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin-bottom: 0.4rem;
}
.gn-card-value {
  font-size: 1.9rem;
  font-weight: 800;
  color: var(--purple);
  line-height: 1.1;
}
.gn-card-value.teal  { color: var(--teal); }
.gn-card-value.gold  { color: var(--gold); }
.gn-card-value.red   { color: var(--red); }
.gn-card-icon {
  font-size: 1.4rem;
  float: right;
  margin-top: -2.4rem;
  opacity: 0.18;
}

/* ── Add sale form card ────────────────────── */
.gn-form-card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 2rem 2rem 1.5rem;
  box-shadow: var(--shadow-sm);
  margin-bottom: 1.5rem;
}

/* ── Preview banner ───────────────────────── */
.gn-preview {
  background: linear-gradient(135deg, var(--purple-light), var(--teal-light));
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 1.2rem 1.5rem;
  margin-top: 1rem;
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}
.gn-preview-item label {
  font-size: 0.68rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  color: var(--text-muted) !important;
  display: block;
}
.gn-preview-item .val {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--purple);
}
.gn-preview-item .val.profit { color: var(--teal); }

/* ── Radio tabs (sidebar) ─────────────────── */
[data-testid="stSidebar"] [data-baseweb="radio"] label {
  border-radius: var(--radius-sm) !important;
  padding: 0.5rem 0.9rem !important;
  font-size: 0.88rem !important;
  font-weight: 600 !important;
  color: var(--text-muted) !important;
  transition: background 0.18s, color 0.18s !important;
}
[data-testid="stSidebar"] [data-baseweb="radio"] label:hover {
  background: var(--purple-light) !important;
  color: var(--purple) !important;
}

/* ── Chart wrapper ────────────────────────── */
.gn-chart-card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.2rem 1rem 0.5rem;
  box-shadow: var(--shadow-sm);
}

/* ── Section separator label ──────────────── */
.gn-sep {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--text-soft);
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.4rem;
  margin: 2rem 0 1.2rem;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  PLOTLY SHARED THEME
# ──────────────────────────────────────────────
CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(245,247,255,0.6)",
    font=dict(family="Plus Jakarta Sans", color="#6b7280", size=12),
    title_font=dict(family="Plus Jakarta Sans", color="#1a1f36", size=15, weight="bold"),  # type: ignore
    xaxis=dict(gridcolor="#e4e9f7", linecolor="#e4e9f7", tickfont=dict(color="#9ca3af")),
    yaxis=dict(gridcolor="#e4e9f7", linecolor="#e4e9f7", tickfont=dict(color="#9ca3af")),
    margin=dict(l=10, r=10, t=45, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#6b7280")),
    coloraxis_colorbar=dict(tickfont=dict(color="#6b7280")),
)
PALETTE = ["#6c63ff", "#00c9a7", "#f5a623", "#ff5c72", "#a78bfa", "#34d399"]


# ──────────────────────────────────────────────
#  SECRETS
# ──────────────────────────────────────────────
EMAIL_SENDER   = st.secrets.get("EMAIL_SENDER", "")
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", "")


# ──────────────────────────────────────────────
#  SESSION STATE
# ──────────────────────────────────────────────
for _k in ["user", "reset_code", "reset_user"]:
    if _k not in st.session_state:
        st.session_state[_k] = None


# ──────────────────────────────────────────────
#  DATABASE
# ──────────────────────────────────────────────
DB_PATH = "business.db"

def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email    TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT,
            product       TEXT,
            quantity      INTEGER,
            cost_price    REAL,
            selling_price REAL,
            profit        REAL,
            date          TEXT,
            status        TEXT DEFAULT 'active'
        )
    """)
    conn.commit()
    conn.close()

init_db()

def load_sales(username):
    conn = get_db()
    df = pd.read_sql_query(
        "SELECT * FROM sales WHERE username=? AND status='active'",
        conn, params=(username,)
    )
    conn.close()
    return df


# ──────────────────────────────────────────────
#  SECURITY
# ──────────────────────────────────────────────
def hash_pw(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_pw(pw, hashed):
    return bcrypt.checkpw(pw.encode(), hashed.encode())


# ──────────────────────────────────────────────
#  EMAIL
# ──────────────────────────────────────────────
def send_email(to, subject, body):
    try:
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(EMAIL_SENDER, EMAIL_PASSWORD)
        s.sendmail(EMAIL_SENDER, to, f"Subject: {subject}\n\n{body}")
        s.quit()
        return True
    except Exception:
        return False


# ══════════════════════════════════════════════
#  AUTH  (shown when not logged in)
# ══════════════════════════════════════════════
if st.session_state.user is None:

    _, mid, _ = st.columns([1, 1.55, 1])
    with mid:
        st.markdown('<div class="gn-login-card">', unsafe_allow_html=True)

        # Logo
        st.markdown("""
        <div class="gn-login-logo">
          <div class="gn-login-logo-icon">📈</div>
        </div>
        <div class="gn-login-title">Growth Network</div>
        <div class="gn-login-tagline">Your intelligent business companion</div>
        """, unsafe_allow_html=True)

        mode = st.radio("", ["Login", "Register", "Forgot Password"],
                        horizontal=True, label_visibility="collapsed")
        st.markdown("<hr>", unsafe_allow_html=True)

        conn = get_db()
        cur  = conn.cursor()

        # ── Register ──────────────────────────
        if mode == "Register":
            username = st.text_input("Username", placeholder="Choose a username")
            email    = st.text_input("Email",    placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="Min 6 characters")
            confirm  = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")

            if st.button("Create My Account →", use_container_width=True):
                if not username or not email or not password:
                    st.warning("Please fill in all fields.")
                elif len(password) < 6:
                    st.warning("Password must be at least 6 characters.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                else:
                    cur.execute("SELECT id FROM users WHERE username=?", (username,))
                    if cur.fetchone():
                        st.error("That username is already taken.")
                    else:
                        cur.execute(
                            "INSERT INTO users (username, password, email) VALUES (?,?,?)",
                            (username, hash_pw(password), email)
                        )
                        conn.commit()
                        st.success("✅ Account created! Switch to Login.")

        # ── Login ─────────────────────────────
        elif mode == "Login":
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            if st.button("Sign In →", use_container_width=True):
                cur.execute("SELECT password FROM users WHERE username=?", (username,))
                row = cur.fetchone()
                if row and verify_pw(password, row[0]):
                    st.session_state.user = username
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

        # ── Forgot Password ────────────────────
        else:
            st.info("Please contact your admin to reset your password.")

        conn.close()
        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# ══════════════════════════════════════════════
#  MAIN APP  (logged in)
# ══════════════════════════════════════════════
user = st.session_state.user
df   = load_sales(user)

# ── Sidebar ────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown(f"""
    <div class="gn-brand">
      <div class="gn-brand-icon">📈</div>
      <div>
        <div class="gn-brand-name">Growth Network</div>
        <div class="gn-brand-sub">Business Intelligence</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # User pill
    initials = user[:2].upper()
    st.markdown(f"""
    <div class="gn-user-pill">
      <div class="gn-user-avatar">{initials}</div>
      <div>
        <div class="gn-user-name">{user}</div>
        <div class="gn-user-role">Business Owner</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Nav
    menu = st.radio(
        "Navigation",
        ["📊  Dashboard", "➕  Add Sale", "📈  Analytics",
         "🗂  History",   "🗑  Trash",    "🧠  AI Brain"],
        label_visibility="collapsed",
    )

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

    # Quick stats at bottom
    if not df.empty:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="gn-sep">Quick Stats</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:0.8rem; color:var(--text-muted); line-height:2;">
          💰 Total Profit: <b style="color:var(--teal)">₦{df['profit'].sum():,.0f}</b><br>
          📦 Sales: <b style="color:var(--purple)">{len(df)}</b><br>
          🏷 Products: <b style="color:var(--gold)">{df['product'].nunique()}</b>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════
if "Dashboard" in menu:
    st.markdown("""
    <div class="gn-page-header">
      <div class="gn-page-title">Good day, <span>let's grow.</span></div>
      <div class="gn-page-sub">Here's your business overview at a glance</div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.markdown("""
        <div class="gn-empty">
          <div class="gn-empty-icon">📭</div>
          <div><b>No sales data yet.</b></div>
          <div>Head to <b>Add Sale</b> to record your first transaction.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── KPI row ──
        total_profit  = df["profit"].sum()
        total_revenue = (df["selling_price"] * df["quantity"]).sum()
        total_cost    = (df["cost_price"]    * df["quantity"]).sum()
        avg_margin    = ((df["selling_price"] - df["cost_price"]) / df["selling_price"]).mean() * 100

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Sales",    len(df))
        c2.metric("Net Profit",     f"₦{total_profit:,.0f}")
        c3.metric("Revenue",        f"₦{total_revenue:,.0f}")
        c4.metric("Avg Margin",     f"{avg_margin:.1f}%")

        st.markdown('<div class="gn-sep">Performance Charts</div>', unsafe_allow_html=True)

        # ── Charts row ──
        left, right = st.columns([3, 2])

        with left:
            st.markdown('<div class="gn-chart-card">', unsafe_allow_html=True)
            summary = df.groupby("product").agg(
                profit=("profit","sum"),
                sales=("id","count")
            ).reset_index().sort_values("profit", ascending=False)
            fig = px.bar(
                summary, x="product", y="profit",
                color="profit",
                color_continuous_scale=["#ede9ff","#6c63ff"],
                labels={"product":"Product","profit":"Profit (₦)"},
                title="Profit by Product",
                text_auto=".2s",
            )
            fig.update_traces(marker_line_width=0, textfont_size=10, textfont_color="#6b7280")
            fig.update_layout(**CHART)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with right:
            st.markdown('<div class="gn-chart-card">', unsafe_allow_html=True)
            pie = df.groupby("product")["profit"].sum().reset_index()
            fig2 = px.pie(
                pie, names="product", values="profit",
                title="Profit Share",
                color_discrete_sequence=PALETTE,
                hole=0.45,
            )
            fig2.update_layout(**CHART)
            fig2.update_traces(textfont_size=11)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Recent sales table ──
        st.markdown('<div class="gn-sep">Recent Transactions</div>', unsafe_allow_html=True)
        recent = df.sort_values("date", ascending=False).head(10)
        display = recent[["date","product","quantity","cost_price","selling_price","profit"]].rename(columns={
            "date":"Date","product":"Product","quantity":"Qty",
            "cost_price":"Cost (₦)","selling_price":"Price (₦)","profit":"Profit (₦)"
        })
        st.dataframe(display, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
#  ADD SALE
# ══════════════════════════════════════════════
elif "Add Sale" in menu:
    st.markdown("""
    <div class="gn-page-header">
      <div class="gn-page-title">Record a <span>new sale</span></div>
      <div class="gn-page-sub">Fill in the details below to log a transaction</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="gn-form-card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        product = st.text_input("Product Name", placeholder="e.g. Ankara Fabric")
    with col2:
        qty = st.number_input("Quantity", min_value=1, value=1, step=1)

    col3, col4 = st.columns(2)
    with col3:
        cost = st.number_input("Cost Price (₦)", min_value=0.0, step=100.0, format="%.2f")
    with col4:
        sell = st.number_input("Selling Price (₦)", min_value=0.0, step=100.0, format="%.2f")

    # Live preview
    if cost > 0 and sell > 0 and qty > 0:
        proj_profit  = (sell - cost) * qty
        revenue      = sell * qty
        margin       = (sell - cost) / sell * 100 if sell > 0 else 0
        profit_color = "profit" if proj_profit >= 0 else "red"
        st.markdown(f"""
        <div class="gn-preview">
          <div class="gn-preview-item">
            <label>Revenue</label>
            <div class="val">₦{revenue:,.0f}</div>
          </div>
          <div class="gn-preview-item">
            <label>Profit</label>
            <div class="val {profit_color}">₦{proj_profit:,.0f}</div>
          </div>
          <div class="gn-preview-item">
            <label>Margin</label>
            <div class="val">{margin:.1f}%</div>
          </div>
          <div class="gn-preview-item">
            <label>Total Cost</label>
            <div class="val">₦{cost*qty:,.0f}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("💾  Save Sale", use_container_width=True):
        if not product.strip():
            st.warning("Please enter a product name.")
        elif sell < cost:
            st.warning("⚠️ Selling price is below cost — you'll make a loss.")
        else:
            profit_val = (sell - cost) * qty
            date_str   = datetime.now().strftime("%Y-%m-%d")
            conn = get_db(); cur = conn.cursor()
            cur.execute("""
                INSERT INTO sales
                  (username, product, quantity, cost_price, selling_price, profit, date, status)
                VALUES (?,?,?,?,?,?,?,'active')
            """, (user, product.strip(), qty, cost, sell, profit_val, date_str))
            conn.commit(); conn.close()
            st.success(f"✅ Sale saved! Profit: ₦{profit_val:,.2f}")
            st.balloons()


# ══════════════════════════════════════════════
#  ANALYTICS
# ══════════════════════════════════════════════
elif "Analytics" in menu:
    st.markdown("""
    <div class="gn-page-header">
      <div class="gn-page-title">Business <span>Analytics</span></div>
      <div class="gn-page-sub">Trends, forecasts and performance over time</div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.markdown('<div class="gn-empty"><div class="gn-empty-icon">📉</div><div>No data to analyse yet.</div></div>', unsafe_allow_html=True)
    else:
        df["date"] = pd.to_datetime(df["date"])
        monthly = df.groupby(df["date"].dt.to_period("M")).agg(
            profit=("profit","sum"),
            sales=("id","count")
        ).reset_index()
        monthly["date_str"] = monthly["date"].astype(str)

        # KPIs
        c1, c2, c3 = st.columns(3)
        c1.metric("Best Month Profit",  f"₦{monthly['profit'].max():,.0f}")
        c2.metric("Avg Monthly Profit", f"₦{monthly['profit'].mean():,.0f}")
        if len(monthly) > 1:
            x = np.arange(len(monthly))
            m, b = np.polyfit(x, monthly["profit"].values, 1)
            c3.metric("Next Month Forecast", f"₦{m*(len(x)+1)+b:,.0f}")

        st.markdown('<div class="gn-sep">Monthly Profit Trend</div>', unsafe_allow_html=True)

        # Trend chart
        st.markdown('<div class="gn-chart-card">', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["date_str"], y=monthly["profit"],
            mode="lines+markers",
            line=dict(color="#6c63ff", width=3),
            marker=dict(size=9, color="#6c63ff",
                        line=dict(color="white", width=2)),
            fill="tozeroy",
            fillcolor="rgba(108,99,255,0.07)",
            name="Profit",
        ))
        if len(monthly) > 1:
            trend_y = m * x + b
            fig.add_trace(go.Scatter(
                x=monthly["date_str"], y=trend_y,
                mode="lines",
                line=dict(color="#f5a623", width=2, dash="dot"),
                name="Trend",
            ))
        fig.update_layout(title="Monthly Profit", **CHART)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Sales volume bar
        st.markdown('<div class="gn-sep">Sales Volume per Month</div>', unsafe_allow_html=True)
        st.markdown('<div class="gn-chart-card">', unsafe_allow_html=True)
        fig2 = px.bar(
            monthly, x="date_str", y="sales",
            title="Monthly Sales Count",
            color_discrete_sequence=["#00c9a7"],
            labels={"date_str":"Month","sales":"Transactions"},
        )
        fig2.update_layout(**CHART)
        fig2.update_traces(marker_line_width=0)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  HISTORY
# ══════════════════════════════════════════════
elif "History" in menu:
    st.markdown("""
    <div class="gn-page-header">
      <div class="gn-page-title">Transaction <span>History</span></div>
      <div class="gn-page-sub">Browse and filter your past sales</div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.markdown('<div class="gn-empty"><div class="gn-empty-icon">🗂</div><div>No history yet.</div></div>', unsafe_allow_html=True)
    else:
        df["date"] = pd.to_datetime(df["date"])

        col_f, _ = st.columns([1, 3])
        with col_f:
            option = st.selectbox("Filter by", ["Daily", "Monthly", "Yearly"])

        if option == "Daily":
            d = st.date_input("Pick a date")
            filtered = df[df["date"].dt.date == d]
        elif option == "Monthly":
            df["_m"] = df["date"].dt.to_period("M")
            m = st.selectbox("Month", sorted(df["_m"].unique(), reverse=True))
            filtered = df[df["_m"] == m]
        else:
            df["_y"] = df["date"].dt.year
            y = st.selectbox("Year", sorted(df["_y"].unique(), reverse=True))
            filtered = df[df["_y"] == y]

        # Summary
        rev = (filtered["selling_price"] * filtered["quantity"]).sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("Transactions", len(filtered))
        c2.metric("Net Profit",   f"₦{filtered['profit'].sum():,.0f}")
        c3.metric("Revenue",      f"₦{rev:,.0f}")

        st.dataframe(
            filtered[["date","product","quantity","cost_price","selling_price","profit"]].rename(columns={
                "date":"Date","product":"Product","quantity":"Qty",
                "cost_price":"Cost (₦)","selling_price":"Sell (₦)","profit":"Profit (₦)"
            }).sort_values("Date", ascending=False),
            use_container_width=True, hide_index=True
        )


# ══════════════════════════════════════════════
#  TRASH
# ══════════════════════════════════════════════
elif "Trash" in menu:
    st.markdown("""
    <div class="gn-page-header">
      <div class="gn-page-title">🗑  <span>Trash</span></div>
      <div class="gn-page-sub">Records moved to trash — restore or delete permanently</div>
    </div>
    """, unsafe_allow_html=True)

    conn = get_db()
    trash = pd.read_sql_query(
        "SELECT * FROM sales WHERE username=? AND status='deleted'",
        conn, params=(user,)
    )
    conn.close()

    if trash.empty:
        st.markdown('<div class="gn-empty"><div class="gn-empty-icon">✨</div><div>Trash is empty.</div></div>', unsafe_allow_html=True)
    else:
        st.dataframe(trash, use_container_width=True, hide_index=True)

        col1, col2, _ = st.columns([1.2, 1.2, 2])
        with col1:
            if st.button("♻️  Restore All", use_container_width=True):
                conn = get_db(); cur = conn.cursor()
                cur.execute("UPDATE sales SET status='active' WHERE username=?", (user,))
                conn.commit(); conn.close()
                st.success("All records restored!")
                st.rerun()
        with col2:
            if st.button("🗑  Delete Forever", use_container_width=True):
                conn = get_db(); cur = conn.cursor()
                cur.execute("DELETE FROM sales WHERE username=? AND status='deleted'", (user,))
                conn.commit(); conn.close()
                st.success("Permanently deleted.")
                st.rerun()


# ══════════════════════════════════════════════
#  AI BRAIN
# ══════════════════════════════════════════════
elif "AI" in menu:
    st.markdown("""
    <div class="gn-page-header">
      <div class="gn-page-title">🧠  AI <span>Business Brain</span></div>
      <div class="gn-page-sub">Upload your Excel data for forecasting, segmentation & insights</div>
    </div>
    """, unsafe_allow_html=True)

    file = st.file_uploader(
        "Drop your Excel file here (.xlsx)",
        type=["xlsx"],
        help="Required columns: date, product, quantity, cost_price, selling_price"
    )

    if file:
        df_ai = pd.read_excel(file)

        st.markdown('<div class="gn-sep">Data Preview</div>', unsafe_allow_html=True)
        st.dataframe(df_ai.head(20), use_container_width=True, hide_index=True)

        required = ["date","product","quantity","cost_price","selling_price"]
        missing  = [c for c in required if c not in df_ai.columns]

        if missing:
            st.error(f"Missing columns: **{', '.join(missing)}**")
            st.info("Your file must have: " + ", ".join(required))
        else:
            # Clean
            df_ai["date"]          = pd.to_datetime(df_ai["date"], errors="coerce")
            df_ai                  = df_ai.dropna(subset=["date"])
            df_ai["quantity"]      = pd.to_numeric(df_ai["quantity"],      errors="coerce").fillna(0)
            df_ai["cost_price"]    = pd.to_numeric(df_ai["cost_price"],    errors="coerce").fillna(0)
            df_ai["selling_price"] = pd.to_numeric(df_ai["selling_price"], errors="coerce").fillna(0)
            df_ai["profit"]        = (df_ai["selling_price"] - df_ai["cost_price"]) * df_ai["quantity"]

            st.success(f"✅ Loaded **{len(df_ai):,}** rows across **{df_ai['product'].nunique()}** products.")

            # ── Summary KPIs ──────────────────────
            st.markdown('<div class="gn-sep">Business Summary</div>', unsafe_allow_html=True)
            total_p   = df_ai["profit"].sum()
            total_qty = df_ai["quantity"].sum()
            total_rev = (df_ai["selling_price"] * df_ai["quantity"]).sum()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Profit",  f"₦{total_p:,.2f}")
            c2.metric("Units Sold",    f"{int(total_qty):,}")
            c3.metric("Revenue",       f"₦{total_rev:,.2f}")
            c4.metric("Products",      df_ai["product"].nunique())

            # ── Forecast ─────────────────────────
            st.markdown('<div class="gn-sep">30-Day Profit Forecast</div>', unsafe_allow_html=True)
            try:
                from prophet import Prophet  # noqa

                sales_ts = df_ai.groupby("date")["profit"].sum().reset_index()
                sales_ts.columns = ["ds", "y"]
                sales_ts = sales_ts.sort_values("ds")

                if len(sales_ts) < 10:
                    st.warning("Need at least 10 days of data for a reliable forecast.")
                else:
                    with st.spinner("Running AI forecast…"):
                        mdl = Prophet(daily_seasonality=False)
                        mdl.fit(sales_ts)
                        fut  = mdl.make_future_dataframe(periods=30)
                        fcst = mdl.predict(fut)

                    st.markdown('<div class="gn-chart-card">', unsafe_allow_html=True)
                    fig_f = go.Figure()
                    fig_f.add_trace(go.Scatter(
                        x=fcst["ds"], y=fcst["yhat_upper"],
                        fill=None, mode="lines",
                        line=dict(width=0, color="rgba(0,201,167,0)"),
                        showlegend=False,
                    ))
                    fig_f.add_trace(go.Scatter(
                        x=fcst["ds"], y=fcst["yhat_lower"],
                        fill="tonexty", mode="lines",
                        fillcolor="rgba(0,201,167,0.1)",
                        line=dict(width=0),
                        name="Confidence Band",
                    ))
                    fig_f.add_trace(go.Scatter(
                        x=fcst["ds"], y=fcst["yhat"],
                        mode="lines", name="Forecast",
                        line=dict(color="#6c63ff", width=2.5),
                    ))
                    fig_f.add_trace(go.Scatter(
                        x=sales_ts["ds"], y=sales_ts["y"],
                        mode="markers", name="Actual",
                        marker=dict(color="#00c9a7", size=5),
                    ))
                    fig_f.update_layout(title="Profit Forecast — Next 30 Days", **CHART)
                    st.plotly_chart(fig_f, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    next30 = fcst["yhat"].tail(30).sum()
                    if next30 >= 0:
                        st.success(f"📈 Projected profit for next 30 days: **₦{next30:,.2f}**")
                    else:
                        st.error(f"📉 Warning — projected loss of **₦{abs(next30):,.2f}** over next 30 days.")

            except ImportError:
                st.warning("Prophet is not installed. Run `pip install prophet` to enable forecasting.")

            # ── Product Intelligence ──────────────
            st.markdown('<div class="gn-sep">Product Intelligence</div>', unsafe_allow_html=True)

            pstats = df_ai.groupby("product").agg(
                quantity=("quantity","sum"),
                profit=("profit","sum"),
                transactions=("profit","count"),
            ).reset_index().sort_values("profit", ascending=False)

            top5  = pstats.head(5)
            bot5  = pstats.tail(5)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🔥 Top 5 Performers**")
                st.dataframe(top5, use_container_width=True, hide_index=True)
            with col2:
                st.markdown("**⚠️ Bottom 5 — Needs Review**")
                st.dataframe(bot5, use_container_width=True, hide_index=True)

            st.markdown('<div class="gn-chart-card">', unsafe_allow_html=True)
            fig_p = px.bar(
                pstats, x="product", y="profit",
                color="profit",
                color_continuous_scale=["#ede9ff","#6c63ff"],
                title="All Products — Profit Breakdown",
                labels={"product":"Product","profit":"Profit (₦)"},
                text_auto=".2s",
            )
            fig_p.update_layout(**CHART)
            fig_p.update_traces(marker_line_width=0)
            st.plotly_chart(fig_p, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Segmentation ──────────────────────
            st.markdown('<div class="gn-sep">Smart Product Segmentation (AI Clustering)</div>', unsafe_allow_html=True)

            from sklearn.cluster import KMeans  # noqa

            cdata = df_ai.groupby("product").agg(
                quantity=("quantity","sum"),
                profit=("profit","sum"),
            ).reset_index()

            if len(cdata) < 2:
                st.warning("Need at least 2 products for segmentation.")
            else:
                k = min(3, len(cdata))
                km = KMeans(n_clusters=k, n_init=10, random_state=42)
                cdata["Segment"] = km.fit_predict(cdata[["quantity","profit"]])
                seg_map = {0: "⭐ Star", 1: "📊 Average", 2: "📉 Low"}
                cdata["Segment"] = cdata["Segment"].map(
                    lambda x: seg_map.get(x, str(x))
                )
                color_map = {"⭐ Star":"#6c63ff","📊 Average":"#f5a623","📉 Low":"#ff5c72"}

                st.markdown('<div class="gn-chart-card">', unsafe_allow_html=True)
                fig_cl = px.scatter(
                    cdata, x="quantity", y="profit",
                    color="Segment", hover_name="product",
                    size=abs(cdata["profit"]).clip(lower=1),
                    color_discrete_map=color_map,
                    title="Product Clusters",
                    labels={"quantity":"Units Sold","profit":"Profit (₦)"},
                )
                fig_cl.update_layout(**CHART)
                st.plotly_chart(fig_cl, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.dataframe(cdata, use_container_width=True, hide_index=True)

            # ── AI Insights ───────────────────────
            st.markdown('<div class="gn-sep">AI Insights & Recommendations</div>', unsafe_allow_html=True)

            if not pstats.empty:
                best_prod = pstats.iloc[0]["product"]
                weak_prod = pstats.iloc[-1]["product"]

                col_i1, col_i2 = st.columns(2)
                with col_i1:
                    st.success(f"💡 **Scale up '{best_prod}'** — your highest-earning product. Increase stock and prioritise this line.")
                with col_i2:
                    st.warning(f"⚠️ **Review '{weak_prod}'** — lowest performer. Consider repricing, bundling or discontinuing.")

                if total_p < 0:
                    st.error("🔴 **Overall Loss Detected.** Your total costs exceed revenue. Review pricing strategy urgently.")
                elif total_p < total_rev * 0.1:
                    st.warning("🟡 **Low Margin Alert.** Profit is less than 10% of revenue. Consider cutting costs or raising prices.")
                else:
                    st.info("📈 **Business is Profitable!** Keep scaling — focus on your top products and reinvest profits.")
