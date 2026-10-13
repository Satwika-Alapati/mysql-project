"""
Librarian Management Portal.
Provides end-to-end administration for Book Catalog, Physical Copies,
Circulation Desk (Borrow/Return), Members, Reservations, Fines, Analytics, and Notifications.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import execute_query, execute_non_query, call_procedure, run_maintenance, add_book_to_catalog
from analytics import (
    get_popular_books_chart,
    get_category_distribution_chart,
    get_copy_status_distribution_chart,
    get_fines_summary_chart,
    get_circulation_trends_chart
)
from email_service import (
    send_issue_confirmation,
    send_return_receipt,
    send_overdue_warning,
    send_all_overdue_reminders,
    send_library_email,
    EMAIL_SIMULATION_MODE
)


def render_librarian_portal(user_info):
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 20px;">
            <div>
                <h3 style="margin: 0; font-size: 1.4rem; color: #1e293b;">👑 Librarian Administrative Hub</h3>
                <small style="color: #64748b;">Logged in as: <strong>{user_info.get('full_name')}</strong> (@{user_info.get('username')})</small>
            </div>
            <div>
                <span style="background: #e0e7ff; color: #4338ca; padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;">
                    🛡️ Administrator
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Navigation Tabs
    tabs = st.tabs([
        "📊 Dashboard & Analytics",
        "🔄 Circulation Desk",
        "📚 Book Catalog",
        "🏷️ Book Copies",
        "👥 Members",
        "📌 Reservations",
        "💰 Fines & Dues",
        "✍️ Authors & Publishers",
        "🔔 Email & Notifications",
        "⚙️ System Settings"
    ])

    # =========================================================================
    # TAB 1: DASHBOARD & ANALYTICS
    # =========================================================================
    with tabs[0]:
        st.subheader("System Performance & Library Metrics")

        # Key Metrics Row
        m_books = execute_query("SELECT COUNT(*) AS c FROM books", fetchone=True)["c"]
        m_copies = execute_query("SELECT COUNT(*) AS c FROM book_copies", fetchone=True)["c"]
        m_loans = execute_query("SELECT COUNT(*) AS c FROM issues WHERE return_date IS NULL", fetchone=True)["c"]
        m_overdue = execute_query("SELECT COUNT(*) AS c FROM issues WHERE return_date IS NULL AND due_date < CURDATE()", fetchone=True)["c"]
        m_fines = execute_query("SELECT COALESCE(SUM(amount), 0) AS s FROM fines WHERE status = 'Unpaid'", fetchone=True)["s"]
        m_members = execute_query("SELECT COUNT(*) AS c FROM members WHERE status = 'Active'", fetchone=True)["c"]

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("📖 Titles", m_books)
        col2.metric("🏷️ Copies", m_copies)
        col3.metric("🔄 Active Loans", m_loans)
        col4.metric("⚠️ Overdue", m_overdue, delta=-m_overdue if m_overdue > 0 else 0, delta_color="inverse")
        col5.metric("💰 Unpaid Fines", f"${float(m_fines):.2f}")
        col6.metric("👥 Members", m_members)

        st.divider()

        # Visual Analytics Charts
        c1, c2 = st.columns(2)
        with c1:
            fig_pop = get_popular_books_chart()
            if fig_pop:
                st.plotly_chart(fig_pop, use_container_width=True)
            else:
                st.info("No borrow analytics yet.")

        with c2:
            fig_stat = get_copy_status_distribution_chart()
            if fig_stat:
                st.plotly_chart(fig_stat, use_container_width=True)
            else:
                st.info("No copy status data.")

        c3, c4 = st.columns(2)
        with c3:
            fig_cat = get_category_distribution_chart()
            if fig_cat:
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("No category data.")

        with c4:
            fig_trend = get_circulation_trends_chart()
            if fig_trend:
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("No circulation trends yet.")

        # Overdue Loans Quick Action Table
        st.subheader("🚨 Overdue Items Requiring Follow-up")
        overdues = execute_query("""
            SELECT 
                i.issue_id,
                m.member_id,
                m.full_name AS member_name,
                m.email,
                b.title,
                c.barcode,
                i.issue_date,
                i.due_date,
                DATEDIFF(CURDATE(), i.due_date) AS days_late,
                fn_calc_fine(i.due_date, CURDATE()) AS fine_accrued
            FROM issues i
            JOIN members m ON m.member_id = i.member_id
            JOIN book_copies c ON c.copy_id = i.copy_id
            JOIN books b ON b.book_id = c.book_id
            WHERE i.return_date IS NULL AND i.due_date < CURDATE()
            ORDER BY days_late DESC
        """)

        if overdues:
            st.markdown(
                """
                <div style="padding: 10px 14px; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; margin-bottom: 12px; color: #9f1239; font-size: 0.9rem;">
                    💡 <strong>Automated Fine Alerts:</strong> Students accrue fines for each delayed day. You can send an individual warning or broadcast reminders with the calculated fine total to all overdue borrowers in one click.
                </div>
                """,
                unsafe_allow_html=True
            )

            df_od = pd.DataFrame(overdues)
            st.dataframe(df_od[["issue_id", "member_name", "email", "title", "barcode", "due_date", "days_late", "fine_accrued"]], use_container_width=True)

            od_btn_col1, od_btn_col2 = st.columns([2, 1])
            with od_btn_col1:
                selected_issue = st.selectbox(
                    "Select Overdue Loan to Email Warning with Fine Amount:",
                    options=overdues,
                    format_func=lambda x: f"Issue #{x['issue_id']} - {x['member_name']} ('{x['title']}' | {x['days_late']} days late | Fine: ${float(x['fine_accrued']):.2f})"
                )
            with od_btn_col2:
                st.write("")
                st.write("")
                if st.button("📧 Send Warning to Selected Student", use_container_width=True, type="primary"):
                    res = send_overdue_warning(
                        member_id=selected_issue["member_id"],
                        member_name=selected_issue["member_name"],
                        email=selected_issue["email"],
                        book_title=selected_issue["title"],
                        due_date=selected_issue["due_date"],
                        accrued_fine=float(selected_issue["fine_accrued"]),
                        issue_id=selected_issue["issue_id"],
                        days_overdue=int(selected_issue["days_late"])
                    )
                    st.success(f"✅ Overdue reminder with fine of **${float(selected_issue['fine_accrued']):.2f}** sent to **{selected_issue['email']}**!")

            # Bulk broadcast button
            if st.button("📢 Broadcast Overdue & Fine Reminders to ALL Late Students", type="secondary"):
                b_res = send_all_overdue_reminders()
                st.success(f"🎉 Sent overdue notices with fine amounts to **{b_res['count']} students** (Total fines notified: **${b_res['total_fines']:.2f}**)! Logged to MySQL database.")
                st.rerun()
        else:
            st.success("✅ Clean circulation desk! No overdue books currently.")

    # =========================================================================
    # TAB 2: CIRCULATION DESK (BORROW & RETURN)
    # =========================================================================
    with tabs[1]:
        st.subheader("🔄 Circulation Desk (Checkout & Check-in)")

        circ_tab1, circ_tab2, circ_tab3 = st.tabs(["📤 Issue Book (Checkout)", "📥 Return Book (Check-in)", "👥 Who Took The Books (Borrowers)"])

        # SUB-TAB 1: ISSUE BOOK
        with circ_tab1:
            st.markdown("##### Issue a Physical Copy to a Member")
            st.caption("Checks member status, max loan limit, unpaid fines, and updates physical copy status to 'Issued'.")

            # Load active members
            active_members = execute_query("""
                SELECT member_id, full_name, email, member_type,
                       fn_member_active_loans(member_id) as active_loans,
                       fn_member_unpaid_fines(member_id) as unpaid_fines
                FROM members 
                WHERE status = 'Active'
                ORDER BY full_name ASC
            """)

            # Load available copies
            available_copies = execute_query("""
                SELECT c.copy_id, c.barcode, c.shelf_location, b.title, b.isbn, b.book_id
                FROM book_copies c
                JOIN books b ON b.book_id = c.book_id
                WHERE c.status = 'Available'
                ORDER BY b.title ASC, c.copy_id ASC
            """)

            col_iss1, col_iss2 = st.columns(2)

            with col_iss1:
                if not active_members:
                    st.warning("No active members found.")
                    sel_member = None
                else:
                    sel_member = st.selectbox(
                        "1. Select Member *",
                        options=active_members,
                        format_func=lambda m: f"{m['full_name']} (ID: {m['member_id']} | Loans: {m['active_loans']} | Dues: ${float(m['unpaid_fines']):.2f})"
                    )

            with col_iss2:
                if not available_copies:
                    st.warning("No available physical copies in the library right now.")
                    sel_copy = None
                else:
                    sel_copy = st.selectbox(
                        "2. Select Available Copy *",
                        options=available_copies,
                        format_func=lambda c: f"'{c['title']}' | Barcode: {c['barcode']} (Shelf: {c['shelf_location'] or 'General'})"
                    )

            if sel_member and sel_copy:
                st.info(f"Issuing **{sel_copy['title']}** (Barcode: `{sel_copy['barcode']}`) to **{sel_member['full_name']}**.")
                if st.button("Confirm Checkout & Issue Book", type="primary", use_container_width=True):
                    # Call Stored Procedure
                    ok, result = call_procedure("sp_issue_book", (sel_member["member_id"], sel_copy["copy_id"]))
                    if ok:
                        # Fetch the new issue details for email confirmation
                        new_issue = execute_query("""
                            SELECT issue_id, due_date FROM issues 
                            WHERE copy_id = %s AND member_id = %s AND return_date IS NULL
                            ORDER BY issue_id DESC LIMIT 1
                        """, (sel_copy["copy_id"], sel_member["member_id"]), fetchone=True)

                        due_dt = new_issue["due_date"] if new_issue else "14 days from today"
                        issue_id = new_issue["issue_id"] if new_issue else None

                        # Send Confirmation Email (safe try-except)
                        try:
                            send_issue_confirmation(
                                member_id=sel_member["member_id"],
                                member_name=sel_member["full_name"],
                                email=sel_member["email"],
                                book_title=sel_copy["title"],
                                barcode=sel_copy["barcode"],
                                due_date=due_dt,
                                issue_id=issue_id
                            )
                        except Exception as em_err:
                            print(f"Notice email error: {em_err}")

                        st.success(f"🎉 Book successfully issued! Due date: **{due_dt}**. Confirmation email recorded to member.")
                        st.rerun()
                    else:
                        st.error(f"❌ Cannot issue book: {result}")

        # SUB-TAB 2: RETURN BOOK
        with circ_tab2:
            st.markdown("##### Check-in a Returned Book")
            st.caption("Inspect physical condition, calculate overdue fines automatically, and update copy availability.")

            active_loans = execute_query("""
                SELECT 
                    i.issue_id,
                    i.member_id,
                    m.full_name,
                    m.email,
                    b.title,
                    c.copy_id,
                    c.barcode,
                    i.issue_date,
                    i.due_date,
                    DATEDIFF(CURDATE(), i.due_date) AS days_late,
                    fn_calc_fine(i.due_date, CURDATE()) AS current_fine
                FROM issues i
                JOIN members m ON m.member_id = i.member_id
                JOIN book_copies c ON c.copy_id = i.copy_id
                JOIN books b ON b.book_id = c.book_id
                WHERE i.return_date IS NULL
                ORDER BY i.due_date ASC
            """)

            if not active_loans:
                st.info("No books are currently issued out.")
            else:
                col_ret1, col_ret2 = st.columns([2, 1])
                with col_ret1:
                    sel_loan = st.selectbox(
                        "Select Active Loan to Return:",
                        options=active_loans,
                        format_func=lambda x: f"Issue #{x['issue_id']} - '{x['title']}' borrowed by {x['full_name']} (Due: {x['due_date']})"
                    )
                with col_ret2:
                    return_condition = st.selectbox(
                        "Inspected Book Condition:",
                        options=["Good", "Damaged", "Lost"],
                        help="Damaged/Lost status will automatically assess replacement fees."
                    )

                if sel_loan:
                    is_late = sel_loan["days_late"] > 0
                    fine_est = float(sel_loan["current_fine"]) if is_late else 0.0

                    if is_late:
                        st.warning(f"⚠️ Book is **{sel_loan['days_late']} days overdue**! Overdue fine calculated: **${fine_est:.2f}**")
                    if return_condition != "Good":
                        st.error(f"⚠️ Condition marked as **{return_condition}**! Additional penalty fee will be billed.")

                    if st.button("Process Book Return", type="primary", use_container_width=True):
                        ok, ret_res = call_procedure("sp_return_book", (sel_loan["issue_id"], return_condition))
                        if ok:
                            # Send Return Receipt Email
                            send_return_receipt(
                                sel_loan["member_id"],
                                sel_loan["full_name"],
                                sel_loan["email"],
                                sel_loan["title"],
                                sel_loan["barcode"],
                                fine_est,
                                return_condition
                            )
                            st.success(f"🎉 Book '{sel_loan['title']}' returned successfully! Copy status updated and receipt emailed.")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to return book: {ret_res}")

        # SUB-TAB 3: WHO TOOK THE BOOKS (BORROWERS LIVE TRACKER)
        with circ_tab3:
            st.markdown("##### 👥 Live Borrower Access & Circulation Records ('Who Took the Books')")
            st.caption("Detailed view of everyone who currently has books checked out, their contact info, due dates, and fines.")

            bw_search = st.text_input("🔍 Search Borrowers (Name, Email, Book Title, Barcode):", "", key="lib_borrowers_search")

            lib_borrow_sql = """
                SELECT 
                    i.issue_id,
                    m.member_id,
                    m.full_name AS borrower_name,
                    m.email AS borrower_email,
                    m.phone AS borrower_phone,
                    b.title AS book_title,
                    b.isbn,
                    c.barcode,
                    c.shelf_location,
                    i.issue_date,
                    i.due_date,
                    CASE 
                        WHEN i.due_date < CURDATE() THEN '🚨 Overdue'
                        ELSE '🟢 On Time'
                    END AS loan_status,
                    CASE 
                        WHEN i.due_date < CURDATE() THEN DATEDIFF(CURDATE(), i.due_date)
                        ELSE 0
                    END AS days_overdue,
                    fn_calc_fine(i.due_date, CURDATE()) AS fine_accrued
                FROM issues i
                JOIN members m ON m.member_id = i.member_id
                JOIN book_copies c ON c.copy_id = i.copy_id
                JOIN books b ON b.book_id = c.book_id
                WHERE i.return_date IS NULL
            """
            lib_params = []
            if bw_search.strip():
                q = f"%{bw_search.strip()}%"
                lib_borrow_sql += " AND (m.full_name LIKE %s OR m.email LIKE %s OR b.title LIKE %s OR c.barcode LIKE %s)"
                lib_params.extend([q, q, q, q])

            lib_borrow_sql += " ORDER BY i.due_date ASC"
            loans_data = execute_query(lib_borrow_sql, lib_params)

            if loans_data:
                df_loans = pd.DataFrame(loans_data)
                st.dataframe(df_loans, use_container_width=True)
            else:
                st.info("No active loans.")

    # =========================================================================
    # TAB 3: BOOK CATALOG
    # =========================================================================
    with tabs[2]:
        st.subheader("📚 Book Catalog Management")

        cat_col1, cat_col2 = st.columns([3, 1])
        with cat_col1:
            search_query = st.text_input("🔍 Search Catalog (Title, ISBN, Category, or Author):", "")
        with cat_col2:
            show_add_book = st.checkbox("➕ Add New Book Title", value=False)

        # ADD NEW BOOK FORM
        if show_add_book:
            with st.expander("📖 Add New Book to Library Catalog", expanded=True):
                with st.form("add_book_form", clear_on_submit=True):
                    ab_c1, ab_c2 = st.columns(2)
                    with ab_c1:
                        new_isbn = st.text_input("ISBN *", placeholder="e.g. 978-0132350884")
                        new_title = st.text_input("Book Title *", placeholder="e.g. Clean Code")
                        new_edition = st.text_input("Edition", value="1st")
                        new_year = st.number_input("Publication Year", min_value=1800, max_value=2030, value=2024)
                    with ab_c2:
                        categories = execute_query("SELECT category_id, name FROM categories ORDER BY name")
                        publishers = execute_query("SELECT publisher_id, name FROM publishers ORDER BY name")
                        authors = execute_query("SELECT author_id, name FROM authors ORDER BY name")

                        new_cat = st.selectbox("Category *", options=categories, format_func=lambda x: x["name"])
                        new_pub = st.selectbox("Publisher *", options=publishers, format_func=lambda x: x["name"])
                        new_authors = st.multiselect("Authors *", options=authors, format_func=lambda x: x["name"])
                        new_price = st.number_input("Price ($)", min_value=0.0, value=45.0, step=1.0)
                        new_lang = st.text_input("Language", value="English")
                        new_copies = st.number_input("Number of Copies to Add to Stack *", min_value=1, max_value=25, value=3)
                        new_shelf = st.text_input("Shelf Location Code", value="Stack A - Shelf 101")

                    submitted_book = st.form_submit_button("Save Book to Catalog & Create Copies", type="primary", use_container_width=True)
                    if submitted_book:
                        if not new_isbn or not new_title or not new_cat or not new_pub or not new_authors:
                            st.error("Please fill in all required fields (ISBN, Title, Category, Publisher, Authors).")
                        else:
                            ok_lib, b_id_lib, msg_lib = add_book_to_catalog(
                                title=new_title,
                                isbn=new_isbn,
                                category_name=new_cat["name"],
                                publisher_name=new_pub["name"],
                                author_names=[a["name"] for a in new_authors],
                                publication_year=int(new_year),
                                edition=new_edition,
                                language=new_lang,
                                price=float(new_price),
                                num_copies=int(new_copies),
                                shelf_location=new_shelf
                            )
                            if ok_lib:
                                st.success(f"🎉 {msg_lib}")
                                st.rerun()
                            else:
                                st.error(f"❌ {msg_lib}")

        # DISPLAY CATALOG TABLE
        cat_sql = """
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
        if search_query:
            cat_sql += " AND (b.title LIKE %s OR b.isbn LIKE %s OR c.name LIKE %s OR a.name LIKE %s)"
            q = f"%{search_query.strip()}%"
            params.extend([q, q, q, q])

        cat_sql += " GROUP BY b.book_id ORDER BY b.title ASC"

        catalog_data = execute_query(cat_sql, params)
        if catalog_data:
            df_cat = pd.DataFrame(catalog_data)
            st.dataframe(
                df_cat[[
                    "book_id", "title", "authors", "category", "publisher",
                    "isbn", "publication_year", "price", "total_copies", "available_copies"
                ]],
                use_container_width=True
            )
        else:
            st.info("No books match your search.")

    # =========================================================================
    # TAB 4: BOOK COPIES TRACKING
    # =========================================================================
    with tabs[3]:
        st.subheader("🏷️ Physical Copy Tracking & Inventory")
        st.caption("Track individual copies separately, assign shelf locations, barcodes, and manage physical conditions.")

        copy_col1, copy_col2 = st.columns([3, 1])
        with copy_col2:
            show_add_copy = st.checkbox("➕ Add New Physical Copy", value=False)

        # ADD NEW COPY FORM
        if show_add_copy:
            with st.expander("🏷️ Add Copy to Inventory", expanded=True):
                with st.form("add_copy_form", clear_on_submit=True):
                    books_list = execute_query("SELECT book_id, title, isbn FROM books ORDER BY title ASC")
                    if not books_list:
                        st.warning("Please add books to catalog first.")
                    else:
                        ac_c1, ac_c2 = st.columns(2)
                        with ac_c1:
                            target_book = st.selectbox("Select Book *", options=books_list, format_func=lambda b: f"{b['title']} (ISBN: {b['isbn']})")
                            copy_shelf = st.text_input("Shelf Location", placeholder="e.g. Shelf B-201, Rack 3")
                        with ac_c2:
                            default_barcode = f"BC-{target_book['book_id']}-{datetime.now().strftime('%H%M%S')}" if target_book else ""
                            copy_barcode = st.text_input("Barcode *", value=default_barcode)
                            copy_status = st.selectbox("Initial Status", options=["Available", "Damaged", "Lost"])

                        submit_copy = st.form_submit_button("Save Physical Copy", type="primary", use_container_width=True)
                        if submit_copy:
                            if not copy_barcode:
                                st.error("Barcode is required.")
                            else:
                                try:
                                    execute_non_query(
                                        "INSERT INTO book_copies (book_id, barcode, shelf_location, status, acquired_on) VALUES (%s, %s, %s, %s, CURDATE())",
                                        (target_book["book_id"], copy_barcode.strip(), copy_shelf.strip(), copy_status)
                                    )
                                    st.success(f"Physical copy `{copy_barcode}` added to inventory!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error adding copy: {str(e)}")

        # FILTER AND MANAGE COPIES
        copies_list = execute_query("""
            SELECT 
                c.copy_id,
                b.title,
                c.barcode,
                c.shelf_location,
                c.status,
                c.acquired_on,
                b.book_id
            FROM book_copies c
            JOIN books b ON b.book_id = c.book_id
            ORDER BY c.copy_id DESC
        """)

        if copies_list:
            df_copies = pd.DataFrame(copies_list)
            st.dataframe(df_copies[["copy_id", "title", "barcode", "shelf_location", "status", "acquired_on"]], use_container_width=True)

            # Update Copy Status
            st.markdown("##### Change Copy Status")
            uc_col1, uc_col2, uc_col3 = st.columns([2, 1, 1])
            with uc_col1:
                sel_cp = st.selectbox("Select Copy to Update:", options=copies_list, format_func=lambda c: f"Copy #{c['copy_id']} - {c['barcode']} ('{c['title']}' | Status: {c['status']})")
            with uc_col2:
                new_cp_status = st.selectbox("New Physical Status:", options=["Available", "Damaged", "Lost", "Reserved"])
            with uc_col3:
                st.write("")
                st.write("")
                if st.button("Update Status", use_container_width=True):
                    try:
                        execute_non_query("UPDATE book_copies SET status = %s WHERE copy_id = %s", (new_cp_status, sel_cp["copy_id"]))
                        st.success(f"Copy #{sel_cp['copy_id']} updated to {new_cp_status}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("No copies found in the database.")

    # =========================================================================
    # TAB 5: MEMBERS
    # =========================================================================
    with tabs[4]:
        st.subheader("👥 Library Members Directory")

        mem_c1, mem_c2 = st.columns([3, 1])
        with mem_c2:
            show_add_member = st.checkbox("➕ Add New Member", value=False)

        if show_add_member:
            with st.expander("📝 Register New Library Member", expanded=True):
                with st.form("add_member_form", clear_on_submit=True):
                    m_c1, m_c2 = st.columns(2)
                    with m_c1:
                        mf_name = st.text_input("Full Name *", placeholder="e.g. Sarah Jenkins")
                        mf_email = st.text_input("Email *", placeholder="sarah@example.com")
                        mf_type = st.selectbox("Member Type", options=["Student", "Faculty", "Public"])
                    with m_c2:
                        mf_phone = st.text_input("Phone", placeholder="e.g. 9876543210")
                        mf_addr = st.text_input("Address / Dept", placeholder="e.g. Computer Science")

                    if st.form_submit_button("Register Member", type="primary", use_container_width=True):
                        if not mf_name or not mf_email:
                            st.error("Full Name and Email are required.")
                        else:
                            try:
                                _, mid = execute_non_query("""
                                    INSERT INTO members (full_name, email, phone, address, member_type, status, joined_on, expires_on)
                                    VALUES (%s, %s, %s, %s, %s, 'Active', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 YEAR))
                                """, (mf_name.strip(), mf_email.strip(), mf_phone.strip(), mf_addr.strip(), mf_type))
                                st.success(f"Member {mf_name} registered successfully with Member ID: {mid}!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

        # Members list
        members_data = execute_query("""
            SELECT 
                m.member_id,
                m.full_name,
                m.email,
                m.phone,
                m.member_type,
                m.status,
                fn_member_active_loans(m.member_id) AS active_loans,
                fn_member_unpaid_fines(m.member_id) AS unpaid_fines,
                m.joined_on,
                m.expires_on
            FROM members m
            ORDER BY m.member_id DESC
        """)

        if members_data:
            df_m = pd.DataFrame(members_data)
            st.dataframe(df_m, use_container_width=True)

            # Member Profile Inspector
            st.markdown("##### 🔍 Inspect Member Profile & Circulation History")
            selected_m = st.selectbox("Select Member to View Details:", options=members_data, format_func=lambda m: f"{m['full_name']} (ID: {m['member_id']} | {m['email']})")

            if selected_m:
                hist = execute_query("""
                    SELECT issue_id, title, barcode, issue_date, due_date, return_date, status, return_condition, fine_amount, fine_status
                    FROM v_circulation_history
                    WHERE member_id = %s
                    ORDER BY issue_id DESC
                """, (selected_m["member_id"],))

                if hist:
                    st.dataframe(pd.DataFrame(hist), use_container_width=True)
                else:
                    st.info("No circulation history for this member.")

    # =========================================================================
    # TAB 6: RESERVATIONS
    # =========================================================================
    with tabs[5]:
        st.subheader("📌 Smart Book Reservations")
        st.caption("When a book is unavailable, members can reserve it. When returned, the system marks the reservation 'Ready'!")

        # Maintenance action to expire holds
        if st.button("⚡ Expire Outdated Holds (Run Maintenance)", help="Runs sp_expire_reservations to release copies if pickup window lapsed"):
            call_procedure("sp_expire_reservations")
            st.success("Expired reservations processed and copies released!")
            st.rerun()

        res_data = execute_query("""
            SELECT 
                r.reservation_id,
                b.title,
                m.full_name AS member_name,
                m.email,
                r.status,
                r.reserved_on,
                r.ready_until,
                r.copy_id
            FROM reservations r
            JOIN books b ON b.book_id = r.book_id
            JOIN members m ON m.member_id = r.member_id
            ORDER BY r.reservation_id DESC
        """)

        if res_data:
            st.dataframe(pd.DataFrame(res_data), use_container_width=True)

            active_res = [r for r in res_data if r["status"] in ("Pending", "Ready")]
            if active_res:
                st.markdown("##### Cancel Reservation")
                c_res1, c_res2 = st.columns([3, 1])
                with c_res1:
                    sel_can_res = st.selectbox(
                        "Select Reservation to Cancel:",
                        options=active_res,
                        format_func=lambda r: f"#{r['reservation_id']} - '{r['title']}' reserved by {r['member_name']} (Status: {r['status']})"
                    )
                with c_res2:
                    st.write("")
                    st.write("")
                    if st.button("Cancel Hold", type="secondary", use_container_width=True):
                        ok, msg = call_procedure("sp_cancel_reservation", (sel_can_res["reservation_id"],))
                        if ok:
                            st.success(f"Reservation #{sel_can_res['reservation_id']} cancelled and copy released!")
                            st.rerun()
                        else:
                            st.error(f"Error cancelling: {msg}")
        else:
            st.info("No reservations currently in the system.")

    # =========================================================================
    # TAB 7: FINES & DUES
    # =========================================================================
    with tabs[6]:
        st.subheader("💰 Fines & Payments Management")
        st.caption("Automated fine tracking based on days overdue and book condition.")

        fines_data = execute_query("""
            SELECT 
                f.fine_id,
                f.issue_id,
                m.full_name AS member_name,
                m.email,
                b.title,
                f.days_overdue,
                f.amount,
                f.reason,
                f.status,
                f.created_at,
                f.paid_on
            FROM fines f
            JOIN members m ON m.member_id = f.member_id
            JOIN issues i ON i.issue_id = f.issue_id
            JOIN book_copies c ON c.copy_id = i.copy_id
            JOIN books b ON b.book_id = c.book_id
            ORDER BY f.fine_id DESC
        """)

        if fines_data:
            st.dataframe(pd.DataFrame(fines_data), use_container_width=True)

            unpaid_fines = [f for f in fines_data if f["status"] == "Unpaid"]
            if unpaid_fines:
                st.markdown("##### 💵 Settle / Waive Fine")
                sf_c1, sf_c2, sf_c3 = st.columns([2, 1, 1])
                with sf_c1:
                    sel_fine = st.selectbox(
                        "Select Unpaid Fine:",
                        options=unpaid_fines,
                        format_func=lambda f: f"Fine #{f['fine_id']} - ${float(f['amount']):.2f} for {f['member_name']} ('{f['title']}')"
                    )
                with sf_c2:
                    st.write("")
                    st.write("")
                    if st.button("✅ Collect Payment (Paid)", type="primary", use_container_width=True):
                        ok, msg = call_procedure("sp_settle_fine", (sel_fine["fine_id"], "Paid"))
                        if ok:
                            st.success(f"Fine #{sel_fine['fine_id']} collected and marked as PAID!")
                            st.rerun()
                        else:
                            st.error(f"Error: {msg}")
                with sf_c3:
                    st.write("")
                    st.write("")
                    if st.button("⚖️ Waive Fine", type="secondary", use_container_width=True):
                        ok, msg = call_procedure("sp_settle_fine", (sel_fine["fine_id"], "Waived"))
                        if ok:
                            st.info(f"Fine #{sel_fine['fine_id']} has been waived.")
                            st.rerun()
                        else:
                            st.error(f"Error: {msg}")
            else:
                st.success("🎉 All fines have been settled!")
        else:
            st.info("No fines recorded in the database.")

    # =========================================================================
    # TAB 8: AUTHORS & PUBLISHERS
    # =========================================================================
    with tabs[7]:
        st.subheader("✍️ Authors & Publishers Directory")

        ap_c1, ap_c2 = st.columns(2)

        with ap_c1:
            st.markdown("##### Authors")
            with st.form("add_author_form", clear_on_submit=True):
                auth_name = st.text_input("Author Name *", placeholder="e.g. Robert C. Martin")
                auth_bio = st.text_area("Biography", placeholder="Software engineer and author...")
                if st.form_submit_button("Add Author", type="primary"):
                    if auth_name:
                        try:
                            execute_non_query("INSERT INTO authors (name, bio) VALUES (%s, %s)", (auth_name.strip(), auth_bio.strip()))
                            st.success(f"Author '{auth_name}' added!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.error("Name is required.")

            authors_db = execute_query("SELECT author_id, name, bio FROM authors ORDER BY name")
            if authors_db:
                st.dataframe(pd.DataFrame(authors_db), use_container_width=True)

        with ap_c2:
            st.markdown("##### Publishers")
            with st.form("add_publisher_form", clear_on_submit=True):
                pub_name = st.text_input("Publisher Name *", placeholder="e.g. Prentice Hall")
                pub_city = st.text_input("City", placeholder="e.g. New York")
                pub_email = st.text_input("Email", placeholder="e.g. contact@prenticehall.com")
                if st.form_submit_button("Add Publisher", type="primary"):
                    if pub_name:
                        try:
                            execute_non_query("INSERT INTO publishers (name, city, email) VALUES (%s, %s, %s)", (pub_name.strip(), pub_city.strip(), pub_email.strip()))
                            st.success(f"Publisher '{pub_name}' added!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.error("Name is required.")

            publishers_db = execute_query("SELECT publisher_id, name, city, email FROM publishers ORDER BY name")
            if publishers_db:
                st.dataframe(pd.DataFrame(publishers_db), use_container_width=True)

    # =========================================================================
    # TAB 9: EMAIL & NOTIFICATIONS
    # =========================================================================
    with tabs[8]:
        st.subheader("🔔 Notification Log & Email Dispatcher")

        mode_badge = "Simulation Mode (Direct Database Logging)" if EMAIL_SIMULATION_MODE else "Live SMTP Dispatch"
        st.info(f"📧 Notification Engine Status: **{mode_badge}**")

        # Notification table from MySQL
        notifs = execute_query("""
            SELECT 
                n.notification_id,
                m.full_name AS member_name,
                m.email,
                n.type,
                n.subject,
                n.status,
                n.sent_at,
                n.created_at,
                n.error
            FROM notifications n
            JOIN members m ON m.member_id = n.member_id
            ORDER BY n.notification_id DESC
            LIMIT 50
        """)

        if notifs:
            st.dataframe(pd.DataFrame(notifs), use_container_width=True)
        else:
            st.info("No notifications recorded yet.")

        # Manual Custom Email Sender
        st.markdown("##### Send Custom Library Notice")
        with st.form("custom_email_form", clear_on_submit=True):
            members_all = execute_query("SELECT member_id, full_name, email FROM members WHERE status = 'Active' ORDER BY full_name")
            target_mem = st.selectbox("Recipient Member:", options=members_all, format_func=lambda m: f"{m['full_name']} ({m['email']})")
            subj = st.text_input("Subject *", value="Library Announcement: Holiday Operating Hours")
            body = st.text_area("Message Body *", value="Dear Member, Please note that the library circulation desk will be open until 8 PM this Friday.")

            if st.form_submit_button("Send Notice", type="primary"):
                if target_mem and subj and body:
                    res = send_library_email(target_mem["member_id"], target_mem["email"], subj, body, notif_type="Custom Notice")
                    st.success(f"Notice sent to {target_mem['email']} ({res['mode']}) and logged to MySQL database!")
                    st.rerun()

    # =========================================================================
    # TAB 10: SYSTEM SETTINGS
    # =========================================================================
    with tabs[9]:
        st.subheader("⚙️ Circulation Rules & Database Maintenance")

        col_st1, col_st2 = st.columns(2)

        with col_st1:
            st.markdown("##### Circulation Rules & Fines Configuration")
            settings = execute_query("SELECT setting_key, setting_value FROM settings")
            settings_dict = {s["setting_key"]: s["setting_value"] for s in settings}

            with st.form("settings_form"):
                daily_fine = st.number_input("Daily Fine Rate ($)", value=float(settings_dict.get("fine_per_day", 5.0)), step=0.5)
                loan_period = st.number_input("Standard Loan Period (Days)", value=int(settings_dict.get("loan_days", 14)), step=1)
                max_borrow = st.number_input("Max Books Allowed per Member", value=int(settings_dict.get("max_loans", 5)), step=1)
                fine_cap = st.number_input("Fine Block Limit ($)", value=float(settings_dict.get("fine_block_limit", 100.0)), step=5.0)
                hold_days = st.number_input("Reservation Hold Window (Days)", value=int(settings_dict.get("reservation_hold_days", 3)), step=1)

                if st.form_submit_button("Save Policy Settings", type="primary"):
                    execute_non_query("UPDATE settings SET setting_value = %s WHERE setting_key = 'fine_per_day'", (str(daily_fine),))
                    execute_non_query("UPDATE settings SET setting_value = %s WHERE setting_key = 'loan_days'", (str(loan_period),))
                    execute_non_query("UPDATE settings SET setting_value = %s WHERE setting_key = 'max_loans'", (str(max_borrow),))
                    execute_non_query("UPDATE settings SET setting_value = %s WHERE setting_key = 'fine_block_limit'", (str(fine_cap),))
                    execute_non_query("UPDATE settings SET setting_value = %s WHERE setting_key = 'reservation_hold_days'", (str(hold_days),))
                    st.success("✅ Circulation settings saved directly to MySQL database!")
                    st.rerun()

        with col_st2:
            st.markdown("##### Automated Stored Procedures Execution")
            st.caption("Trigger automated MySQL database procedures manually:")

            if st.button("🚀 Run Daily Maintenance Procedure (sp_daily_maintenance)", use_container_width=True):
                ok, msg = run_maintenance()
                if ok:
                    st.success("✅ Procedure `sp_daily_maintenance` completed! Overdue loans updated and automated notices generated.")
                else:
                    st.error(f"Error: {msg}")

            if st.button("⏱️ Run Reservation Expiration (sp_expire_reservations)", use_container_width=True):
                ok, msg = call_procedure("sp_expire_reservations")
                if ok:
                    st.success("✅ Procedure `sp_expire_reservations` completed! Lapsed holds released.")
                else:
                    st.error(f"Error: {msg}")
