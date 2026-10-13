"""
Admin Side Dashboard Module.
Provides administrative controls:
1. 'Who Took the Books' (Comprehensive live borrower tracking, active loans, overdue alerts, and circulation history).
2. 'Add Books' (Manual addition with auto-generated copies, plus smart 1-click API autofill from Open Library).
3. Book Catalog & Inventory Management.
4. Member Oversight & Audit.
5. Digital E-Books Administration.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import execute_query, execute_non_query, call_procedure, run_maintenance
from ebooks_api import (
    search_openlibrary_api,
    CURATED_EBOOKS,
    get_db_ebooks,
    add_ebook_to_db,
    delete_ebook_from_db
)
from email_service import (
    send_issue_confirmation,
    send_return_receipt,
    send_overdue_warning,
    send_all_overdue_reminders
)
from auth import (
    register_user,
    reset_user_password,
    get_all_system_users
)


def render_admin_dashboard(user_info):
    """Render the primary Administration Hub."""
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 14px 20px; background: linear-gradient(135deg, #1e1b4b, #312e81); border-radius: 14px; margin-bottom: 22px; color: white; box-shadow: 0 4px 15px rgba(30, 27, 75, 0.2);">
            <div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.8rem;">🛡️</span>
                    <div>
                        <h2 style="margin: 0; font-size: 1.5rem; font-weight: 800; color: #ffffff;">Admin Master Dashboard</h2>
                        <small style="color: #c7d2fe;">System Administrator: <strong>{user_info.get('full_name', 'Administrator')}</strong> (@{user_info.get('username')})</small>
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 8px;">
                <span style="background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25); color: #ffffff; padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;">
                    👑 Full Admin Privileges
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Top KPI Metrics Row
    try:
        cnt_books = execute_query("SELECT COUNT(*) AS c FROM books", fetchone=True)["c"]
        cnt_copies = execute_query("SELECT COUNT(*) AS c FROM book_copies", fetchone=True)["c"]
        cnt_active_loans = execute_query("SELECT COUNT(*) AS c FROM issues WHERE return_date IS NULL", fetchone=True)["c"]
        cnt_overdue = execute_query("SELECT COUNT(*) AS c FROM issues WHERE return_date IS NULL AND due_date < CURDATE()", fetchone=True)["c"]
        cnt_borrowers = execute_query("SELECT COUNT(DISTINCT member_id) AS c FROM issues WHERE return_date IS NULL", fetchone=True)["c"]
        sum_fines = execute_query("SELECT COALESCE(SUM(amount), 0) AS s FROM fines WHERE status = 'Unpaid'", fetchone=True)["s"]
    except Exception as e:
        cnt_books, cnt_copies, cnt_active_loans, cnt_overdue, cnt_borrowers, sum_fines = 0, 0, 0, 0, 0, 0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("📖 Catalog Titles", cnt_books)
    k2.metric("🏷️ Total Copies", cnt_copies)
    k3.metric("📤 Books Taken Out", cnt_active_loans)
    k4.metric("👥 Active Borrowers", cnt_borrowers)
    k5.metric("🚨 Overdue Items", cnt_overdue, delta=-cnt_overdue if cnt_overdue > 0 else 0, delta_color="inverse")
    k6.metric("💰 Unpaid Fines", f"${float(sum_fines):.2f}")

    st.write("")

    # Main Navigation Tabs
    tabs = st.tabs([
        "👥 Who Took The Books (Borrowers)",
        "➕ Add New Books",
        "📚 Catalog & Copies",
        "⚡ Quick Circulation Desk",
        "🌐 Digital E-Books Catalog",
        "👤 Member Accounts",
        "⚙️ System Maintenance"
    ])

    # =========================================================================
    # TAB 1: WHO TOOK THE BOOKS (BORROWER ACCESS & TRACKING)
    # =========================================================================
    with tabs[0]:
        st.subheader("👥 Live Borrower Tracker & Circulation Records")
        st.caption("Complete transparency into who borrowed books, current possession, due dates, late fees, and borrower contact details.")

        # Filter Sub-Tabs / View Mode
        filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
        with filter_col1:
            search_borrower = st.text_input(
                "🔍 Search Borrowers (Name, Email, Student Username, Book Title, or Barcode):",
                placeholder="Type to filter immediately...",
                key="admin_search_borrowers"
            )
        with filter_col2:
            status_filter = st.selectbox(
                "Filter Circulation Status:",
                options=["🔴 Currently Holding Books (Active)", "🚨 Overdue Borrowers Only", "🟢 Returned Books History", "📋 All Records"],
                index=0
            )
        with filter_col3:
            st.write("")
            st.write("")
            refresh_btn = st.button("🔄 Refresh Data", use_container_width=True)

        # Build Query based on status_filter
        base_sql = """
            SELECT 
                i.issue_id,
                m.member_id,
                m.full_name AS borrower_name,
                u.username AS student_username,
                m.email AS borrower_email,
                m.phone AS borrower_phone,
                m.address AS borrower_dept,
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

        if status_filter == "🔴 Currently Holding Books (Active)":
            base_sql += " AND i.return_date IS NULL"
        elif status_filter == "🚨 Overdue Borrowers Only":
            base_sql += " AND i.return_date IS NULL AND i.due_date < CURDATE()"
        elif status_filter == "🟢 Returned Books History":
            base_sql += " AND i.return_date IS NOT NULL"

        if search_borrower.strip():
            sq = f"%{search_borrower.strip()}%"
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
            st.info("ℹ️ No borrowing records found matching your current filter.")
        else:
            st.markdown(f"Found **{len(borrower_records)}** record(s).")
            df_disp = pd.DataFrame(borrower_records)

            # Display friendly columns
            cols_to_show = [
                "issue_id", "borrower_name", "student_username", "borrower_email", "borrower_phone",
                "book_title", "barcode", "shelf_location", "issue_date", "due_date",
                "loan_status", "days_overdue", "fine_amount"
            ]
            st.dataframe(df_disp[cols_to_show], use_container_width=True)

            st.divider()

            # Actions on specific borrower
            st.markdown("##### ⚡ Quick Administrative Actions on Borrowers")
            act_col1, act_col2 = st.columns([2, 1])

            active_only = [r for r in borrower_records if r["return_date"] is None]
            if active_only:
                with act_col1:
                    sel_borrower_record = st.selectbox(
                        "Select Active Loan to Manage / Return / Send Warning:",
                        options=active_only,
                        format_func=lambda x: f"Issue #{x['issue_id']} - {x['borrower_name']} holding '{x['book_title']}' (Due: {x['due_date']} | Status: {x['loan_status']})"
                    )

                with act_col2:
                    st.write("")
                    st.write("")
                    sub_col1, sub_col2 = st.columns(2)
                    with sub_col1:
                        if st.button("📥 Quick Return Book", type="primary", use_container_width=True):
                            ok, ret_res = call_procedure("sp_return_book", (sel_borrower_record["issue_id"], "Good"))
                            if ok:
                                send_return_receipt(
                                    sel_borrower_record["member_id"],
                                    sel_borrower_record["borrower_name"],
                                    sel_borrower_record["borrower_email"],
                                    sel_borrower_record["book_title"],
                                    sel_borrower_record["barcode"],
                                    float(sel_borrower_record["fine_amount"]),
                                    "Good"
                                )
                                st.success(f"🎉 Book '{sel_borrower_record['book_title']}' returned by {sel_borrower_record['borrower_name']}!")
                                st.rerun()
                            else:
                                st.error(f"Failed to return: {ret_res}")

                    with sub_col2:
                        if st.button("📧 Email Due/Late Notice", use_container_width=True):
                            send_overdue_warning(
                                member_id=sel_borrower_record["member_id"],
                                member_name=sel_borrower_record["borrower_name"],
                                email=sel_borrower_record["borrower_email"],
                                book_title=sel_borrower_record["book_title"],
                                due_date=sel_borrower_record["due_date"],
                                accrued_fine=float(sel_borrower_record["fine_amount"]),
                                issue_id=sel_borrower_record["issue_id"],
                                days_overdue=int(sel_borrower_record["days_overdue"])
                            )
                            st.success(f"Notification email dispatched to {sel_borrower_record['borrower_email']}!")
            else:
                st.info("No active borrowers needing follow-up under current filter.")

            # CSV Export
            csv_data = df_disp.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Export Circulation & Borrowers Report (CSV)",
                data=csv_data,
                file_name=f"library_borrowers_{date.today()}.csv",
                mime="text/csv"
            )

    # =========================================================================
    # TAB 2: ADD NEW BOOKS (MANUAL + SMART API AUTOFILL)
    # =========================================================================
    with tabs[1]:
        st.subheader("➕ Add Books to Library Catalog")
        st.caption("Admins can quickly add books manually or use the Open Library API to auto-fill book details in 1 click!")

        add_mode = st.radio(
            "Select Book Addition Method:",
            ["✍️ Manual Entry Form", "⚡ Smart API Auto-Fill (Search by Title or ISBN)"],
            horizontal=True
        )

        # Pre-load metadata for selectors
        existing_categories = execute_query("SELECT category_id, name FROM categories ORDER BY name ASC")
        existing_publishers = execute_query("SELECT publisher_id, name FROM publishers ORDER BY name ASC")
        existing_authors = execute_query("SELECT author_id, name FROM authors ORDER BY name ASC")

        # SMART API AUTOFILL MODE
        autofill_title = ""
        autofill_isbn = ""
        autofill_year = 2024
        autofill_author = ""
        autofill_publisher = ""

        if add_mode == "⚡ Smart API Auto-Fill (Search by Title or ISBN)":
            st.markdown(
                """
                <div style="padding: 12px 16px; background: #eef2ff; border-left: 4px solid #6366f1; border-radius: 8px; margin-bottom: 16px; color: #1e1b4b;">
                    <strong style="color: #312e81;">💡 Instant E-Book & Catalog Finder:</strong> <span style="color: #3730a3;">Search any book from Open Library's millions of academic records to instantly populate title, author, publisher, publication year, and ISBN!</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_api_s, col_api_b = st.columns([3, 1])
            with col_api_s:
                api_query = st.text_input("Enter Title, Topic, or ISBN to lookup:", placeholder="e.g. Clean Code, Python, Artificial Intelligence, 978-0132350884")
            with col_api_b:
                st.write("")
                st.write("")
                search_api_btn = st.button("🔎 Fetch from API", type="primary", use_container_width=True)

            if api_query:
                api_matches = search_openlibrary_api(api_query, limit=5)
                if api_matches:
                    st.markdown("##### 📚 Matching Books Found in Public Catalog:")
                    for idx, item in enumerate(api_matches):
                        with st.container():
                            c_img, c_info, c_btn = st.columns([1, 4, 1.5])
                            with c_img:
                                if item.get("cover_url"):
                                    st.image(item["cover_url"], width=80)
                                else:
                                    st.markdown("📖 *No Cover*")
                            with c_info:
                                st.markdown(f"**{item['title']}**")
                                st.caption(f"Author(s): {item['authors']} | Publisher: {item['publisher']} | Year: {item['year']} | ISBN: `{item['isbn'] or 'N/A'}`")
                            with c_btn:
                                if st.button("📥 Use This Book", key=f"sel_api_{idx}", use_container_width=True):
                                    st.session_state["autofill_title"] = item["title"]
                                    st.session_state["autofill_isbn"] = item["isbn"] or f"978-AUTO-{datetime.now().strftime('%H%M%S')}"
                                    st.session_state["autofill_year"] = int(item["year"]) if str(item["year"]).isdigit() else 2024
                                    st.session_state["autofill_author"] = item["authors"]
                                    st.session_state["autofill_publisher"] = item["publisher"]
                                    st.success(f"Loaded '{item['title']}'! Review details below and click Save.")
                else:
                    st.warning("No matches found in API for that query. You can add it manually below.")

        # Shared Addition Form
        init_title = st.session_state.get("autofill_title", "")
        init_isbn = st.session_state.get("autofill_isbn", "")
        init_year = st.session_state.get("autofill_year", 2024)
        init_author_name = st.session_state.get("autofill_author", "")
        init_pub_name = st.session_state.get("autofill_publisher", "")

        st.markdown("##### 📝 Book Specification Details")
        with st.form("admin_add_book_master_form", clear_on_submit=False):
            f1, f2 = st.columns(2)
            with f1:
                form_title = st.text_input("Book Title *", value=init_title, placeholder="e.g. Design Patterns: Elements of Reusable Object-Oriented Software")
                form_isbn = st.text_input("ISBN (International Standard Book Number) *", value=init_isbn, placeholder="e.g. 978-0201633610")
                form_edition = st.text_input("Edition", value="1st")
                form_year = st.number_input("Publication Year", min_value=1800, max_value=2030, value=init_year)
                form_price = st.number_input("Unit Price ($)", min_value=0.0, value=50.0, step=5.0)

            with f2:
                # Category selection or new
                cat_names = [c["name"] for c in existing_categories]
                form_cat = st.selectbox("Category *", options=cat_names if cat_names else ["Computer Science"])
                new_cat_custom = st.text_input("Or create New Category (leave blank if selecting above):", "")

                # Publisher selection or new
                pub_names = [p["name"] for p in existing_publishers]
                form_pub = st.selectbox("Publisher *", options=pub_names if pub_names else ["Pearson"])
                new_pub_custom = st.text_input("Or create New Publisher (leave blank if selecting above):", value=init_pub_name if init_pub_name and init_pub_name not in pub_names else "")

                # Authors selection or new
                auth_names = [a["name"] for a in existing_authors]
                form_authors = st.multiselect("Select Authors *", options=auth_names)
                new_author_custom = st.text_input("Or add New Author (leave blank if selected above):", value=init_author_name if init_author_name and init_author_name not in auth_names else "")

                form_language = st.text_input("Language", value="English")

            st.markdown("##### 🏷️ Automatic Physical Copies Creation")
            st.caption("The system will immediately generate physical copies with unique barcodes for circulation.")
            cp_col1, cp_col2 = st.columns(2)
            with cp_col1:
                num_copies_to_create = st.number_input("Number of Physical Copies to Add to Shelf *", min_value=1, max_value=50, value=3)
            with cp_col2:
                shelf_location = st.text_input("Shelf Location Code", value="Stack A - Shelf 101")

            save_submitted = st.form_submit_button("🚀 Add Book & Generate Copies", type="primary", use_container_width=True)

            if save_submitted:
                if not form_title.strip() or not form_isbn.strip():
                    st.error("Please provide both Book Title and ISBN.")
                else:
                    try:
                        # 1. Handle Category
                        cat_id = None
                        if new_cat_custom.strip():
                            existing_c = execute_query("SELECT category_id FROM categories WHERE name = %s", (new_cat_custom.strip(),), fetchone=True)
                            if existing_c:
                                cat_id = existing_c["category_id"]
                            else:
                                _, cat_id = execute_non_query("INSERT INTO categories (name) VALUES (%s)", (new_cat_custom.strip(),))
                        else:
                            for c in existing_categories:
                                if c["name"] == form_cat:
                                    cat_id = c["category_id"]
                                    break

                        # 2. Handle Publisher
                        pub_id = None
                        target_pub_name = new_pub_custom.strip() if new_pub_custom.strip() else form_pub
                        existing_p = execute_query("SELECT publisher_id FROM publishers WHERE name = %s", (target_pub_name,), fetchone=True)
                        if existing_p:
                            pub_id = existing_p["publisher_id"]
                        else:
                            _, pub_id = execute_non_query("INSERT INTO publishers (name) VALUES (%s)", (target_pub_name,))

                        # 3. Handle Authors
                        chosen_author_ids = []
                        for a in existing_authors:
                            if a["name"] in form_authors:
                                chosen_author_ids.append(a["author_id"])

                        if new_author_custom.strip():
                            existing_a = execute_query("SELECT author_id FROM authors WHERE name = %s", (new_author_custom.strip(),), fetchone=True)
                            if existing_a:
                                if existing_a["author_id"] not in chosen_author_ids:
                                    chosen_author_ids.append(existing_a["author_id"])
                            else:
                                _, new_a_id = execute_non_query("INSERT INTO authors (name) VALUES (%s)", (new_author_custom.strip(),))
                                chosen_author_ids.append(new_a_id)

                        if not chosen_author_ids:
                            # Default fallback author
                            fallback_a = execute_query("SELECT author_id FROM authors LIMIT 1", fetchone=True)
                            if fallback_a:
                                chosen_author_ids.append(fallback_a["author_id"])

                        # 4. Insert into Books
                        ins_book_sql = """
                            INSERT INTO books (isbn, title, publisher_id, category_id, publication_year, edition, language, price)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        _, new_book_id = execute_non_query(ins_book_sql, (
                            form_isbn.strip(),
                            form_title.strip(),
                            pub_id,
                            cat_id,
                            int(form_year),
                            form_edition.strip(),
                            form_language.strip(),
                            float(form_price)
                        ))

                        # 5. Link Authors
                        for aid in chosen_author_ids:
                            execute_non_query("INSERT IGNORE INTO book_authors (book_id, author_id) VALUES (%s, %s)", (new_book_id, aid))

                        # 6. Generate Physical Copies
                        created_barcodes = []
                        for i in range(1, int(num_copies_to_create) + 1):
                            barcode = f"BC-{new_book_id}-{i:02d}-{datetime.now().strftime('%M%S')}"
                            execute_non_query(
                                "INSERT INTO book_copies (book_id, barcode, shelf_location, status, acquired_on) VALUES (%s, %s, %s, 'Available', CURDATE())",
                                (new_book_id, barcode, shelf_location.strip())
                            )
                            created_barcodes.append(barcode)

                        st.success(f"🎉 Successfully added '{form_title}' (Book ID: {new_book_id}) with {num_copies_to_create} physical copies!")
                        st.info(f"Generated Barcodes: {', '.join(created_barcodes)}")
                        
                        # Clear autofill session
                        if "autofill_title" in st.session_state:
                            del st.session_state["autofill_title"]
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error adding book: {str(e)}")

    # =========================================================================
    # TAB 3: BOOK CATALOG & COPIES INVENTORY
    # =========================================================================
    with tabs[2]:
        st.subheader("📚 Library Catalog & Inventory Oversight")

        c_search, c_add_copy_toggle = st.columns([3, 1])
        with c_search:
            cat_query = st.text_input("Search Catalog:", placeholder="Filter by Title, ISBN, Author, or Category...")
        with c_add_copy_toggle:
            open_add_copy = st.checkbox("➕ Add Copies to Existing Book", value=False)

        if open_add_copy:
            with st.expander("🏷️ Add Extra Physical Copies to Existing Title", expanded=True):
                with st.form("admin_add_extra_copy_form", clear_on_submit=True):
                    all_books = execute_query("SELECT book_id, title, isbn FROM books ORDER BY title ASC")
                    ec_c1, ec_c2 = st.columns(2)
                    with ec_c1:
                        target_b = st.selectbox("Select Book *", options=all_books, format_func=lambda b: f"{b['title']} (ISBN: {b['isbn']})")
                        shelf_loc = st.text_input("Shelf Location", value="Main Stack - Shelf 204")
                    with ec_c2:
                        copies_count = st.number_input("Number of Copies to Add", min_value=1, max_value=20, value=1)
                        custom_barcode = st.text_input("Custom Barcode Prefix (Optional)", value=f"BC-{target_b['book_id'] if target_b else 1}")

                    if st.form_submit_button("Generate & Add Physical Copies", type="primary", use_container_width=True):
                        try:
                            for idx in range(copies_count):
                                bc = f"{custom_barcode}-{idx+1}-{datetime.now().strftime('%S%f')[:4]}"
                                execute_non_query(
                                    "INSERT INTO book_copies (book_id, barcode, shelf_location, status, acquired_on) VALUES (%s, %s, %s, 'Available', CURDATE())",
                                    (target_b["book_id"], bc, shelf_loc.strip())
                                )
                            st.success(f"Added {copies_count} copies for '{target_b['title']}'!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

        # Catalog Query
        cat_sql = """
            SELECT 
                b.book_id,
                b.title,
                GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') AS authors,
                c.name AS category,
                p.name AS publisher,
                b.isbn,
                b.publication_year,
                b.price,
                COUNT(DISTINCT cp.copy_id) AS total_copies,
                SUM(CASE WHEN cp.status = 'Available' THEN 1 ELSE 0 END) AS available_copies,
                SUM(CASE WHEN cp.status = 'Issued' THEN 1 ELSE 0 END) AS issued_copies
            FROM books b
            LEFT JOIN book_authors ba ON ba.book_id = b.book_id
            LEFT JOIN authors a ON a.author_id = ba.author_id
            LEFT JOIN categories c ON c.category_id = b.category_id
            LEFT JOIN publishers p ON p.publisher_id = b.publisher_id
            LEFT JOIN book_copies cp ON cp.book_id = b.book_id
            WHERE 1=1
        """
        c_params = []
        if cat_query.strip():
            cq = f"%{cat_query.strip()}%"
            cat_sql += " AND (b.title LIKE %s OR b.isbn LIKE %s OR a.name LIKE %s OR c.name LIKE %s)"
            c_params.extend([cq, cq, cq, cq])

        cat_sql += " GROUP BY b.book_id ORDER BY b.title ASC"
        catalog_rows = execute_query(cat_sql, c_params)

        if catalog_rows:
            df_cat = pd.DataFrame(catalog_rows)
            st.dataframe(df_cat, use_container_width=True)
        else:
            st.info("No books match query.")

    # =========================================================================
    # TAB 4: QUICK CIRCULATION DESK
    # =========================================================================
    with tabs[3]:
        st.subheader("⚡ Quick Issue & Return Counter")
        cir_c1, cir_c2 = st.columns(2)

        with cir_c1:
            st.markdown("##### 📤 Issue Physical Book to Student")
            members_list = execute_query("SELECT member_id, full_name, email FROM members WHERE status = 'Active' ORDER BY full_name")
            copies_avail = execute_query("""
                SELECT c.copy_id, c.barcode, b.title, c.shelf_location 
                FROM book_copies c 
                JOIN books b ON b.book_id = c.book_id 
                WHERE c.status = 'Available' 
                ORDER BY b.title ASC
            """)

            with st.form("admin_issue_book_form"):
                sel_m = st.selectbox("Select Student / Member *", options=members_list, format_func=lambda m: f"{m['full_name']} (#{m['member_id']} - {m['email']})")
                sel_c = st.selectbox("Select Available Copy *", options=copies_avail, format_func=lambda c: f"'{c['title']}' | Barcode: {c['barcode']}")
                submit_iss = st.form_submit_button("Confirm Issue / Checkout", type="primary", use_container_width=True)

                if submit_iss and sel_m and sel_c:
                    ok, res = call_procedure("sp_issue_book", (sel_m["member_id"], sel_c["copy_id"]))
                    if ok:
                        send_issue_confirmation(
                            sel_m["member_id"],
                            sel_m["full_name"],
                            sel_m["email"],
                            sel_c["title"],
                            sel_c["barcode"],
                            "14 days from today"
                        )
                        st.success(f"Issued '{sel_c['title']}' to {sel_m['full_name']}!")
                        st.rerun()
                    else:
                        st.error(f"Cannot issue: {res}")

        with cir_c2:
            st.markdown("##### 📥 Check-In / Return Book")
            active_issues = execute_query("""
                SELECT i.issue_id, m.member_id, m.full_name, m.email, b.title, c.barcode, i.due_date,
                       fn_calc_fine(i.due_date, CURDATE()) as fine
                FROM issues i
                JOIN members m ON m.member_id = i.member_id
                JOIN book_copies c ON c.copy_id = i.copy_id
                JOIN books b ON b.book_id = c.book_id
                WHERE i.return_date IS NULL
                ORDER BY i.due_date ASC
            """)

            with st.form("admin_return_book_form"):
                if not active_issues:
                    st.info("No active loans out.")
                    st.form_submit_button("No Loans", disabled=True)
                else:
                    sel_ret = st.selectbox(
                        "Select Loan to Check-in *",
                        options=active_issues,
                        format_func=lambda x: f"Issue #{x['issue_id']} - {x['full_name']} ('{x['title']}' | Due: {x['due_date']} | Fine: ${float(x['fine']):.2f})"
                    )
                    cond = st.selectbox("Return Physical Condition", ["Good", "Damaged", "Lost"])
                    submit_ret = st.form_submit_button("Process Check-In", type="primary", use_container_width=True)

                    if submit_ret and sel_ret:
                        ok, ret_res = call_procedure("sp_return_book", (sel_ret["issue_id"], cond))
                        if ok:
                            send_return_receipt(
                                sel_ret["member_id"],
                                sel_ret["full_name"],
                                sel_ret["email"],
                                sel_ret["title"],
                                sel_ret["barcode"],
                                float(sel_ret["fine"]),
                                cond
                            )
                            st.success(f"Returned '{sel_ret['title']}' from {sel_ret['full_name']}!")
                            st.rerun()
                        else:
                            st.error(f"Return failed: {ret_res}")

    # =========================================================================
    # TAB 5: DIGITAL E-BOOKS PREVIEW & CURATION
    # =========================================================================
    with tabs[4]:
        st.subheader("🌐 Digital E-Books Administration & Repository")
        st.caption("Manage digital textbooks, track reading metrics, upload or publish new e-books, and curate materials from Open Library.")

        adm_eb_subtabs = st.tabs(["📚 Stored E-Books Collection", "➕ Publish New E-Book", "⚡ Import from Open Library API"])

        # SUB-TAB 1: STORED E-BOOKS
        with adm_eb_subtabs[0]:
            st.markdown("##### 📚 E-Books Stored in MySQL Database")
            db_ebs = get_db_ebooks()

            if not db_ebs:
                st.info("No e-books currently stored in database.")
            else:
                st.markdown(f"**Total E-Books:** {len(db_ebs)} titles")
                df_eb = pd.DataFrame(db_ebs)
                cols_show = ["ebook_id", "title", "author", "category", "publication_year", "format", "file_size", "views_count", "downloads_count", "added_by"]
                st.dataframe(df_eb[cols_show], use_container_width=True)

                st.write("")
                st.markdown("##### ⚡ Quick E-Book Management")
                eb_del_c1, eb_del_c2 = st.columns([3, 1])
                with eb_del_c1:
                    sel_del_eb = st.selectbox(
                        "Select E-Book to Inspect / Delete:",
                        options=db_ebs,
                        format_func=lambda x: f"#{x['ebook_id']} - {x['title']} (by {x['author']} | Reads: {x['views_count']})"
                    )
                with eb_del_c2:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Delete E-Book", type="secondary", use_container_width=True):
                        if sel_del_eb:
                            delete_ebook_from_db(sel_del_eb["ebook_id"])
                            st.success(f"Deleted '{sel_del_eb['title']}'!")
                            st.rerun()

        # SUB-TAB 2: PUBLISH NEW E-BOOK
        with adm_eb_subtabs[1]:
            st.markdown("##### ➕ Publish Digital E-Book to Repository")
            with st.form("admin_publish_ebook_form"):
                eb_c1, eb_c2 = st.columns(2)
                with eb_c1:
                    a_eb_title = st.text_input("E-Book Title *", placeholder="e.g. Distributed Systems: Concepts and Design")
                    a_eb_author = st.text_input("Author(s) *", placeholder="e.g. George Coulouris, Jean Dollimore")
                    a_eb_cat = st.selectbox("Category *", [
                        "Computer Science", "Artificial Intelligence", "Physics & Science",
                        "Philosophy", "Literature", "Mathematics", "Engineering", "Business & Economics"
                    ])
                    a_eb_year = st.text_input("Publication Year", value="2024")
                    a_eb_isbn = st.text_input("Digital ISBN / Identifier", placeholder="e.g. 978-0132143011")

                with eb_c2:
                    a_eb_format = st.selectbox("Format", ["PDF / Online", "EPUB / Text", "HTML / Web", "Interactive Textbook"])
                    a_eb_size = st.text_input("File Size", value="5.2 MB")
                    a_eb_read = st.text_input("Read Online URL *", placeholder="https://openlibrary.org or direct reading URL")
                    a_eb_down = st.text_input("Direct Download URL (PDF / EPUB)", placeholder="https://.../book.pdf")
                    a_eb_cover = st.text_input("Cover Image URL", placeholder="https://images.unsplash.com/... or leave blank")

                a_eb_desc = st.text_area("Description & Synopsis", placeholder="Overview of book contents and learning objectives...", height=90)
                a_eb_sample = st.text_area("Chapter 1 Preview / Sample Text (Markdown Supported)", placeholder="# Chapter 1: Introduction\n\nPreview text for reader...", height=130)

                sub_a_eb = st.form_submit_button("💾 Publish E-Book to Database", type="primary", use_container_width=True)
                if sub_a_eb:
                    ok_a, msg_a = add_ebook_to_db(
                        title=a_eb_title,
                        author=a_eb_author,
                        category=a_eb_cat,
                        publication_year=a_eb_year,
                        isbn=a_eb_isbn,
                        cover_url=a_eb_cover,
                        read_url=a_eb_read,
                        download_url=a_eb_down,
                        format_type=a_eb_format,
                        file_size=a_eb_size,
                        description=a_eb_desc,
                        content_preview=a_eb_sample,
                        added_by=f"Admin (@{user_info.get('username')})"
                    )
                    if ok_a:
                        st.success(f"🎉 {msg_a}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg_a}")

        # SUB-TAB 3: IMPORT FROM API
        with adm_eb_subtabs[2]:
            st.markdown("##### ⚡ Search Open Library & 1-Click Import")
            api_q = st.text_input("Search Open Library Repository:", placeholder="Search title, author, or subject (e.g. Algorithms, Physics, Philosophy)...", key="admin_eb_search")
            if api_q:
                eb_results = search_openlibrary_api(api_q, limit=6)
                st.markdown(f"Found {len(eb_results)} e-books from Open Library:")
                for b in eb_results:
                    with st.expander(f"📖 {b['title']} — by {b['authors']} ({b['year']})"):
                        c_eb1, c_eb2, c_eb3 = st.columns([1, 3, 1.5])
                        with c_eb1:
                            if b["cover_url"]:
                                st.image(b["cover_url"], width=80)
                        with c_eb2:
                            st.write(f"**Publisher:** {b['publisher']}")
                            st.write(f"**ISBN:** `{b['isbn'] or 'N/A'}`")
                            st.write(f"**Subjects:** {', '.join(b['subjects_list'])}")
                            st.markdown(f"[🔗 Open in Open Library Reader]({b['read_url']})")
                        with c_eb3:
                            if st.button("📥 Import into MySQL", key=f"adm_imp_{b['id']}", use_container_width=True):
                                ok_imp, msg_imp = add_ebook_to_db(
                                    title=b["title"],
                                    author=b["authors"],
                                    category=b.get("subject", "General"),
                                    publication_year=str(b.get("year", "2024")),
                                    isbn=b.get("isbn", ""),
                                    cover_url=b.get("cover_url", ""),
                                    read_url=b.get("read_url", ""),
                                    download_url=b.get("archive_url", ""),
                                    format_type="PDF / Web",
                                    file_size="4.0 MB",
                                    description=b.get("description", ""),
                                    content_preview="",
                                    added_by=f"Admin (@{user_info.get('username')})"
                                )
                                if ok_imp:
                                    st.success("Imported to Library Collection!")
                                    st.rerun()

    # =========================================================================
    # TAB 6: MEMBER & USER ACCOUNT MANAGEMENT
    # =========================================================================
    with tabs[5]:
        st.subheader("👤 User & Member Account Management")
        st.caption("Manage existing student borrowers and administrative staff, register new accounts directly into MySQL, or reset account passwords.")

        u_subtabs = st.tabs(["👥 Registered Accounts in Database", "➕ Create New User / Admin Account", "🔑 Reset User Password"])

        # SUB-TAB 1: REGISTERED ACCOUNTS
        with u_subtabs[0]:
            st.markdown("##### 👥 All User Accounts in MySQL Database")
            users_list = get_all_system_users()
            if users_list:
                total_u = len(users_list)
                total_stu = sum(1 for u in users_list if u.get("role") == "student")
                total_adm = total_u - total_stu

                mc1, mc2, mc3 = st.columns(3)
                mc1.metric("Total Registered Users", total_u)
                mc2.metric("Student Borrowers", total_stu)
                mc3.metric("Staff / Administrators", total_adm)

                st.write("")
                filter_user = st.text_input("🔍 Filter by Username, Name, Role, or Email:", placeholder="Type to search...", key="filter_admin_users")

                df_users = pd.DataFrame(users_list)
                if filter_user:
                    q = filter_user.lower()
                    mask = (
                        df_users["username"].astype(str).str.lower().str.contains(q) |
                        df_users["full_name"].astype(str).str.lower().str.contains(q) |
                        df_users["email"].astype(str).str.lower().str.contains(q) |
                        df_users["role"].astype(str).str.lower().str.contains(q)
                    )
                    df_users = df_users[mask]

                cols_display = ["user_id", "username", "role", "full_name", "email", "phone", "member_type", "member_status", "created_at"]
                cols_existing = [c for c in cols_display if c in df_users.columns]
                st.dataframe(df_users[cols_existing], use_container_width=True)
            else:
                st.info("No registered users found in the database.")

        # SUB-TAB 2: REGISTER NEW USER DIRECTLY
        with u_subtabs[1]:
            st.markdown("##### ➕ Create New Account (Stored in MySQL)")
            st.caption("Admin tool to manually onboard new Students, Librarians, or Administrators into the database.")
            with st.form("admin_create_user_form", clear_on_submit=False):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    new_u_role = st.selectbox(
                        "Role / Privilege Level *",
                        ["student", "admin", "librarian"],
                        format_func=lambda x: "🎓 Student" if x == "student" else ("🛡️ Administrator" if x == "admin" else "👑 Librarian")
                    )
                    new_u_name = st.text_input("Full Name *", placeholder="e.g. Ananya Rao")
                    new_u_uname = st.text_input("Username *", placeholder="e.g. ananya_admin")
                with col_u2:
                    new_u_email = st.text_input("Email Address *", placeholder="e.g. ananya@college.edu")
                    new_u_phone = st.text_input("Phone Number", placeholder="e.g. 9876543210")
                    new_u_dept = st.text_input("Department / Address", placeholder="e.g. Information Technology")

                col_u3, col_u4 = st.columns(2)
                with col_u3:
                    new_u_pwd = st.text_input("Password *", type="password", placeholder="Minimum 4 characters")
                with col_u4:
                    new_u_pwd2 = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password")

                btn_create_u = st.form_submit_button("Save User Account to Database", type="primary", use_container_width=True)

                if btn_create_u:
                    if new_u_pwd != new_u_pwd2:
                        st.error("❌ Passwords do not match. Please verify your entry.")
                    else:
                        ok_cr, res_cr = register_user(
                            username=new_u_uname,
                            password=new_u_pwd,
                            full_name=new_u_name,
                            email=new_u_email,
                            role=new_u_role,
                            phone=new_u_phone,
                            address=new_u_dept
                        )
                        if ok_cr:
                            st.success(f"🎉 Successfully created {new_u_role.upper()} account '@{new_u_uname}'! Record stored in MySQL database with Member ID #{res_cr['member_id']}.")
                            st.rerun()
                        else:
                            st.error(f"❌ {res_cr}")

        # SUB-TAB 3: RESET USER PASSWORD
        with u_subtabs[2]:
            st.markdown("##### 🔑 Reset or Update Any Account's Password")
            st.caption("Quickly fix forgotten passwords for any student or staff member directly in the MySQL database.")
            with st.form("admin_reset_user_pwd_form"):
                all_u = get_all_system_users()
                u_opts = [f"{u['username']} ({u['role'].upper()} - {u.get('full_name') or 'N/A'})" for u in all_u]
                
                sel_u_str = st.selectbox("Select Account to Reset:", options=u_opts if u_opts else ["No users"])
                adm_new_pwd = st.text_input("Set New Password *", type="password", placeholder="Minimum 4 characters")
                btn_adm_set_pwd = st.form_submit_button("Update Password in MySQL", type="primary", use_container_width=True)

                if btn_adm_set_pwd:
                    if not sel_u_str or sel_u_str == "No users":
                        st.error("❌ No account selected.")
                    else:
                        target_username = sel_u_str.split(" ")[0]
                        ok_p, msg_p = reset_user_password(target_username, adm_new_pwd)
                        if ok_p:
                            st.success(f"✅ {msg_p}")
                        else:
                            st.error(f"❌ {msg_p}")

    # =========================================================================
    # TAB 7: SYSTEM MAINTENANCE
    # =========================================================================
    with tabs[6]:
        st.subheader("⚙️ System Health & Overdue Batch Execution")
        st.caption("Trigger daily automated maintenance routines, calculate fines, and inspect system integrity.")

        sm_c1, sm_c2 = st.columns(2)
        with sm_c1:
            if st.button("🚀 Run Daily Maintenance (Fine Recalculation)", use_container_width=True, type="primary"):
                ok, msg = run_maintenance()
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

        with sm_c2:
            if st.button("📢 Broadcast Email Notices to All Overdue Borrowers", use_container_width=True):
                res = send_all_overdue_reminders()
                st.success(f"Sent notifications to {res['count']} overdue borrowers! (Total fines billed: ${res['total_fines']:.2f})")
