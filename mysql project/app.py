"""
Main Application Entry Point & Master Portal Gateway.
Provides direct links to the dedicated Admin and User portals,
as well as unified authentication and system oversight.
"""

import streamlit as st
from database import test_connection, execute_query
from views.login_view import render_login_page
from views.admin_view import render_admin_dashboard
from views.librarian_view import render_librarian_portal
from views.student_view import render_student_portal

# Configure Page
st.set_page_config(
    page_title="Digital Library & Circulation Gateway",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Aesthetic Styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }

    div[data-testid="stMetric"] {
        background: var(--secondary-background-color, #1e293b) !important;
        border: 1px solid rgba(128, 128, 128, 0.25) !important;
        padding: 16px 20px !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15) !important;
        border-color: #6366f1 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricLabel"],
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] * {
        color: var(--text-color, inherit) !important;
        opacity: 0.9 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"],
    div[data-testid="stMetric"] [data-testid="stMetricValue"] * {
        color: var(--text-color, inherit) !important;
        font-weight: 800 !important;
    }

    /* GLOBAL CONTRAST FIX FOR CARDS & BANNERS IN DARK MODE */
    div[data-testid="stMarkdownContainer"] div[style*="background: #ecfdf5"],
    div[data-testid="stMarkdownContainer"] div[style*="background:#ecfdf5"],
    div[data-testid="stMarkdownContainer"] div[style*="background: #f0fdf4"],
    div[data-testid="stMarkdownContainer"] div[style*="background:#f0fdf4"] {
        color: #064e3b !important;
    }
    div[data-testid="stMarkdownContainer"] div[style*="background: #ecfdf5"] *,
    div[data-testid="stMarkdownContainer"] div[style*="background:#ecfdf5"] *,
    div[data-testid="stMarkdownContainer"] div[style*="background: #f0fdf4"] *,
    div[data-testid="stMarkdownContainer"] div[style*="background:#f0fdf4"] * {
        color: #064e3b !important;
    }

    div[data-testid="stMarkdownContainer"] div[style*="background: #eef2ff"],
    div[data-testid="stMarkdownContainer"] div[style*="background:#eef2ff"] {
        color: #1e1b4b !important;
    }
    div[data-testid="stMarkdownContainer"] div[style*="background: #eef2ff"] *,
    div[data-testid="stMarkdownContainer"] div[style*="background:#eef2ff"] * {
        color: #1e1b4b !important;
    }

    div[data-testid="stMarkdownContainer"] div[style*="background: #fef2f2"],
    div[data-testid="stMarkdownContainer"] div[style*="background:#fef2f2"] {
        color: #7f1d1d !important;
    }
    div[data-testid="stMarkdownContainer"] div[style*="background: #fef2f2"] *,
    div[data-testid="stMarkdownContainer"] div[style*="background:#fef2f2"] * {
        color: #7f1d1d !important;
    }

    div[data-testid="stMarkdownContainer"] div[style*="background: #f8fafc"],
    div[data-testid="stMarkdownContainer"] div[style*="background:#f8fafc"],
    div[data-testid="stMarkdownContainer"] div[style*="background: #f1f5f9"],
    div[data-testid="stMarkdownContainer"] div[style*="background:#f1f5f9"],
    div[data-testid="stMarkdownContainer"] div[style*="background: #ffffff"],
    div[data-testid="stMarkdownContainer"] div[style*="background:#ffffff"],
    div[data-testid="stMarkdownContainer"] div[style*="background: white"],
    div[data-testid="stMarkdownContainer"] div[style*="background:white"] {
        color: #0f172a !important;
    }
    div[data-testid="stMarkdownContainer"] div[style*="background: #f8fafc"] strong,
    div[data-testid="stMarkdownContainer"] div[style*="background: #f1f5f9"] strong,
    div[data-testid="stMarkdownContainer"] div[style*="background: #ffffff"] strong,
    div[data-testid="stMarkdownContainer"] div[style*="background: white"] strong {
        color: #0f172a !important;
    }
    div[data-testid="stMarkdownContainer"] div[style*="background: #f8fafc"] p,
    div[data-testid="stMarkdownContainer"] div[style*="background: #f1f5f9"] p,
    div[data-testid="stMarkdownContainer"] div[style*="background: #ffffff"] p,
    div[data-testid="stMarkdownContainer"] div[style*="background: white"] p {
        color: #334155 !important;
    }
    div[data-testid="stMarkdownContainer"] div[style*="background: #f8fafc"] code,
    div[data-testid="stMarkdownContainer"] div[style*="background: #ffffff"] code,
    div[data-testid="stMarkdownContainer"] div[style*="background: white"] code {
        color: #0f172a !important;
        background: #e2e8f0 !important;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
    }

    .portal-card {
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        background: #ffffff;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .portal-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None


# Sidebar Navigation & System Status
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
            <div style="background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 22px;">
                📚
            </div>
            <div>
                <h3 style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b;">Digital Library</h3>
                <small style="color: #64748b;">Circulation System</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Database connectivity indicator
    db_ok, db_msg = test_connection()
    if db_ok:
        st.markdown(
            """
            <div style="padding: 6px 12px; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 20px; font-size: 0.78rem; color: #065f46; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; margin-bottom: 15px;">
                <span style="display: inline-block; width: 8px; height: 8px; background: #10b981; border-radius: 50%;"></span>
                MySQL Connected (Port 3306)
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error(f"❌ DB Offline: {db_msg}")

    st.markdown("##### 🧭 Dedicated Pages")
    if st.button("🛡️ Open Admin Portal", use_container_width=True):
        st.switch_page("pages/1_Admin_Portal.py")
    if st.button("🎓 Open User / Student Portal", use_container_width=True):
        st.switch_page("pages/2_User_Portal.py")

    st.divider()

    # User Status in Sidebar
    if st.session_state["logged_in"]:
        curr_user = st.session_state["user"]
        if curr_user["role"] == "admin":
            role_label = "🛡️ System Administrator"
        elif curr_user["role"] == "librarian":
            role_label = "👑 Chief Librarian"
        else:
            role_label = "🎓 Student Member"

        st.markdown(
            f"""
            <div style="padding: 12px; background: #f1f5f9; border-radius: 10px; margin-bottom: 15px;">
                <small style="color: #64748b; font-size: 0.75rem; text-transform: uppercase; font-weight: 700;">Active Account</small>
                <div style="font-weight: 700; color: #1e293b; font-size: 1rem; margin-top: 2px;">{curr_user.get('full_name')}</div>
                <div style="font-size: 0.82rem; color: #475569;">@{curr_user.get('username')}</div>
                <div style="margin-top: 6px; font-size: 0.8rem; font-weight: 600; color: #4338ca;">{role_label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.toast("Signed out successfully.")
            st.rerun()

    else:
        st.caption("Choose a dedicated portal or sign in below.")

    st.divider()
    st.markdown(
        """
        <div style="color: #94a3b8; font-size: 0.75rem; text-align: center;">
            <strong>Digital Library System</strong><br>
            Python • MySQL 8.0 • Streamlit • Plotly<br>
            Dedicated Admin & User Portals
        </div>
        """,
        unsafe_allow_html=True
    )


# HERO HEADER
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 30px;">
        <div style="display: inline-block; background: linear-gradient(135deg, #4f46e5, #7c3aed); padding: 18px 22px; border-radius: 20px; box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);">
            <span style="font-size: 38px;">📚</span>
        </div>
        <h1 style="margin-top: 15px; margin-bottom: 5px; font-weight: 800; font-size: 2.3rem; background: linear-gradient(135deg, #4f46e5, #9333ea); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Digital Library & Circulation System
        </h1>
        <p style="color: #64748b; font-size: 1.05rem; max-width: 650px; margin: 0 auto;">
            Separate dedicated portals for Administrators and Students. Select your destination below:
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# PORTAL SELECTION CARDS
p_col1, p_col2 = st.columns(2)

with p_col1:
    st.markdown(
        """
        <div style="padding: 22px; border-radius: 14px; background: linear-gradient(135deg, #ffffff, #f8fafc); border: 1.5px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.05); min-height: 250px;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <span style="font-size: 30px;">🛡️</span>
                <div>
                    <h3 style="margin: 0; color: #1e1b4b; font-size: 1.3rem; font-weight: 700;">Admin Portal</h3>
                    <small style="color: #6366f1; font-weight: 600;">For Administrators & Librarians</small>
                </div>
            </div>
            <p style="color: #475569; font-size: 0.92rem; line-height: 1.6; margin-bottom: 16px;">
                Complete management hub: Add books manually or via Open Library API, view live borrowers (<strong>"Who Took The Books"</strong>), manage physical barcode copies, calculate fines, and handle circulation.
            </p>
            <ul style="color: #64748b; font-size: 0.85rem; padding-left: 20px; margin-bottom: 15px;">
                <li>👥 Real-time Borrower Tracker & Active Loans</li>
                <li>➕ Add Books with 1-Click API Auto-Fill</li>
                <li>🏷️ Barcode inventory & shelf tracking</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("🚀 Enter Admin Portal ➔", type="primary", use_container_width=True, key="btn_main_enter_adm"):
        st.switch_page("pages/1_Admin_Portal.py")

with p_col2:
    st.markdown(
        """
        <div style="padding: 22px; border-radius: 14px; background: linear-gradient(135deg, #ffffff, #f0fdf4); border: 1.5px solid #bbf7d0; box-shadow: 0 4px 15px rgba(0,0,0,0.05); min-height: 250px;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <span style="font-size: 30px;">🎓</span>
                <div>
                    <h3 style="margin: 0; color: #064e3b; font-size: 1.3rem; font-weight: 700;">User / Student Portal</h3>
                    <small style="color: #059669; font-weight: 600;">For Students & Members</small>
                </div>
            </div>
            <p style="color: #475569; font-size: 0.92rem; line-height: 1.6; margin-bottom: 16px;">
                Full-featured student workspace: See <strong>"Who Took The Books"</strong> live tracker, <strong>Add new books & e-books</strong> to the catalog, access persistent <strong>E-Books with in-browser reader</strong>, and borrow physical titles.
            </p>
            <ul style="color: #64748b; font-size: 0.85rem; padding-left: 20px; margin-bottom: 15px;">
                <li>👥 <strong>Who Took The Books:</strong> Live borrower & checkout transparency</li>
                <li>➕ <strong>Add Books & E-Books:</strong> 1-Click API auto-fill + manual entry</li>
                <li>📱 <strong>E-Books Library:</strong> Online study reader, downloads & notes in MySQL</li>
                <li>📖 <strong>Borrow & Reserve:</strong> 1-Click checkouts & automated queue</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("📚 Enter User Portal ➔", type="primary", use_container_width=True, key="btn_main_enter_usr"):
        st.switch_page("pages/2_User_Portal.py")

st.divider()

# LIVE SYSTEM STATS ROW
try:
    s_books = execute_query("SELECT COUNT(*) AS c FROM books", fetchone=True)["c"]
    s_copies = execute_query("SELECT COUNT(*) AS c FROM book_copies", fetchone=True)["c"]
    s_loans = execute_query("SELECT COUNT(*) AS c FROM issues WHERE return_date IS NULL", fetchone=True)["c"]
    s_members = execute_query("SELECT COUNT(*) AS c FROM members WHERE status = 'Active'", fetchone=True)["c"]
except Exception:
    s_books, s_copies, s_loans, s_members = 0, 0, 0, 0

sc1, sc2, sc3, sc4, sc5 = st.columns(5)
sc1.metric("📖 Catalog Titles", s_books)
sc2.metric("🏷️ Physical Copies", s_copies)
sc3.metric("📤 Books Currently Out", s_loans)
sc4.metric("👥 Active Members", s_members)
sc5.metric("🌐 Digital E-Books", "70,000+")

st.write("")

# SIGN-IN EXPANDER (QUICK ACCESS)
with st.expander("🔐 Or Sign In Directly on Gateway Screen", expanded=not st.session_state["logged_in"]):
    if not st.session_state["logged_in"]:
        render_login_page()
    else:
        user = st.session_state["user"]
        st.success(f"Signed in as **{user['full_name']}** (@{user['username']}) — Role: **{user['role'].upper()}**")
        col_dir1, col_dir2 = st.columns(2)
        with col_dir1:
            if user["role"] in ["admin", "librarian"]:
                if st.button("🛡️ Open My Admin Dashboard", type="primary", use_container_width=True):
                    st.switch_page("pages/1_Admin_Portal.py")
        with col_dir2:
            if user["role"] == "student":
                if st.button("🎓 Open My Student Portal", type="primary", use_container_width=True):
                    st.switch_page("pages/2_User_Portal.py")
