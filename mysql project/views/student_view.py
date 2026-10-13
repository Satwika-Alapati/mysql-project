"""
Student Self-Service Portal.
Provides student dashboard, active loan tracking, smart catalog search,
one-click book borrowing / checkout, book reservations, return actions,
borrowing history, and digital library card.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
from database import execute_query, execute_non_query, call_procedure, add_book_to_catalog
from email_service import send_issue_confirmation, send_return_receipt
from ebooks_api import (
    search_all_ebooks,
    fetch_remote_text,
    save_study_note,
    get_study_notes,
    delete_study_note,
    get_db_ebooks,
    add_ebook_to_db,
    increment_ebook_stat,
    delete_ebook_from_db,
    search_openlibrary_api,
    CURATED_EBOOKS
)


def render_student_portal(user_info):
    member_id = user_info.get("member_id")
    if not member_id:
        st.error("Error: No linked library membership found for this user.")
        return

    # Fetch latest member profile from DB
    member = execute_query(
        "SELECT * FROM members WHERE member_id = %s",
        (member_id,),
        fetchone=True
    )

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; margin-bottom: 20px; color: #166534;">
            <div>
                <h3 style="margin: 0; font-size: 1.4rem; color: #166534;">🎓 Student Portal — Welcome, {member.get('full_name')}</h3>
                <small style="color: #15803d;">Member ID: <strong>#{member.get('member_id')}</strong> | Status: <strong>{member.get('status')}</strong></small>
            </div>
            <div>
                <span style="background: #dcfce7; color: #15803d; padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;">
                    📚 Student Member
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tabs = st.tabs([
        "🏠 My Dashboard",
        "👥 Who Took The Books",
        "➕ Add Books & E-Books",
        "📱 E-Books Library & Reader",
        "📖 Search & Borrow Books",
        "📜 My Borrowing History",
        "📌 My Reservations",
        "🪪 Digital Library Card"
    ])

    # =========================================================================
    # TAB 1: MY DASHBOARD
    # =========================================================================
    with tabs[0]:
        st.subheader("My Library Status")

        # Metrics for student
        active_loans_cnt = execute_query(
            "SELECT fn_member_active_loans(%s) AS c", (member_id,), fetchone=True
        )["c"]
        unpaid_fines_val = execute_query(
            "SELECT fn_member_unpaid_fines(%s) AS f", (member_id,), fetchone=True
        )["f"]
        pending_res_cnt = execute_query(
            "SELECT COUNT(*) AS c FROM reservations WHERE member_id = %s AND status IN ('Pending', 'Ready')",
            (member_id,), fetchone=True
        )["c"]

        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("📚 Books Currently in Possession", active_loans_cnt)
        sc2.metric("📌 Active Reservations", pending_res_cnt)
        sc3.metric("💰 Unpaid Fines Balance", f"${float(unpaid_fines_val):.2f}",
                   delta="No Outstanding Dues" if float(unpaid_fines_val) == 0 else f"${float(unpaid_fines_val):.2f} Due",
                   delta_color="normal" if float(unpaid_fines_val) == 0 else "inverse")

        st.divider()

        # CURRENT ACTIVE BORROWS
        st.markdown("##### 📖 Books You Currently Have Checked Out")
        my_loans = execute_query("""
            SELECT 
                i.issue_id,
                b.title,
                c.barcode,
                c.shelf_location,
                i.issue_date,
                i.due_date,
                DATEDIFF(i.due_date, CURDATE()) AS days_left,
                DATEDIFF(CURDATE(), i.due_date) AS days_overdue,
                fn_calc_fine(i.due_date, CURDATE()) AS accrued_fine
            FROM issues i
            JOIN book_copies c ON c.copy_id = i.copy_id
            JOIN books b ON b.book_id = c.book_id
            WHERE i.member_id = %s AND i.return_date IS NULL
            ORDER BY i.due_date ASC
        """, (member_id,))

        if my_loans:
            overdue_loans = [l for l in my_loans if l["days_left"] < 0]
            if overdue_loans:
                total_od_fine = sum(float(l["accrued_fine"] or 0.0) for l in overdue_loans)
                st.markdown(
                    f"""
                    <div style="padding: 16px 20px; background: #fef2f2; border: 2px solid #ef4444; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.1); color: #7f1d1d;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 24px;">🚨</span>
                            <h4 style="margin: 0; color: #b91c1c; font-size: 1.15rem;">URGENT OVERDUE REMINDER: Return Books & Settle Fines</h4>
                        </div>
                        <p style="margin: 8px 0 0 0; color: #7f1d1d; font-size: 0.95rem; line-height: 1.5;">
                            You currently have <strong style="color: #991b1b;">{len(overdue_loans)}</strong> book(s) past the due date with a total accrued fine of 
                            <span style="background: #fee2e2; color: #991b1b; padding: 2px 8px; border-radius: 4px; font-weight: 800; font-size: 1.05rem;">${total_od_fine:.2f}</span>.
                            Fines accumulate daily at <strong style="color: #991b1b;">$5.00/day</strong> for each delayed day. Please return your books below immediately to stop further penalties.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            for loan in my_loans:
                is_late = loan["days_left"] < 0
                box_bg = "#fef2f2" if is_late else "#f8fafc"
                border_c = "#ef4444" if is_late else "#cbd5e1"
                status_text = f"⚠️ OVERDUE by {loan['days_overdue']} days — Fine: ${float(loan['accrued_fine']):.2f}" if is_late else f"✅ Due in {loan['days_left']} days ({loan['due_date']})"

                with st.container():
                    st.markdown(
                        f"""
                        <div style="padding: 14px 18px; background: {box_bg}; border-left: 5px solid {border_c}; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); color: #1e293b;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h4 style="margin: 0; color: #1e293b;">{loan['title']}</h4>
                                <span style="font-weight: 700; font-size: 0.9rem; color: {'#dc2626' if is_late else '#16a34a'};">{status_text}</span>
                            </div>
                            <p style="margin: 6px 0 0 0; color: #475569; font-size: 0.9rem;">
                                Barcode: <code style="color: #0f172a; background: #e2e8f0;">{loan['barcode']}</code> | Shelf: <strong style="color: #1e293b;">{loan['shelf_location'] or 'General'}</strong> | Borrowed: {loan['issue_date']} | Due Date: <strong style="color: #1e293b;">{loan['due_date']}</strong>
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    c_btn1, c_btn2 = st.columns([4, 1])
                    with c_btn2:
                        if st.button("📥 Return This Book", key=f"ret_loan_{loan['issue_id']}", use_container_width=True, type="secondary"):
                            ok, ret_msg = call_procedure("sp_return_book", (loan["issue_id"], "Good"))
                            if ok:
                                fine_calc = float(loan["accrued_fine"]) if is_late else 0.0
                                send_return_receipt(
                                    member_id,
                                    member["full_name"],
                                    member["email"],
                                    loan["title"],
                                    loan["barcode"],
                                    fine_calc,
                                    "Good"
                                )
                                st.success(f"🎉 '{loan['title']}' returned successfully! Thank you.")
                                st.rerun()
                            else:
                                st.error(f"Error returning book: {ret_msg}")
        else:
            st.info("You do not have any borrowed books right now. Browse the catalog to select and borrow your next read!")

        # OUTSTANDING FINES NOTICE
        if float(unpaid_fines_val) > 0:
            st.markdown("##### ⚠️ Unpaid Fines Ledger")
            my_fines = execute_query("""
                SELECT f.fine_id, b.title, f.amount, f.reason, f.days_overdue, f.created_at
                FROM fines f
                JOIN issues i ON i.issue_id = f.issue_id
                JOIN book_copies c ON c.copy_id = i.copy_id
                JOIN books b ON b.book_id = c.book_id
                WHERE f.member_id = %s AND f.status = 'Unpaid'
            """, (member_id,))
            if my_fines:
                st.dataframe(pd.DataFrame(my_fines), use_container_width=True)
                st.caption("Please visit the library circulation desk to settle your outstanding fines.")

        # NOTIFICATION & OVERDUE REMINDER HISTORY
        with st.expander("📬 View My Overdue Notices & Reminders History"):
            my_notifs = execute_query("""
                SELECT type, subject, message, created_at, status
                FROM notifications
                WHERE member_id = %s
                ORDER BY notification_id DESC
                LIMIT 20
            """, (member_id,))
            if my_notifs:
                for n in my_notifs:
                    n_badge = "#dc2626" if "Overdue" in n["type"] else "#4f46e5"
                    st.markdown(
                        f"""
                        <div style="padding: 10px 14px; background: #f8fafc; border-left: 4px solid {n_badge}; border-radius: 6px; margin-bottom: 8px; color: #1e293b;">
                            <div style="display: flex; justify-content: space-between;">
                                <strong style="color: #0f172a;">{n['subject']}</strong>
                                <small style="color: #64748b;">{n['created_at']}</small>
                            </div>
                            <p style="margin: 4px 0 0 0; color: #334155; font-size: 0.88rem; white-space: pre-line;">{n['message']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No notices on file.")

    # =========================================================================
    # TAB 2: WHO TOOK THE BOOKS (BORROWER TRANSPARENCY)
    # =========================================================================
    with tabs[1]:
        st.subheader("👥 Live Borrower Tracker & Circulation Records ('Who Took The Books')")
        st.caption("Complete library transparency: see which books are currently checked out, who is reading them, issue dates, and when they are due back.")

        # KPI Summary Metrics Row
        try:
            tot_out = execute_query("SELECT COUNT(*) AS c FROM issues WHERE return_date IS NULL", fetchone=True)["c"]
            tot_borrowers = execute_query("SELECT COUNT(DISTINCT member_id) AS c FROM issues WHERE return_date IS NULL", fetchone=True)["c"]
            tot_od = execute_query("SELECT COUNT(*) AS c FROM issues WHERE return_date IS NULL AND due_date < CURDATE()", fetchone=True)["c"]
            tot_avail = execute_query("SELECT COUNT(*) AS c FROM book_copies WHERE status = 'Available'", fetchone=True)["c"]
        except Exception:
            tot_out, tot_borrowers, tot_od, tot_avail = 0, 0, 0, 0

        bk1, bk2, bk3, bk4 = st.columns(4)
        bk1.metric("📤 Books Currently Checked Out", tot_out)
        bk2.metric("👥 Active Student Readers", tot_borrowers)
        bk3.metric("🚨 Overdue Items", tot_od, delta=-tot_od if tot_od > 0 else 0, delta_color="inverse")
        bk4.metric("🟢 Copies Available in Library", tot_avail)

        st.write("")

        # Filters
        c_f1, c_f2, c_f3 = st.columns([2.5, 1.5, 1])
        with c_f1:
            circ_search = st.text_input(
                "🔍 Search Borrowers (Title, Student Name, Username, or Barcode):",
                placeholder="e.g. 1984, Sapiens, Aarav, Diya, BC-0001-1...",
                key="user_circ_search"
            )
        with c_f2:
            circ_status_filter = st.selectbox(
                "Filter Circulation Status:",
                ["🔴 Currently Borrowed (Active)", "🚨 Overdue Borrowers Only", "🟢 Returned History", "📋 All Records"],
                key="user_circ_filter"
            )
        with c_f3:
            st.write("")
            st.write("")
            if st.button("🔄 Refresh", use_container_width=True, key="user_circ_refresh"):
                st.rerun()

        # Query records
        base_sql = """
            SELECT 
                i.issue_id,
                m.member_id,
                m.full_name AS borrower_name,
                COALESCE(u.username, 'student') AS student_username,
                m.email AS borrower_email,
                COALESCE(m.address, 'Campus') AS borrower_dept,
                b.book_id,
                b.title AS book_title,
                b.isbn,
                c.barcode,
                c.shelf_location,
                i.issue_date,
                i.due_date,
                i.return_date,
                CASE 
                    WHEN i.return_date IS NOT NULL THEN 'Returned'
                    WHEN i.due_date < CURDATE() THEN 'Overdue'
                    ELSE 'Active Loan'
                END AS loan_status,
                CASE 
                    WHEN i.return_date IS NOT NULL THEN DATEDIFF(i.return_date, i.issue_date)
                    ELSE DATEDIFF(CURDATE(), i.issue_date)
                END AS days_held,
                DATEDIFF(i.due_date, CURDATE()) AS days_left,
                CASE 
                    WHEN i.return_date IS NULL AND i.due_date < CURDATE() THEN DATEDIFF(CURDATE(), i.due_date)
                    ELSE 0
                END AS days_overdue,
                fn_calc_fine(i.due_date, COALESCE(i.return_date, CURDATE())) AS fine_amount
            FROM issues i
            JOIN members m ON m.member_id = i.member_id
            LEFT JOIN users u ON u.member_id = m.member_id
            JOIN book_copies c ON c.copy_id = i.copy_id
            JOIN books b ON b.book_id = c.book_id
            WHERE 1=1
        """
        params = []
        if circ_status_filter == "🔴 Currently Borrowed (Active)":
            base_sql += " AND i.return_date IS NULL"
        elif circ_status_filter == "🚨 Overdue Borrowers Only":
            base_sql += " AND i.return_date IS NULL AND i.due_date < CURDATE()"
        elif circ_status_filter == "🟢 Returned History":
            base_sql += " AND i.return_date IS NOT NULL"

        if circ_search.strip():
            sq = f"%{circ_search.strip()}%"
            base_sql += """ AND (
                m.full_name LIKE %s OR 
                m.email LIKE %s OR 
                u.username LIKE %s OR 
                b.title LIKE %s OR 
                c.barcode LIKE %s OR
                b.isbn LIKE %s
            )"""
            params.extend([sq, sq, sq, sq, sq, sq])

        base_sql += " ORDER BY CASE WHEN i.return_date IS NULL THEN 0 ELSE 1 END, i.due_date ASC"

        borrower_records = execute_query(base_sql, params)

        if not borrower_records:
            st.info("ℹ️ No borrowing records found matching your filter.")
        else:
            st.markdown(f"##### 📋 Showing {len(borrower_records)} Circulation Record(s):")

            for rec in borrower_records:
                is_returned = rec["return_date"] is not None
                is_od = rec["loan_status"] == "Overdue"
                is_my_loan = rec["member_id"] == member_id

                if is_returned:
                    status_color = "#10b981"
                    status_badge = f"<span style='background: #dcfce7; color: #15803d; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 0.82rem;'>✅ Returned on {rec['return_date']}</span>"
                elif is_od:
                    status_color = "#ef4444"
                    status_badge = f"<span style='background: #fee2e2; color: #b91c1c; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 0.82rem;'>🚨 Overdue by {rec['days_overdue']} days</span>"
                else:
                    status_color = "#3b82f6"
                    status_badge = f"<span style='background: #dbeafe; color: #1d4ed8; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 0.82rem;'>📖 Due in {rec['days_left']} days ({rec['due_date']})</span>"

                borrower_tag = f"<strong>{rec['borrower_name']}</strong> (@{rec['student_username']})"
                if is_my_loan:
                    borrower_tag += " <span style='background: #e0e7ff; color: #4338ca; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700;'>YOU</span>"

                with st.container():
                    st.markdown(
                        f"""
                        <div style="padding: 14px 18px; background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid {status_color}; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); color: #1e293b;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                                <div>
                                    <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">📖 {rec['book_title']}</div>
                                    <div style="font-size: 0.88rem; color: #334155; margin-top: 4px;">
                                        👤 <strong style="color: #0f172a;">Taken by:</strong> <strong style="color: #0f172a;">{rec['borrower_name']}</strong> (@{rec['student_username']}) &bull; Member ID: #{rec['member_id']} &bull; Email: {rec['borrower_email']}
                                    </div>
                                    <div style="font-size: 0.8rem; color: #64748b; margin-top: 4px;">
                                        🏷️ Barcode: <code style="color: #0f172a; background: #e2e8f0;">{rec['barcode']}</code> | 📍 Shelf: {rec['shelf_location'] or 'Stack'} | 📅 Borrowed: {rec['issue_date']} | Due: {rec['due_date']}
                                    </div>
                                </div>
                                <div style="text-align: right;">
                                    {status_badge}
                                    <div style="font-size: 0.78rem; color: #64748b; margin-top: 6px;">Held for {rec['days_held']} days</div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Quick Reserve Action if not returned and not the current student
                    if not is_returned and not is_my_loan:
                        r_c1, r_c2 = st.columns([4, 1.2])
                        with r_c2:
                            if st.button("📌 Reserve This Book", key=f"circ_res_btn_{rec['issue_id']}", use_container_width=True):
                                ok, res_msg = call_procedure("sp_reserve_book", (member_id, rec["book_id"]))
                                if ok:
                                    st.success(f"🎉 Reserved '{rec['book_title']}'! You will receive notice when returned.")
                                    st.rerun()
                                else:
                                    st.error(f"Cannot reserve: {res_msg}")

            with st.expander("📊 View Complete Tabular Data & Export CSV"):
                df_circ = pd.DataFrame(borrower_records)
                cols_show = ["issue_id", "book_title", "borrower_name", "student_username", "barcode", "shelf_location", "issue_date", "due_date", "loan_status", "days_held", "days_overdue"]
                st.dataframe(df_circ[cols_show], use_container_width=True)
                csv_circ = df_circ.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Export Borrowers Report (CSV)", data=csv_circ, file_name=f"library_borrowers_{date.today()}.csv", mime="text/csv")

    # =========================================================================
    # TAB 3: ADD BOOKS & E-BOOKS
    # =========================================================================
    with tabs[2]:
        st.subheader("➕ Add Books to Library (Catalog & E-Books)")
        st.caption("Contribute and expand our library! Register physical printed books with physical copies, or publish digital e-books for online reading.")

        add_book_subtabs = st.tabs(["📖 Add Physical Book to Catalog", "🌐 Add Digital E-Book", "📚 Recently Added Titles"])

        # SUB-TAB 1: PHYSICAL BOOK
        with add_book_subtabs[0]:
            st.markdown("##### 📖 Add Physical Book to Catalog")
            st.caption("Register printed books into the library database. Shelf copies and barcodes are generated automatically.")

            p_mode = st.radio("Choose Input Method:", ["⚡ Smart 1-Click Open Library API Search", "✍️ Manual Form Entry"], horizontal=True, key="usr_add_phys_mode")

            if "user_autofill_title" not in st.session_state:
                st.session_state["user_autofill_title"] = ""
                st.session_state["user_autofill_isbn"] = ""
                st.session_state["user_autofill_year"] = 2024
                st.session_state["user_autofill_author"] = ""
                st.session_state["user_autofill_pub"] = ""

            if p_mode == "⚡ Smart 1-Click Open Library API Search":
                st.markdown(
                    """
                    <div style="padding: 12px 16px; background: #eef2ff; border-left: 4px solid #6366f1; border-radius: 8px; margin-bottom: 14px; color: #1e1b4b;">
                        <strong style="color: #312e81;">💡 Smart Auto-Fill:</strong> <span style="color: #3730a3;">Search millions of books on Open Library. Select any book to instantly populate title, author, publisher, ISBN, and publication year!</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                col_s_inp, col_s_btn = st.columns([3, 1])
                with col_s_inp:
                    ol_lookup_q = st.text_input("Search Open Library by Title, Topic, or ISBN:", placeholder="e.g. Clean Code, Python, Operating Systems...", key="user_ol_lookup_input")
                with col_s_btn:
                    st.write("")
                    st.write("")
                    do_ol_lookup = st.button("🔎 Search API", type="primary", use_container_width=True, key="btn_usr_ol_lookup")

                if ol_lookup_q:
                    ol_matches = search_openlibrary_api(ol_lookup_q, limit=4)
                    if ol_matches:
                        st.markdown("##### 📚 Select a Match to Autofill:")
                        for idx, item in enumerate(ol_matches):
                            with st.container():
                                m_c1, m_c2, m_c3 = st.columns([1, 4, 1.5])
                                with m_c1:
                                    if item.get("cover_url"):
                                        st.image(item["cover_url"], width=75)
                                    else:
                                        st.markdown("📖 *No Cover*")
                                with m_c2:
                                    st.markdown(f"**{item['title']}**")
                                    st.caption(f"Author(s): {item['authors']} | Publisher: {item['publisher']} | Year: {item['year']} | ISBN: `{item['isbn'] or 'N/A'}`")
                                with m_c3:
                                    if st.button("📥 Autofill Details", key=f"btn_usr_autofill_{idx}", use_container_width=True):
                                        st.session_state["user_autofill_title"] = item["title"]
                                        st.session_state["user_autofill_isbn"] = item["isbn"] or f"978-USR-{datetime.now().strftime('%H%M%S')}"
                                        st.session_state["user_autofill_year"] = int(item["year"]) if str(item["year"]).isdigit() else 2024
                                        st.session_state["user_autofill_author"] = item["authors"]
                                        st.session_state["user_autofill_pub"] = item["publisher"]
                                        st.success(f"Loaded '{item['title']}'! Review below and click Register.")

            # Physical Book Form
            existing_categories = execute_query("SELECT category_id, name FROM categories ORDER BY name ASC")
            existing_publishers = execute_query("SELECT publisher_id, name FROM publishers ORDER BY name ASC")
            existing_authors = execute_query("SELECT author_id, name FROM authors ORDER BY name ASC")

            with st.form("user_add_physical_book_form"):
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    bk_title = st.text_input("Book Title *", value=st.session_state.get("user_autofill_title", ""), placeholder="e.g. Design Patterns: Elements of Reusable Object-Oriented Software")
                    bk_isbn = st.text_input("ISBN (Unique Identifier) *", value=st.session_state.get("user_autofill_isbn", ""), placeholder="e.g. 978-0201633610")
                    bk_edition = st.text_input("Edition", value="1st")
                    bk_year = st.number_input("Publication Year", min_value=1800, max_value=2030, value=st.session_state.get("user_autofill_year", 2024))
                    bk_price = st.number_input("Unit Price ($)", min_value=0.0, value=45.0, step=5.0)

                with f_col2:
                    cat_names = [c["name"] for c in existing_categories]
                    sel_cat = st.selectbox("Category *", options=cat_names if cat_names else ["Computer Science"])
                    new_cat_txt = st.text_input("Or create New Category (leave blank if selected above):", "")

                    pub_names = [p["name"] for p in existing_publishers]
                    init_pub = st.session_state.get("user_autofill_pub", "")
                    sel_pub = st.selectbox("Publisher *", options=pub_names if pub_names else ["Pearson"])
                    new_pub_txt = st.text_input("Or create New Publisher (leave blank if selected above):", value=init_pub if init_pub and init_pub not in pub_names else "")

                    auth_names = [a["name"] for a in existing_authors]
                    init_auth = st.session_state.get("user_autofill_author", "")
                    sel_authors = st.multiselect("Select Authors *", options=auth_names)
                    new_auth_txt = st.text_input("Or add New Author (leave blank if selected above):", value=init_auth if init_auth and init_auth not in auth_names else "")

                    bk_lang = st.text_input("Language", value="English")

                st.markdown("##### 🏷️ Physical Copies & Shelf Placement")
                cp_c1, cp_c2 = st.columns(2)
                with cp_c1:
                    bk_num_copies = st.number_input("Number of Physical Copies to Add to Shelves *", min_value=1, max_value=20, value=3)
                with cp_c2:
                    bk_shelf = st.text_input("Shelf Location Code", value="Stack B - Shelf 104")

                submit_add_bk = st.form_submit_button("🚀 Register Book in Library Catalog", type="primary", use_container_width=True)

                if submit_add_bk:
                    final_cat = new_cat_txt.strip() if new_cat_txt.strip() else sel_cat
                    final_pub = new_pub_txt.strip() if new_pub_txt.strip() else sel_pub
                    final_authors = list(sel_authors)
                    if new_auth_txt.strip():
                        final_authors.append(new_auth_txt.strip())

                    ok, b_id, msg = add_book_to_catalog(
                        title=bk_title,
                        isbn=bk_isbn,
                        category_name=final_cat,
                        publisher_name=final_pub,
                        author_names=final_authors,
                        publication_year=bk_year,
                        edition=bk_edition,
                        language=bk_lang,
                        price=bk_price,
                        num_copies=bk_num_copies,
                        shelf_location=bk_shelf
                    )
                    if ok:
                        st.success(f"🎉 {msg}")
                        st.toast("Book registered in library catalog!", icon="📚")
                        st.session_state["user_autofill_title"] = ""
                        st.session_state["user_autofill_isbn"] = ""
                        st.session_state["user_autofill_author"] = ""
                        st.session_state["user_autofill_pub"] = ""
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

        # SUB-TAB 2: DIGITAL E-BOOK
        with add_book_subtabs[1]:
            st.markdown("##### 🌐 Add Digital E-Book to Library")
            st.caption("Publish digital textbooks, study materials, or open-access e-books for in-app reading and downloading.")

            with st.form("user_add_ebook_form"):
                eb_f1, eb_f2 = st.columns(2)
                with eb_f1:
                    eb_in_title = st.text_input("E-Book Title *", placeholder="e.g. Modern Operating Systems & Concurrency")
                    eb_in_author = st.text_input("Author(s) *", placeholder="e.g. Andrew S. Tanenbaum")
                    eb_in_cat = st.selectbox("Category / Discipline *", [
                        "Computer Science", "Artificial Intelligence", "Physics & Science",
                        "Philosophy", "Literature", "Mathematics", "Engineering", "Business & Economics"
                    ])
                    eb_in_year = st.text_input("Publication Year", value="2024")
                    eb_in_isbn = st.text_input("Digital Identifier / ISBN (Optional)", placeholder="e.g. 978-0133591620")

                with eb_f2:
                    eb_in_format = st.selectbox("Format", ["PDF / Online", "EPUB / Text", "HTML / Web", "Interactive Textbook"])
                    eb_in_size = st.text_input("File Size", value="4.5 MB")
                    eb_in_read = st.text_input("Read Online URL *", placeholder="https://openlibrary.org or reading URL")
                    eb_in_down = st.text_input("Direct Download URL (PDF / EPUB)", placeholder="https://.../book.pdf or https://.../book.epub")
                    eb_in_cover = st.text_input("Cover Image URL", placeholder="https://images.unsplash.com/... or leave blank for default")

                eb_in_desc = st.text_area("Overview & Summary", placeholder="Brief synopsis or abstract of the e-book...", height=100)
                eb_in_sample = st.text_area("Chapter 1 / Excerpt Content Preview (Markdown Supported)", placeholder="# Chapter 1: Introduction\n\nWrite chapter excerpt here for student preview...", height=150)

                submit_add_eb = st.form_submit_button("💾 Publish E-Book to Digital Library", type="primary", use_container_width=True)

                if submit_add_eb:
                    ok_eb, msg_eb = add_ebook_to_db(
                        title=eb_in_title,
                        author=eb_in_author,
                        category=eb_in_cat,
                        publication_year=eb_in_year,
                        isbn=eb_in_isbn,
                        cover_url=eb_in_cover,
                        read_url=eb_in_read,
                        download_url=eb_in_down,
                        format_type=eb_in_format,
                        file_size=eb_in_size,
                        description=eb_in_desc,
                        content_preview=eb_in_sample,
                        added_by=f"Student ({member['full_name']})"
                    )
                    if ok_eb:
                        st.success(f"🎉 {msg_eb}")
                        st.toast("E-Book added to Digital Library!", icon="📱")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg_eb}")

        # SUB-TAB 3: RECENTLY ADDED TITLES
        with add_book_subtabs[2]:
            st.markdown("##### 🌟 Recently Added Library Titles")
            recent_bks = execute_query("""
                SELECT b.book_id, b.title, b.isbn, c.name AS category, p.name AS publisher, b.publication_year,
                       (SELECT COUNT(*) FROM book_copies cp WHERE cp.book_id = b.book_id) AS total_copies,
                       (SELECT COUNT(*) FROM book_copies cp WHERE cp.book_id = b.book_id AND cp.status = 'Available') AS avail_copies
                FROM books b
                LEFT JOIN categories c ON c.category_id = b.category_id
                LEFT JOIN publishers p ON p.publisher_id = b.publisher_id
                ORDER BY b.book_id DESC LIMIT 8
            """)
            if recent_bks:
                df_recent = pd.DataFrame(recent_bks)
                st.dataframe(df_recent, use_container_width=True)

    # =========================================================================
    # TAB 4: E-BOOKS LIBRARY & READER
    # =========================================================================
    with tabs[3]:
        st.subheader("📱 E-Books Library & Digital Study Center")
        st.caption("Browse persistent e-books stored in MySQL and public academic repositories. Read online, take persistent notes, and download materials.")

        # Check if student is currently studying a book
        active_study_book = st.session_state.get("active_study_book", None)

        if active_study_book:
            # -------------------------------------------------------------
            # VIEW A: DEDICATED STUDY WORKSPACE
            # -------------------------------------------------------------
            w_top1, w_top2 = st.columns([1, 4])
            with w_top1:
                if st.button("⬅️ Back to E-Books Catalog", use_container_width=True):
                    st.session_state["active_study_book"] = None
                    st.rerun()

            st.markdown(
                f"""
                <div style="padding: 16px 20px; background: linear-gradient(135deg, #064e3b, #047857); border-radius: 12px; color: white; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                                📖 Digital Study Workspace
                            </span>
                            <h2 style="margin: 8px 0 4px 0; color: white; font-size: 1.4rem;">{active_study_book['title']}</h2>
                            <small style="color: #a7f3d0;">Author(s): <strong>{active_study_book['authors']}</strong> | Category: {active_study_book.get('subject', 'Academic')} | Format: {active_study_book.get('format', 'E-Book')}</small>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            study_col_left, study_col_right = st.columns([1.5, 1])

            # LEFT COLUMN: THE BOOK READER
            with study_col_left:
                st.markdown("##### 📖 Digital Reading & Material View")

                rc1, rc2 = st.columns(2)
                with rc1:
                    theme_choice = st.selectbox(
                        "Reading Theme:",
                        ["☀️ Daylight (Clean)", "🌙 Dark Mode", "📜 Warm Sepia (Paper)"],
                        key="reader_theme"
                    )
                with rc2:
                    font_size_choice = st.selectbox(
                        "Font Size:",
                        ["Normal (15px)", "Large (18px)", "Extra Large (21px)"],
                        key="reader_font_size"
                    )

                theme_styles = {
                    "☀️ Daylight (Clean)": "background: #ffffff; color: #1e293b; border: 1px solid #e2e8f0;",
                    "🌙 Dark Mode": "background: #0f172a; color: #e2e8f0; border: 1px solid #334155;",
                    "📜 Warm Sepia (Paper)": "background: #fef9c3; color: #713f12; border: 1px solid #fde047;"
                }
                font_sizes = {
                    "Normal (15px)": "15px",
                    "Large (18px)": "18px",
                    "Extra Large (21px)": "21px"
                }
                sel_style = theme_styles[theme_choice]
                sel_fsize = font_sizes[font_size_choice]

                ext_c1, ext_c2 = st.columns(2)
                with ext_c1:
                    if active_study_book.get("read_url"):
                        st.markdown(f"🔗 [**Open Full Online Reader ↗**]({active_study_book['read_url']})")
                with ext_c2:
                    if active_study_book.get("download_url") or active_study_book.get("epub_url"):
                        d_url = active_study_book.get("download_url") or active_study_book.get("epub_url")
                        st.markdown(f"📥 [**Download Free ({active_study_book.get('file_size', 'PDF')}) ↗**]({d_url})")

                content_to_display = ""
                if active_study_book.get("sample_content"):
                    content_to_display = active_study_book["sample_content"]
                elif active_study_book.get("txt_url"):
                    with st.spinner("Fetching full text excerpt..."):
                        content_to_display = fetch_remote_text(active_study_book["txt_url"])
                elif active_study_book.get("description"):
                    content_to_display = f"# {active_study_book['title']}\n\n**Author:** {active_study_book['authors']}\n\n**Overview:**\n\n{active_study_book['description']}\n\n*Click 'Open Full Online Reader' above to study complete online edition.*"
                else:
                    content_to_display = "Text preview loading... Click 'Open Full Online Reader' above for full interactive view."

                st.markdown(
                    f"""
                    <div style="{sel_style} font-size: {sel_fsize}; line-height: 1.7; padding: 22px; border-radius: 12px; max-height: 520px; overflow-y: auto; white-space: pre-wrap; font-family: 'Plus Jakarta Sans', Georgia, serif; box-shadow: inset 0 2px 4px rgba(0,0,0,0.04);">
{content_to_display}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # RIGHT COLUMN: STUDY TOOLKIT & SAVED NOTES
            with study_col_right:
                st.markdown("##### ⏱️ Focus & Study Session Timer")
                timer_c1, timer_c2 = st.columns([2, 1])
                with timer_c1:
                    st.info("💡 **Pomodoro Technique:** Focus on reading and taking notes for 25 minutes, then take a 5-minute break.")
                with timer_c2:
                    if st.button("⏱️ Start 25m Focus", use_container_width=True):
                        st.session_state["focus_timer_active"] = True
                        st.toast("25-minute study focus started! Stay focused and take notes.", icon="🎯")

                st.divider()

                st.markdown("##### 📝 My Personal Study Notes (Saved to MySQL)")
                st.caption("Your notes are saved directly to MySQL and persist permanently across logins.")

                existing_notes_list = get_study_notes(member_id)
                current_book_note = next((n for n in existing_notes_list if str(n["ebook_id"]) == str(active_study_book["id"])), None)
                init_note_content = current_book_note["notes"] if current_book_note else ""

                with st.form("student_ebook_notes_form"):
                    student_notes_text = st.text_area(
                        "Study Notes & Summaries:",
                        value=init_note_content,
                        height=200,
                        placeholder="Write your chapter takeaways, key definitions, or questions..."
                    )
                    save_notes_btn = st.form_submit_button("💾 Save Notes to Account", type="primary", use_container_width=True)

                    if save_notes_btn:
                        ok_n, msg_n = save_study_note(
                            member_id=member_id,
                            book_title=active_study_book["title"],
                            book_author=active_study_book["authors"],
                            ebook_id=str(active_study_book["id"]),
                            notes=student_notes_text
                        )
                        if ok_n:
                            st.success(f"✅ {msg_n}")
                            st.toast("Notes saved to your library account!", icon="💾")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg_n}")

                if current_book_note:
                    st.caption(f"Last updated: **{current_book_note['last_studied']}**")

                with st.expander("📚 View All My Saved Study Notes"):
                    if existing_notes_list:
                        for n in existing_notes_list:
                            st.markdown(f"**📖 {n['book_title']}** by {n['book_author']}")
                            st.code(n['notes'])
                            st.caption(f"Saved on {n['last_studied']}")
                            if st.button("🗑️ Delete Note", key=f"del_note_{n['note_id']}"):
                                delete_study_note(n['note_id'], member_id)
                                st.rerun()
                            st.write("---")
                    else:
                        st.info("No study notes saved yet. Start typing above!")

        else:
            # -------------------------------------------------------------
            # VIEW B: E-BOOKS DISCOVERY & SELECTION HUB
            # -------------------------------------------------------------
            st.markdown(
                """
                <div style="padding: 14px 18px; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 10px; margin-bottom: 16px; color: #064e3b;">
                    <strong style="color: #064e3b; font-weight: 700;">🌟 Interactive Digital Study:</strong> <span style="color: #065f46;">Select any e-book below to immediately open the reader, review chapters, stream full public domain texts, and record personalized study notes!</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Search & Filter Bar
            eb_s1, eb_s2, eb_s3 = st.columns([2.5, 1.5, 1])
            with eb_s1:
                eb_search_term = st.text_input(
                    "🔍 Search by Topic, Book Title, or Author:",
                    placeholder="e.g. Python, Algorithms, Artificial Intelligence, Einstein, Philosophy...",
                    key="student_eb_search_input"
                )
            with eb_s2:
                eb_category_filter = st.selectbox(
                    "Filter Discipline:",
                    ["All", "Computer Science", "Artificial Intelligence", "Physics & Science", "Philosophy", "Literature", "Mathematics"]
                )
            with eb_s3:
                st.write("")
                st.write("")
                do_eb_search = st.button("🔎 Search E-Books", type="primary", use_container_width=True)

            found_ebooks = search_all_ebooks(query=eb_search_term, category_filter=eb_category_filter)

            if not found_ebooks:
                st.info("No e-books found for that query. Try searching for 'Python', 'Algorithms', 'Science', or 'Literature'.")
            else:
                st.markdown(f"##### 📚 Available E-Books ({len(found_ebooks)} titles):")

                for i in range(0, len(found_ebooks), 2):
                    row_books = found_ebooks[i:i+2]
                    cols = st.columns(2)

                    for col, bk in zip(cols, row_books):
                        with col:
                            with st.container():
                                is_db = bk.get("is_db_stored", False)
                                badge_bg = "#ecfdf5" if is_db else "#e0e7ff"
                                badge_color = "#065f46" if is_db else "#4338ca"
                                badge_txt = "✨ Digital Library (MySQL)" if is_db else "🌐 Public Archive"

                                st.markdown(
                                    f"""
                                    <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; background: #ffffff; min-height: 220px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-bottom: 12px; color: #1e293b;">
                                        <div style="display: flex; gap: 14px;">
                                            <div style="flex-shrink: 0;">
                                                <img src="{bk.get('cover_url') or 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=200&q=80'}" style="width: 85px; height: 120px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);" />
                                            </div>
                                            <div style="flex-grow: 1;">
                                                <div style="display: flex; gap: 6px; margin-bottom: 4px;">
                                                    <span style="background: {badge_bg}; color: {badge_color}; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">{badge_txt}</span>
                                                    <span style="background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600;">{bk.get('subject', 'Academic')}</span>
                                                </div>
                                                <h4 style="margin: 4px 0 2px 0; font-size: 1.05rem; color: #1e293b;">{bk['title']}</h4>
                                                <div style="font-size: 0.85rem; color: #475569; font-weight: 500;">✍️ {bk['authors']}</div>
                                                <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">📅 {bk.get('year', 'N/A')} | 📦 {bk.get('format', 'PDF/EPUB')} ({bk.get('file_size', '3.5 MB')})</div>
                                                <p style="font-size: 0.8rem; color: #64748b; margin: 6px 0 0 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{bk.get('description', '')}</p>
                                            </div>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                                btn_c1, btn_c2 = st.columns([2, 1.2])
                                with btn_c1:
                                    if st.button("📖 Select & Study This E-Book", key=f"study_btn_{bk['id']}", type="primary", use_container_width=True):
                                        if bk.get("db_id"):
                                            increment_ebook_stat(bk["db_id"], "views")
                                        st.session_state["active_study_book"] = bk
                                        st.rerun()
                                with btn_c2:
                                    if bk.get("download_url") or bk.get("epub_url"):
                                        dl_link = bk.get("download_url") or bk.get("epub_url")
                                        st.link_button("📥 Download", dl_link, use_container_width=True)
                                    elif bk.get("read_url"):
                                        st.link_button("🌐 Reader", bk["read_url"], use_container_width=True)
                                    else:
                                        st.button("Available", disabled=True, use_container_width=True)

                                # Optional: If from external API, offer 1-click save to MySQL collection
                                if not is_db and bk.get("source") != "Digital Library (MySQL)":
                                    if st.button("💾 Save to Library Collection", key=f"save_col_{bk['id']}", use_container_width=True):
                                        ok_s, msg_s = add_ebook_to_db(
                                            title=bk["title"],
                                            author=bk["authors"],
                                            category=bk.get("subject", "General"),
                                            publication_year=str(bk.get("year", "2024")),
                                            isbn=bk.get("isbn", ""),
                                            cover_url=bk.get("cover_url", ""),
                                            read_url=bk.get("read_url", ""),
                                            download_url=bk.get("download_url", "") or bk.get("epub_url", ""),
                                            format_type="PDF / EPUB",
                                            file_size="3.5 MB",
                                            description=bk.get("description", ""),
                                            content_preview="",
                                            added_by=f"Student ({member['full_name']})"
                                        )
                                        if ok_s:
                                            st.success("Saved to Library Collection!")
                                            st.rerun()

                                st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)


    # =========================================================================
    # TAB 5: SEARCH & BORROW BOOKS
    # =========================================================================
    with tabs[4]:
        st.subheader("📖 Library Catalog — Browse, Borrow & Reserve")
        st.caption("Select and borrow available physical books directly, or place a smart reservation if all copies are checked out.")

        c_srch1, c_srch2 = st.columns([3, 1])
        with c_srch1:
            search_term = st.text_input("🔍 Search by Title, Author, Category, or ISBN:", "", key="stud_search")
        with c_srch2:
            cat_filter = st.selectbox("Filter Category:", ["All Categories"] + [c["name"] for c in execute_query("SELECT name FROM categories ORDER BY name")])

        # Fetch Catalog
        sql = """
            SELECT 
                b.book_id,
                b.isbn,
                b.title,
                GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') AS authors,
                p.name AS publisher,
                c.name AS category,
                b.publication_year,
                b.edition,
                b.price,
                COUNT(DISTINCT cp.copy_id) AS total_copies,
                SUM(CASE WHEN cp.status = 'Available' THEN 1 ELSE 0 END) AS available_copies
            FROM books b
            LEFT JOIN publishers p ON p.publisher_id = b.publisher_id
            LEFT JOIN categories c ON c.category_id = b.category_id
            LEFT JOIN book_authors ba ON ba.book_id = b.book_id
            LEFT JOIN authors a ON a.author_id = ba.author_id
            LEFT JOIN book_copies cp ON cp.book_id = b.book_id
            WHERE 1=1
        """
        params = []
        if search_term:
            sql += " AND (b.title LIKE %s OR b.isbn LIKE %s OR a.name LIKE %s)"
            st_like = f"%{search_term.strip()}%"
            params.extend([st_like, st_like, st_like])
        if cat_filter != "All Categories":
            sql += " AND c.name = %s"
            params.append(cat_filter)

        sql += " GROUP BY b.book_id ORDER BY b.title ASC"

        books_data = execute_query(sql, params)

        if not books_data:
            st.info("No books match your criteria.")
        else:
            for b in books_data:
                total_cp = int(b["total_copies"] or 0)
                avail_cp = int(b["available_copies"] or 0)
                is_available = avail_cp > 0

                # Check if this student currently has an active copy of this book
                already_borrowed = execute_query("""
                    SELECT i.issue_id, i.due_date, c.barcode, c.shelf_location
                    FROM issues i
                    JOIN book_copies c ON c.copy_id = i.copy_id
                    WHERE i.member_id = %s AND c.book_id = %s AND i.return_date IS NULL
                """, (member_id, b["book_id"]), fetchone=True)

                # Check if student already has a pending/ready reservation for this book
                already_reserved = execute_query("""
                    SELECT reservation_id, status, ready_until
                    FROM reservations
                    WHERE member_id = %s AND book_id = %s AND status IN ('Pending', 'Ready')
                """, (member_id, b["book_id"]), fetchone=True)

                # Available physical copies for this book
                copies_available = execute_query("""
                    SELECT copy_id, barcode, shelf_location, status
                    FROM book_copies
                    WHERE book_id = %s AND status = 'Available'
                    ORDER BY copy_id ASC
                """, (b["book_id"],))

                # Card styling
                if already_borrowed:
                    card_border = "#6366f1"
                    avail_badge = f"<span style='background: #e0e7ff; color: #4338ca; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85rem;'>📘 Currently in Your Possession (Due: {already_borrowed['due_date']})</span>"
                elif is_available:
                    card_border = "#10b981"
                    avail_badge = f"<span style='background: #dcfce7; color: #15803d; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85rem;'>✅ {avail_cp} of {total_cp} Copies Available</span>"
                else:
                    card_border = "#f59e0b"
                    avail_badge = f"<span style='background: #fef3c7; color: #b45309; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85rem;'>⏳ All {total_cp} Copies Checked Out (Reservable)</span>"

                with st.container():
                    st.markdown(
                        f"""
                        <div style="padding: 16px; background: white; border: 1px solid #e2e8f0; border-left: 5px solid {card_border}; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.04); color: #1e293b;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div>
                                    <h4 style="margin: 0; font-size: 1.18rem; color: #0f172a;">{b['title']}</h4>
                                    <p style="margin: 4px 0; color: #334155; font-size: 0.9rem;">
                                        <strong style="color: #0f172a;">Author(s):</strong> {b['authors'] or 'Unknown'} | 
                                        <strong style="color: #0f172a;">Category:</strong> {b['category']} | 
                                        <strong style="color: #0f172a;">Publisher:</strong> {b['publisher']} ({b['publication_year']})
                                    </p>
                                    <small style="color: #64748b;">ISBN: {b['isbn']} | Edition: {b['edition']} | Price: ${float(b['price']):.2f}</small>
                                </div>
                                <div>{avail_badge}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Action buttons and copy selector row
                    act_col1, act_col2 = st.columns([3, 2])

                    if already_borrowed:
                        with act_col1:
                            st.caption(f"You have copy barcode `{already_borrowed['barcode']}` checked out. Shelf: {already_borrowed['shelf_location'] or 'General'}")
                        with act_col2:
                            if st.button(f"📥 Return '{b['title']}'", key=f"ret_from_cat_{b['book_id']}", use_container_width=True, type="secondary"):
                                ok, ret_msg = call_procedure("sp_return_book", (already_borrowed["issue_id"], "Good"))
                                if ok:
                                    send_return_receipt(
                                        member_id,
                                        member["full_name"],
                                        member["email"],
                                        b["title"],
                                        already_borrowed["barcode"],
                                        0.0,
                                        "Good"
                                    )
                                    st.success(f"🎉 Book '{b['title']}' returned successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Return error: {ret_msg}")

                    elif is_available and copies_available:
                        with act_col1:
                            # If multiple copies exist, let student select shelf location or pick first
                            selected_copy = st.selectbox(
                                "Select Physical Copy to Borrow:",
                                options=copies_available,
                                format_func=lambda cp: f"Barcode: {cp['barcode']} (Shelf Location: {cp['shelf_location'] or 'General Desk'})",
                                key=f"sel_copy_{b['book_id']}"
                            )
                        with act_col2:
                            st.write("")
                            if st.button(f"📖 Borrow Book Now", key=f"borrow_{b['book_id']}", type="primary", use_container_width=True):
                                ok, res = call_procedure("sp_issue_book", (member_id, selected_copy["copy_id"]))
                                if ok:
                                    # Fetch issue details
                                    new_issue = execute_query("""
                                        SELECT issue_id, due_date FROM issues 
                                        WHERE copy_id = %s AND member_id = %s AND return_date IS NULL
                                        ORDER BY issue_id DESC LIMIT 1
                                    """, (selected_copy["copy_id"], member_id), fetchone=True)

                                    due_dt = new_issue["due_date"] if new_issue else "14 days from today"
                                    iss_id = new_issue["issue_id"] if new_issue else None

                                    # Send email receipt (safe try-except)
                                    try:
                                        send_issue_confirmation(
                                            member_id=member_id,
                                            member_name=member.get("full_name", "Student Member"),
                                            email=member.get("email", ""),
                                            book_title=b["title"],
                                            barcode=selected_copy["barcode"],
                                            due_date=due_dt,
                                            issue_id=iss_id
                                        )
                                    except Exception as em_err:
                                        print(f"Notice email error: {em_err}")

                                    st.success(f"🎉 Successfully borrowed '{b['title']}'! Barcode: `{selected_copy['barcode']}` | Due Date: **{due_dt}**.")
                                    st.rerun()
                                else:
                                    st.error(f"Cannot borrow: {res}")

                    else:
                        # Book is currently unavailable
                        with act_col1:
                            if already_reserved:
                                ready_info = f" (Ready for pickup until {already_reserved['ready_until']})" if already_reserved["status"] == "Ready" else ""
                                st.info(f"📌 You currently have a **{already_reserved['status']}** reservation for this book{ready_info}.")
                            else:
                                st.caption("All physical copies are currently checked out by other readers. You can place a reservation to hold the next returned copy.")
                        with act_col2:
                            if already_reserved:
                                if st.button("Cancel Hold", key=f"cancel_res_cat_{already_reserved['reservation_id']}", use_container_width=True):
                                    ok, msg = call_procedure("sp_cancel_reservation", (already_reserved["reservation_id"],))
                                    if ok:
                                        st.success("Reservation cancelled.")
                                        st.rerun()
                                    else:
                                        st.error(f"Error: {msg}")
                            else:
                                if st.button(f"📌 Reserve This Book", key=f"res_{b['book_id']}", type="primary", use_container_width=True):
                                    ok, res_msg = call_procedure("sp_reserve_book", (member_id, b["book_id"]))
                                    if ok:
                                        st.success(f"🎉 Successfully reserved '{b['title']}'! You will receive an email notice as soon as a copy is returned.")
                                        st.rerun()
                                    else:
                                        st.error(f"Cannot reserve: {res_msg}")

                    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 6: MY BORROWING HISTORY
    # =========================================================================
    with tabs[5]:
        st.subheader("📜 Complete Personal Circulation History")
        st.caption("All your past borrowing records, return dates, condition check-ins, and fines.")

        hist_records = execute_query("""
            SELECT 
                issue_id,
                title,
                barcode,
                issue_date,
                due_date,
                return_date,
                status,
                return_condition,
                fine_amount,
                fine_status
            FROM v_circulation_history
            WHERE member_id = %s
            ORDER BY issue_id DESC
        """, (member_id,))

        if hist_records:
            st.dataframe(pd.DataFrame(hist_records), use_container_width=True)
        else:
            st.info("No previous borrowing history on file.")

    # =========================================================================
    # TAB 7: MY RESERVATIONS
    # =========================================================================
    with tabs[6]:
        st.subheader("📌 My Book Reservations & Holds")

        my_res = execute_query("""
            SELECT 
                r.reservation_id,
                b.title,
                r.status,
                r.reserved_on,
                r.ready_until,
                r.copy_id,
                c.barcode
            FROM reservations r
            JOIN books b ON b.book_id = r.book_id
            LEFT JOIN book_copies c ON c.copy_id = r.copy_id
            WHERE r.member_id = %s
            ORDER BY r.reservation_id DESC
        """, (member_id,))

        if my_res:
            for r in my_res:
                st_color = "#3b82f6" if r["status"] == "Pending" else ("#10b981" if r["status"] == "Ready" else "#64748b")
                c_r1, c_r2 = st.columns([4, 1])
                with c_r1:
                    ready_info = f" — <strong>Ready for pickup until {r['ready_until']}!</strong>" if r["status"] == "Ready" else ""
                    st.markdown(
                        f"""
                        <div style="padding: 12px; background: #f8fafc; border-left: 4px solid {st_color}; border-radius: 6px; margin-bottom: 8px; color: #1e293b;">
                            <strong style="color: #0f172a;">{r['title']}</strong> | Status: <span style="color: {st_color}; font-weight: 600;">{r['status']}</span>{ready_info}<br>
                            <small style="color: #64748b;">Reserved on: {r['reserved_on']}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with c_r2:
                    if r["status"] in ("Pending", "Ready"):
                        if st.button("Cancel Hold", key=f"cancel_res_{r['reservation_id']}", use_container_width=True):
                            ok, msg = call_procedure("sp_cancel_reservation", (r["reservation_id"],))
                            if ok:
                                st.success("Reservation cancelled.")
                                st.rerun()
                            else:
                                st.error(f"Error: {msg}")
        else:
            st.info("You have no active or past reservations.")

    # =========================================================================
    # TAB 8: DIGITAL LIBRARY CARD
    # =========================================================================
    with tabs[7]:
        st.subheader("🪪 Digital Membership Card")

        st.markdown(
            f"""
            <div style="max-width: 480px; margin: 20px auto; background: linear-gradient(135deg, #1e1b4b, #312e81, #4338ca); color: white; padding: 25px; border-radius: 18px; box-shadow: 0 15px 35px rgba(30, 27, 75, 0.4); border: 1px solid rgba(255,255,255,0.15);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <div>
                        <span style="font-size: 1.1rem; font-weight: 700; letter-spacing: 1px;">DIGITAL LIBRARY</span><br>
                        <small style="color: #c7d2fe; font-size: 0.75rem;">OFFICIAL CIRCULATION PASS</small>
                    </div>
                    <span style="font-size: 28px;">🏛️</span>
                </div>
                
                <div style="margin: 25px 0;">
                    <div style="font-size: 0.75rem; color: #a5b4fc; text-transform: uppercase; letter-spacing: 0.5px;">Member Name</div>
                    <div style="font-size: 1.35rem; font-weight: 700; margin-top: 2px;">{member.get('full_name')}</div>
                </div>

                <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                    <div>
                        <div style="font-size: 0.75rem; color: #a5b4fc;">MEMBER ID</div>
                        <div style="font-size: 1.1rem; font-weight: 600;">#{member.get('member_id')}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #a5b4fc;">ROLE / TYPE</div>
                        <div style="font-size: 1.1rem; font-weight: 600;">{member.get('member_type')}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #a5b4fc;">VALID UNTIL</div>
                        <div style="font-size: 1.1rem; font-weight: 600;">{member.get('expires_on')}</div>
                    </div>
                </div>

                <div style="border-top: 1px dashed rgba(255,255,255,0.25); padding-top: 15px; display: flex; justify-content: space-between; align-items: center;">
                    <small style="color: #c7d2fe; font-size: 0.75rem;">Status: <strong style="color: #86efac;">{member.get('status')}</strong></small>
                    <span style="font-family: monospace; font-size: 0.95rem; letter-spacing: 2px; color: #e0e7ff;">LIB-{member.get('member_id'):06d}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div style="max-width: 480px; margin: 0 auto; background: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; font-size: 0.9rem; color: #1e293b;">
                <p style="margin: 4px 0; color: #334155;"><strong style="color: #0f172a;">Email:</strong> {member.get('email')}</p>
                <p style="margin: 4px 0; color: #334155;"><strong style="color: #0f172a;">Phone:</strong> {member.get('phone') or 'Not provided'}</p>
                <p style="margin: 4px 0; color: #334155;"><strong style="color: #0f172a;">Joined On:</strong> {member.get('joined_on')}</p>
                <p style="margin: 4px 0; color: #334155;"><strong style="color: #0f172a;">Address:</strong> {member.get('address') or 'Campus Library'}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
