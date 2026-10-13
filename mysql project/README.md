# 📚 Digital Library and Book Circulation System

A production-grade, MySQL-backed Digital Library and Book Circulation System built with **Python**, **MySQL 8.0**, **Streamlit**, **Plotly**, and **Email Notifications**.

---

## 🌟 Key Features & Uniqueness

1. **Physical Book Copy Tracking**  
   Tracks each physical copy individually with distinct barcodes, shelf locations, and real-time statuses (`Available`, `Issued`, `Reserved`, `Lost`, `Damaged`).

2. **Automated Circulation Desk (Issue & Return)**  
   - Direct integration with MySQL stored procedures (`sp_issue_book`, `sp_return_book`).
   - Automatically checks member borrowing limits, suspensions, and unpaid fine caps before issuing books.
   - Automatically marks physical copy availability upon return.

3. **Smart Book Reservations**  
   - Members can reserve books that currently have zero available physical copies.
   - When a borrowed copy is returned, the system automatically marks the reservation as `Ready` and holds the physical copy for the reserving member!

4. **Automated Overdue Fines Calculation**  
   - Calculates daily overdue fines dynamically using MySQL stored function `fn_calc_fine(due_date, return_date)`.
   - Supports condition-based penalty assessment (`Damaged`, `Lost`) and fine settlement (`sp_settle_fine`).

5. **Role-Based Authentication & Portals**  
   - **Admin Master Dashboard**:
     - 👥 **"Who Took The Books" Live Borrower Tracker**: Complete visibility into all active borrowers holding books, overdue statuses, contact info (email/phone), days overdue, fine amounts, and 1-click notice emails or return processing.
     - ➕ **Add Books & Smart Auto-Fill**: Add books manually with auto-generated physical copies/barcodes, or use the integrated Open Library API to auto-fill book titles, authors, publishers, and ISBN in 1 click!
   - **Chief Librarian Portal**: Full administration of Catalog, Physical Copies, Members, Circulation Desk, Fines, Reservations, Analytics, and Notifications.
   - **Student / Member Portal**:
     - 👥 **"Who Took The Books" Live Borrower Tracker**: Real-time transparency to see who borrowed books, barcodes, due dates, and 1-click reservation holds.
     - ➕ **Add Books & E-Books**: 1-Click Open Library API search/auto-fill + manual entry with auto-generated barcode copies, plus digital e-book publishing.
     - 📱 **Digital E-Books Library**: In-browser reader (Daylight, Dark Mode, Sepia), persistent study notes saved to MySQL, and free downloads.
     - 📖 **Physical Catalog & Borrowing**: Instant checkouts, automated overdue tracking, and queue reservations.
     - 🪪 **Digital Library Card Pass**: Real-time student membership badge and credentials.
   - **Student Self-Registration**: Direct registration form saving member and user credentials transactionally into MySQL.

6. **Student E-Books & Digital Study Center (Public APIs)**  
   - Integrated with **Open Library API** and **Project Gutenberg (Gutendex)**.
   - Students can search over 70,000+ digital books across Computer Science, Science, Math, Literature, and Philosophy.
   - **In-App Reader Workspace**: Read full texts inside the portal with customizable themes (Daylight, Dark Mode, Warm Sepia) and adjustable font sizes.
   - **Personal Study Notes**: Students can take notes while reading, persistently saved directly into the MySQL database (`student_study_notes`).
   - **Pomodoro Study Timer**: Built-in 25-minute focus sprints for students.

7. **Interactive Visual Analytics (Plotly)**  
   - Top 10 Most Borrowed Books with unique readers count.
   - Physical Copy Status breakdown (Available vs Issued vs Reserved vs Lost/Damaged).
   - Catalog Volume distribution by Category (Donut chart).
   - Circulation trends and borrowing volume over time.

8. **Email Notification Engine**  
   - Sends rich HTML receipts and warnings:
     - 📖 Book Issue Confirmation (with barcode and due date).
     - 📥 Book Return Receipt & condition inspection.
     - ⚠️ Urgent Overdue Warning Notices.
     - 📌 Reservation Ready for Pickup Notices.
   - All notifications are persisted directly into the MySQL `notifications` table.
   - Operates in both Simulated Mode (instant database logging) and Live SMTP mode (Gmail/Outlook).

---

## 🏗️ MySQL Architecture & Database Objects

### 🗄️ Tables
- `publishers`: Publishing houses and contacts
- `categories`: Book genres and classifications
- `authors`: Author catalog and biographies
- `books`: Master book titles, ISBNs, prices, and publication details
- `book_authors`: Many-to-many relationship linking books to multiple authors
- `book_copies`: Individual physical items with unique barcodes and shelf coordinates
- `members`: Registered library members (Students, Faculty, Public)
- `users`: User authentication credentials with SHA-256 hashed passwords and roles
- `issues`: Issue transactions, due dates, return dates, and physical return conditions
- `reservations`: Book hold requests with priority timestamps and hold windows
- `fines`: Financial penalty ledger for overdue, lost, or damaged books
- `notifications`: Complete audit log of all email alerts and communication status
- `settings`: Configurable system policies (daily fine rate, loan days, max loans, etc.)

### ⚙️ Stored Procedures & Functions
- `sp_issue_book(p_member, p_copy)`: Executes transactional checkout, checks limits, and updates copy status.
- `sp_return_book(p_issue, p_condition)`: Processes check-in, calculates overdue fines, inspects condition, and assigns returned copy to pending reservations.
- `sp_reserve_book(p_member, p_book)`: Validates eligibility and records reservations.
- `sp_cancel_reservation(p_res)`: Cancels reservations and releases held copies back to general circulation.
- `sp_settle_fine(p_fine, p_action)`: Marks fines as `Paid` or `Waived`.
- `sp_daily_maintenance()`: Updates overdue statuses and queues reminder notices.
- `sp_expire_reservations()`: Releases unclaimed holds after the reservation window expires.
- `fn_calc_fine(p_due, p_returned)`: Dynamic daily overdue penalty calculation.
- `fn_available_copies(p_book)`: Count of ready-to-borrow physical copies for a title.
- `fn_member_active_loans(p_member)`: Count of currently borrowed books by member.
- `fn_member_unpaid_fines(p_member)`: Total unpaid penalty balance for a member.

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.10+
- MySQL Server 8.0+

### 2. Configure Environment (`.env`)
The database connection settings are configured in `.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=digital_library

EMAIL_SIMULATION_MODE=True
```

### 3. Database Setup (If initializing a new server)
The repository contains the complete schema and seed data in `schema.sql`:
```bash
mysql -u root -p < schema.sql
```

### 4. Run the Application
Activate the virtual environment and start Streamlit:
```bash
# On Windows:
.venv\Scripts\streamlit run app.py
```
Open your browser at: `http://localhost:8501`

---

## 🔑 Default Credentials for Testing

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Librarian** | `librarian` | `admin123` | Full Administrative & Circulation Access |
| **Administrator** | `admin` | `admin123` | Full Administrative Access |
| **Student** | `aarav` | `student123` | Active student with borrowed books & history |
| **Student** | `diya` | `student123` | Student member |
| **Student** | `abc` | `student123` | Student member |
| **New Student** | *(Self-Register)* | *(Your choice)* | Register using the "Student Registration" tab |

---

## 📁 Project Directory Structure
```
d:/mysql project/
├── .env                  # MySQL and Email configuration
├── .env.example          # Environment variables template
├── app.py                # Main Streamlit web application & router
├── auth.py               # Authentication, SHA-256 password hashing & registration
├── database.py           # MySQL connection pool, query execution & stored routines
├── email_service.py      # Email notification engine with HTML templates & DB logging
├── analytics.py          # Interactive Plotly visualizations and dashboards
├── requirements.txt      # Python dependencies
├── schema.sql            # Complete MySQL DDL, stored procedures, triggers & seed data
├── views/
│   ├── login_view.py     # Login, registration, and 1-click demo login screen
│   ├── librarian_view.py # Administrative & circulation management portal
│   └── student_view.py   # Student member self-service portal & digital library card
└── README.md             # Project documentation
```
