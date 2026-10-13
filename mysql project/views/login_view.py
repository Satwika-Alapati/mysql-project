"""
Login, Multi-Role Registration (Admin, Librarian, Student),
Password Recovery & Reset, and Dedicated Portal Gateways.
Provides:
1. render_login_page(): Gateway login with multi-role registration & password reset.
2. render_admin_login_page(): Dedicated Admin login + New Admin/Staff Registration form.
3. render_user_login_page(): Dedicated Student login + Registration form.
"""

import streamlit as st
from auth import (
    verify_user,
    register_user,
    register_student,
    register_admin,
    reset_user_password,
    get_demo_accounts
)


def render_login_page():
    """Unified login page used by main gateway."""
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 25px;">
            <div style="display: inline-block; background: linear-gradient(135deg, #4f46e5, #7c3aed); padding: 18px 22px; border-radius: 20px; box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);">
                <span style="font-size: 38px;">📚</span>
            </div>
            <h1 style="margin-top: 15px; margin-bottom: 5px; font-weight: 800; font-size: 2.2rem; background: linear-gradient(135deg, #4f46e5, #9333ea); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Digital Library & Book Circulation System
            </h1>
            <p style="color: #64748b; font-size: 1.05rem; max-width: 600px; margin: 0 auto;">
                Smart catalog tracking, physical copy availability, automated loans, and reservations powered by MySQL
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        tab_login, tab_register, tab_reset, tab_demo = st.tabs([
            "🔐 Sign In",
            "📝 Create New Account",
            "🔑 Reset / Update Password",
            "⚡ Quick Demo Access"
        ])

        # TAB 1: LOGIN
        with tab_login:
            st.markdown("##### Access Your Library Account")
            with st.form("main_login_form", clear_on_submit=False):
                username_input = st.text_input("Username", placeholder="e.g. admin, librarian, aarav, abc")
                password_input = st.text_input("Password", type="password", placeholder="Enter your account password")
                submitted = st.form_submit_button("Sign In to Portal", use_container_width=True, type="primary")

                if submitted:
                    success, result = verify_user(username_input, password_input)
                    if success:
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = result
                        st.toast(f"Welcome back, {result['full_name']}! 👋", icon="🎉")
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")

        # TAB 2: REGISTRATION (STUDENT OR ADMIN / STAFF)
        with tab_register:
            st.markdown("##### Create a New Library Account")
            st.caption("New accounts are stored immediately in the MySQL database with complete persistence.")
            
            with st.form("main_register_form", clear_on_submit=False):
                role_choice = st.selectbox(
                    "Account Type / Role *",
                    options=["Student (Borrower)", "Administrator (Full Staff Access)", "Librarian (Circulation Desk)"],
                    index=0
                )
                
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    new_full_name = st.text_input("Full Name *", placeholder="e.g. Priya Sharma")
                    new_username = st.text_input("Desired Username *", placeholder="e.g. priya24")
                with col_r2:
                    new_email = st.text_input("Email Address *", placeholder="priya@college.edu")
                    new_phone = st.text_input("Phone Number", placeholder="e.g. 9876543210")

                col_r3, col_r4 = st.columns(2)
                with col_r3:
                    new_password = st.text_input("Password *", type="password", placeholder="Minimum 4 characters")
                with col_r4:
                    confirm_pwd = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password")

                new_address = st.text_input("Department / Address", placeholder="e.g. Computer Science - Year 3")

                reg_submitted = st.form_submit_button("Register & Save to Database", use_container_width=True, type="primary")

                if reg_submitted:
                    if new_password != confirm_pwd:
                        st.error("❌ Passwords do not match. Please verify your password entry.")
                    else:
                        # Determine role string
                        if "Administrator" in role_choice:
                            role_str = "admin"
                        elif "Librarian" in role_choice:
                            role_str = "librarian"
                        else:
                            role_str = "student"

                        reg_ok, reg_res = register_user(
                            username=new_username,
                            password=new_password,
                            full_name=new_full_name,
                            email=new_email,
                            role=role_str,
                            phone=new_phone,
                            address=new_address
                        )
                        if reg_ok:
                            st.session_state["just_registered_user"] = reg_res
                            st.success(f"🎉 Account '{new_username}' ({role_str.upper()}) was successfully created and stored in the MySQL database!")
                        else:
                            st.error(f"❌ {reg_res}")

            # Quick login shortcut right after registering
            if "just_registered_user" in st.session_state and st.session_state["just_registered_user"]:
                just_u = st.session_state["just_registered_user"]
                st.info(f"✨ Ready to access as **{just_u['full_name']}** (@{just_u['username']})?")
                if st.button(f"🚀 Sign In Now as @{just_u['username']}", type="primary", use_container_width=True, key="btn_quick_log_main"):
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = just_u
                    st.session_state["just_registered_user"] = None
                    st.rerun()

        # TAB 3: PASSWORD RESET
        with tab_reset:
            st.markdown("##### 🔑 Reset or Update Account Password")
            st.caption("If your username already exists in the database but you cannot sign in, enter your username and set a new password here:")
            with st.form("main_reset_pwd_form"):
                rst_username = st.text_input("Your Username *", placeholder="Enter your registered username (e.g. abc, admin)")
                rst_pwd1 = st.text_input("New Password *", type="password", placeholder="Minimum 4 characters")
                rst_pwd2 = st.text_input("Confirm New Password *", type="password", placeholder="Re-type new password")
                btn_rst = st.form_submit_button("Update Password in Database", type="primary", use_container_width=True)

                if btn_rst:
                    if rst_pwd1 != rst_pwd2:
                        st.error("❌ New passwords do not match. Please re-enter carefully.")
                    else:
                        r_ok, r_msg = reset_user_password(rst_username, rst_pwd1)
                        if r_ok:
                            st.success(f"✅ {r_msg}")
                        else:
                            st.error(f"❌ {r_msg}")

        # TAB 4: DEMO CREDENTIALS
        with tab_demo:
            st.markdown("##### Instant 1-Click Login for Evaluation")
            st.caption("Click any profile below to instantly log in with pre-seeded demo accounts:")

            demo_accounts = get_demo_accounts()
            for acc in demo_accounts:
                c1, c2 = st.columns([3, 1])
                if acc["role"] == "Admin":
                    badge_color = "#7c3aed"
                elif acc["role"] == "Librarian":
                    badge_color = "#4f46e5"
                else:
                    badge_color = "#10b981"
                with c1:
                    st.markdown(
                        f"""
                        <div style="padding: 6px 10px; background: #f8fafc; border-left: 4px solid {badge_color}; border-radius: 4px; margin-bottom: 6px; color: #1e293b;">
                            <strong style="color: #0f172a;">{acc['username']}</strong> 
                            <span style="background: {badge_color}20; color: {badge_color}; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 600;">{acc['role']}</span>
                            <br><small style="color: #64748b;">Pwd: <code style="color: #0f172a; background: #e2e8f0;">{acc['password']}</code> — {acc['desc']}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with c2:
                    if st.button("Log In", key=f"demo_{acc['username']}", use_container_width=True):
                        s, res = verify_user(acc["username"], acc["password"])
                        if s:
                            st.session_state["logged_in"] = True
                            st.session_state["user"] = res
                            st.toast(f"Logged in as {acc['role']} ({acc['username']})", icon="🚀")
                            st.rerun()


def render_admin_login_page():
    """Dedicated login and registration view for the Admin Portal page."""
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 25px;">
            <div style="display: inline-block; background: linear-gradient(135deg, #1e1b4b, #312e81); padding: 18px 22px; border-radius: 20px; box-shadow: 0 10px 25px rgba(30, 27, 75, 0.3);">
                <span style="font-size: 38px;">🛡️</span>
            </div>
            <h1 style="margin-top: 15px; margin-bottom: 5px; font-weight: 800; font-size: 2.2rem; background: linear-gradient(135deg, #312e81, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Administrator & Staff Gateway
            </h1>
            <p style="color: #64748b; font-size: 1.05rem; max-width: 600px; margin: 0 auto;">
                Restricted portal for catalog management, book addition, borrower tracking, and library circulation oversight.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c_left, c_center, c_right = st.columns([1, 2, 1])
    with c_center:
        tab_admin_login, tab_admin_reg, tab_admin_reset, tab_admin_demo = st.tabs([
            "🔐 Admin Sign In",
            "📝 Register New Admin / Staff",
            "🔑 Reset Password",
            "⚡ 1-Click Admin Access"
        ])

        # TAB 1: ADMIN SIGN IN
        with tab_admin_login:
            st.markdown("##### Administrative Credentials")
            with st.form("admin_dedicated_login_form"):
                admin_username = st.text_input("Administrator Username", placeholder="e.g. admin or librarian", key="adm_u_input")
                admin_password = st.text_input("Password", type="password", placeholder="Enter admin password", key="adm_p_input")
                btn_adm_sub = st.form_submit_button("Sign In to Admin Dashboard", type="primary", use_container_width=True)

                if btn_adm_sub:
                    ok, res = verify_user(admin_username, admin_password)
                    if ok:
                        if res["role"] not in ["admin", "librarian"]:
                            st.warning(f"⚠️ Account '@{res['username']}' is registered as a **Student Member**, not an Administrator.")
                            st.info("You can either switch to the Student Portal, or create a dedicated Administrator account on the 'Register New Admin' tab.")
                            if st.button("🎓 Open User / Student Portal Instead", key="adm_err_switch_usr", use_container_width=True):
                                st.switch_page("pages/2_User_Portal.py")
                        else:
                            st.session_state["logged_in"] = True
                            st.session_state["user"] = res
                            st.toast(f"Admin Access Granted: Welcome {res['full_name']}!", icon="🛡️")
                            st.rerun()
                    else:
                        st.error(f"❌ {res}")

        # TAB 2: REGISTER NEW ADMIN / STAFF
        with tab_admin_reg:
            st.markdown("##### 📝 Register New Administrator / Staff")
            st.caption("Create a new Administrative account with full catalog, borrower oversight, and circulation management privileges.")
            
            with st.form("admin_new_staff_reg_form", clear_on_submit=False):
                adm_role = st.selectbox(
                    "Administrative Role *",
                    options=["System Administrator (Full Control)", "Chief Librarian (Circulation & Catalog)"],
                    index=0
                )
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    adm_name = st.text_input("Staff Full Name *", placeholder="e.g. Dr. Rajesh Verma")
                    adm_user = st.text_input("Admin Username *", placeholder="e.g. admin_rajesh")
                with col_a2:
                    adm_email = st.text_input("Official Email *", placeholder="rajesh@college.edu")
                    adm_phone = st.text_input("Phone Number", placeholder="e.g. 9876543210")

                col_a3, col_a4 = st.columns(2)
                with col_a3:
                    adm_pwd1 = st.text_input("Password *", type="password", placeholder="Minimum 4 characters")
                with col_a4:
                    adm_pwd2 = st.text_input("Confirm Password *", type="password", placeholder="Re-type password")

                adm_btn_reg = st.form_submit_button("Create Admin Account in Database", type="primary", use_container_width=True)

                if adm_btn_reg:
                    if adm_pwd1 != adm_pwd2:
                        st.error("❌ Passwords do not match. Please verify your password entry.")
                    else:
                        chosen_role = "librarian" if "Librarian" in adm_role else "admin"
                        ok_reg, res_reg = register_admin(
                            username=adm_user,
                            password=adm_pwd1,
                            full_name=adm_name,
                            email=adm_email,
                            role=chosen_role,
                            phone=adm_phone
                        )
                        if ok_reg:
                            st.session_state["just_registered_admin"] = res_reg
                            st.success(f"🎉 Administrator account '@{adm_user}' ({chosen_role.upper()}) was saved in the MySQL database!")
                        else:
                            st.error(f"❌ {res_reg}")

            if "just_registered_admin" in st.session_state and st.session_state["just_registered_admin"]:
                j_adm = st.session_state["just_registered_admin"]
                st.info(f"✨ Ready to enter dashboard as **{j_adm['full_name']}** (@{j_adm['username']})?")
                if st.button(f"🚀 Sign In Immediately as @{j_adm['username']}", type="primary", use_container_width=True, key="btn_quick_log_adm"):
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = j_adm
                    st.session_state["just_registered_admin"] = None
                    st.rerun()

        # TAB 3: RESET ADMIN PASSWORD
        with tab_admin_reset:
            st.markdown("##### 🔑 Reset Administrator Password")
            st.caption("Update password for an existing Administrator or Librarian username:")
            with st.form("admin_reset_pwd_form"):
                a_rst_uname = st.text_input("Admin Username *", placeholder="e.g. admin or librarian", key="adm_rst_u")
                a_rst_pwd1 = st.text_input("New Password *", type="password", placeholder="Enter new password", key="adm_rst_p1")
                a_rst_pwd2 = st.text_input("Confirm New Password *", type="password", placeholder="Re-type new password", key="adm_rst_p2")
                btn_a_rst = st.form_submit_button("Update Admin Password", type="primary", use_container_width=True)

                if btn_a_rst:
                    if a_rst_pwd1 != a_rst_pwd2:
                        st.error("❌ Passwords do not match.")
                    else:
                        a_ok, a_msg = reset_user_password(a_rst_uname, a_rst_pwd1)
                        if a_ok:
                            st.success(f"✅ {a_msg}")
                        else:
                            st.error(f"❌ {a_msg}")

        # TAB 4: DEMO ACCESS
        with tab_admin_demo:
            st.markdown("##### Instant 1-Click Administrator Testing")
            admin_demos = [d for d in get_demo_accounts() if d["role"] in ["Admin", "Librarian"]]
            for ad in admin_demos:
                col_d1, col_d2 = st.columns([3, 1])
                with col_d1:
                    st.markdown(
                        f"""
                        <div style="padding: 8px 12px; background: #f8fafc; border-left: 4px solid #6366f1; border-radius: 4px; margin-bottom: 8px; color: #1e293b;">
                            <strong style="color: #0f172a;">{ad['username']}</strong> <span style="background: #e0e7ff; color: #4338ca; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 600;">{ad['role']}</span>
                            <br><small style="color: #64748b;">Pwd: <code style="color: #0f172a; background: #e2e8f0;">{ad['password']}</code> — {ad['desc']}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col_d2:
                    if st.button("Log In", key=f"btn_adm_demo_{ad['username']}", use_container_width=True):
                        s, res = verify_user(ad["username"], ad["password"])
                        if s:
                            st.session_state["logged_in"] = True
                            st.session_state["user"] = res
                            st.toast(f"Logged in as {res['role'].upper()}", icon="🚀")
                            st.rerun()


def render_user_login_page():
    """Dedicated login and registration view for the User/Student Portal page."""
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 25px;">
            <div style="display: inline-block; background: linear-gradient(135deg, #064e3b, #059669); padding: 18px 22px; border-radius: 20px; box-shadow: 0 10px 25px rgba(5, 150, 105, 0.3);">
                <span style="font-size: 38px;">🎓</span>
            </div>
            <h1 style="margin-top: 15px; margin-bottom: 5px; font-weight: 800; font-size: 2.2rem; background: linear-gradient(135deg, #059669, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Student & Member Library Portal
            </h1>
            <p style="color: #64748b; font-size: 1.05rem; max-width: 600px; margin: 0 auto;">
                Borrow physical books, access over 70,000+ digital e-books, stream academic texts, and save personal study notes.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c_left, c_center, c_right = st.columns([1, 2, 1])
    with c_center:
        tab_u_login, tab_u_reg, tab_u_reset, tab_u_demo = st.tabs([
            "🔐 Student Sign In",
            "📝 Create Free Account",
            "🔑 Reset / Update Password",
            "⚡ 1-Click Student Login"
        ])

        # TAB 1: STUDENT SIGN IN
        with tab_u_login:
            st.markdown("##### Student Sign In")
            with st.form("student_dedicated_login_form"):
                stu_user = st.text_input("Username", placeholder="e.g. aarav, diya, priya, abc", key="stu_u_input")
                stu_pwd = st.text_input("Password", type="password", placeholder="Enter password", key="stu_p_input")
                btn_stu_sub = st.form_submit_button("Sign In to Student Portal", type="primary", use_container_width=True)

                if btn_stu_sub:
                    ok, res = verify_user(stu_user, stu_pwd)
                    if ok:
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = res
                        st.toast(f"Welcome back, {res['full_name']}! 👋", icon="🎓")
                        st.rerun()
                    else:
                        st.error(f"❌ {res}")

        # TAB 2: CREATE STUDENT ACCOUNT
        with tab_u_reg:
            st.markdown("##### Register New Student Library Account")
            st.caption("Instant registration with immediate physical book borrowing and E-Books study access.")
            with st.form("student_dedicated_register_form", clear_on_submit=False):
                r1, r2 = st.columns(2)
                with r1:
                    reg_fname = st.text_input("Full Name *", placeholder="e.g. Rahul Gupta", key="u_reg_fn")
                    reg_uname = st.text_input("Desired Username *", placeholder="e.g. rahul24", key="u_reg_un")
                with r2:
                    reg_email = st.text_input("College Email *", placeholder="rahul@college.edu", key="u_reg_em")
                    reg_phone = st.text_input("Phone Number", placeholder="e.g. 9876543210", key="u_reg_ph")

                r3, r4 = st.columns(2)
                with r3:
                    reg_pwd = st.text_input("Password *", type="password", placeholder="Minimum 4 characters", key="u_reg_p1")
                with r4:
                    reg_pwd2 = st.text_input("Confirm Password *", type="password", placeholder="Re-type password", key="u_reg_p2")

                reg_dept = st.text_input("Department / Year", placeholder="e.g. Computer Science - Year 2", key="u_reg_dp")

                sub_reg = st.form_submit_button("Register & Save to Database", type="primary", use_container_width=True)
                if sub_reg:
                    if reg_pwd != reg_pwd2:
                        st.error("❌ Passwords do not match. Please verify your entry.")
                    else:
                        reg_ok, reg_res = register_student(
                            username=reg_uname,
                            password=reg_pwd,
                            full_name=reg_fname,
                            email=reg_email,
                            phone=reg_phone,
                            address=reg_dept
                        )
                        if reg_ok:
                            st.session_state["just_registered_student"] = reg_res
                            st.success(f"🎉 Account '{reg_uname}' created successfully in MySQL database for {reg_fname}!")
                        else:
                            st.error(f"❌ {reg_res}")

            if "just_registered_student" in st.session_state and st.session_state["just_registered_student"]:
                j_stu = st.session_state["just_registered_student"]
                st.info(f"✨ Ready to enter student portal as **{j_stu['full_name']}** (@{j_stu['username']})?")
                if st.button(f"🚀 Sign In Immediately as @{j_stu['username']}", type="primary", use_container_width=True, key="btn_quick_log_stu"):
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = j_stu
                    st.session_state["just_registered_student"] = None
                    st.rerun()

        # TAB 3: RESET STUDENT PASSWORD
        with tab_u_reset:
            st.markdown("##### 🔑 Reset Student Password")
            st.caption("Update password for an existing student username:")
            with st.form("student_reset_pwd_form"):
                s_rst_uname = st.text_input("Username *", placeholder="e.g. aarav, diya, abc", key="stu_rst_u")
                s_rst_pwd1 = st.text_input("New Password *", type="password", placeholder="Enter new password", key="stu_rst_p1")
                s_rst_pwd2 = st.text_input("Confirm New Password *", type="password", placeholder="Re-type new password", key="stu_rst_p2")
                btn_s_rst = st.form_submit_button("Update Password in Database", type="primary", use_container_width=True)

                if btn_s_rst:
                    if s_rst_pwd1 != s_rst_pwd2:
                        st.error("❌ Passwords do not match.")
                    else:
                        s_ok, s_msg = reset_user_password(s_rst_uname, s_rst_pwd1)
                        if s_ok:
                            st.success(f"✅ {s_msg}")
                        else:
                            st.error(f"❌ {s_msg}")

        # TAB 4: DEMO ACCESS
        with tab_u_demo:
            st.markdown("##### Instant 1-Click Student Evaluation")
            student_demos = [d for d in get_demo_accounts() if d["role"] == "Student"]
            for sd in student_demos:
                col_d1, col_d2 = st.columns([3, 1])
                with col_d1:
                    st.markdown(
                        f"""
                        <div style="padding: 8px 12px; background: #f8fafc; border-left: 4px solid #10b981; border-radius: 4px; margin-bottom: 8px; color: #1e293b;">
                            <strong style="color: #0f172a;">{sd['username']}</strong> <span style="background: #d1fae5; color: #065f46; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 600;">{sd['role']}</span>
                            <br><small style="color: #64748b;">Pwd: <code style="color: #0f172a; background: #e2e8f0;">{sd['password']}</code> — {sd['desc']}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col_d2:
                    if st.button("Log In", key=f"btn_stu_demo_{sd['username']}", use_container_width=True):
                        s, res = verify_user(sd["username"], sd["password"])
                        if s:
                            st.session_state["logged_in"] = True
                            st.session_state["user"] = res
                            st.toast(f"Logged in as Student ({res['username']})", icon="🎓")
                            st.rerun()
