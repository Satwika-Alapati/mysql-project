"""
Dedicated User / Student Portal Page.
Direct access page for Students & Library Members.
Allows viewing live borrower circulation ('Who Took The Books'), adding books & e-books to catalog,
reading e-books with persistent study notes in MySQL, searching and borrowing books, and tracking loans.
"""

import streamlit as st
from database import test_connection
from views.student_view import render_student_portal
from views.login_view import render_user_login_page


# Page Configuration
st.set_page_config(
    page_title="User Portal — Digital Library",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
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
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

# Sidebar Controls
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
            <div style="background: linear-gradient(135deg, #065f46, #10b981); color: white; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                🎓
            </div>
            <div>
                <h3 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #1e293b;">User Portal</h3>
                <small style="color: #64748b;">Student Self-Service</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    db_ok, db_msg = test_connection()
    if db_ok:
        st.caption("🟢 MySQL Database Connected")
    else:
        st.error(f"❌ DB Offline: {db_msg}")

    st.divider()

    # User Account in Sidebar
    if st.session_state["logged_in"]:
        curr_user = st.session_state["user"]
        role_label = "🎓 Student Member" if curr_user["role"] == "student" else ("🛡️ System Administrator" if curr_user["role"] == "admin" else "👑 Chief Librarian")
        st.markdown(
            f"""
            <div style="padding: 12px; background: #f0fdf4; border-radius: 10px; border: 1px solid #bbf7d0; margin-bottom: 12px;">
                <small style="color: #15803d; font-size: 0.72rem; text-transform: uppercase; font-weight: 700;">Active Account</small>
                <div style="font-weight: 700; color: #1e293b; font-size: 0.95rem;">{curr_user.get('full_name')}</div>
                <div style="font-size: 0.8rem; color: #64748b;">@{curr_user.get('username')}</div>
                <div style="margin-top: 4px; font-size: 0.78rem; font-weight: 600; color: #059669;">{role_label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("🚪 Sign Out", use_container_width=True, type="secondary", key="usr_sidebar_signout"):
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.toast("Signed out successfully.")
            st.rerun()

    st.markdown("##### 🧭 Navigation Shortcuts")
    if st.button("🏠 Home / Portal Gateway", use_container_width=True, key="btn_usr_to_home"):
        st.switch_page("app.py")
    if st.button("🛡️ Go to Admin Portal", use_container_width=True, key="btn_usr_to_adm"):
        st.switch_page("pages/1_Admin_Portal.py")

    st.divider()
    st.caption("Digital Library System • User Page")


# Main Content Area
if not st.session_state["logged_in"]:
    render_user_login_page()
else:
    user = st.session_state["user"]
    if user["role"] == "student":
        render_student_portal(user)
    else:
        # User is logged in as an admin or librarian
        st.info(f"ℹ️ You are currently logged in as Administrator (**@{user['username']}**).")
        col_sw1, col_sw2 = st.columns(2)
        with col_sw1:
            if st.button("🛡️ Return to Admin Portal", type="primary", use_container_width=True):
                st.switch_page("pages/1_Admin_Portal.py")
        with col_sw2:
            if st.button("🚪 Sign Out to Login as Student", use_container_width=True):
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.rerun()
        
        st.divider()
        st.markdown("##### 👁️ Previewing Student View (Demo Profile):")
        # Find a student member for preview
        demo_student_info = {
            "user_id": 3,
            "username": "aarav",
            "role": "student",
            "member_id": 1,
            "full_name": "Aarav Sharma"
        }
        render_student_portal(demo_student_info)
