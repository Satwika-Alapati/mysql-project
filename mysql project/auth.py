"""
Authentication and User Management Module.
Supports role-based login (Librarian, Student) and Student registration.
Uses SHA-256 password hashing matching MySQL SHA2(..., 256).
"""

import hashlib
from database import execute_query, execute_non_query, get_connection


def hash_password(password: str) -> str:
    """Return SHA-256 hexadecimal digest of password."""
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()


def verify_user(username: str, password: str):
    """
    Verify user credentials against users and members table.
    Returns (True, user_info) if valid, otherwise (False, detailed_error_message).
    Provides clear diagnostics if username is missing or password does not match.
    """
    if not username or not username.strip():
        return False, "Please enter your username."
    if not password or not password.strip():
        return False, "Please enter your password."

    clean_username = username.strip()
    pwd_hash = hash_password(password)

    # 1. Check if username exists in database (case-insensitive)
    existing_user_check = execute_query(
        "SELECT user_id, username, role FROM users WHERE LOWER(username) = LOWER(%s)",
        (clean_username,),
        fetchone=True
    )
    if not existing_user_check:
        return False, f"Username '{clean_username}' was not found in the database. Please check your spelling or register a new account."

    # 2. Check full credentials with password hash
    sql = """
        SELECT 
            u.user_id, 
            u.username, 
            u.role, 
            u.member_id,
            m.full_name,
            m.email,
            m.phone,
            m.address,
            m.member_type,
            m.status AS member_status,
            m.joined_on,
            m.expires_on
        FROM users u
        LEFT JOIN members m ON u.member_id = m.member_id
        WHERE LOWER(u.username) = LOWER(%s) AND u.password_hash = %s
    """
    row = execute_query(sql, (clean_username, pwd_hash), fetchone=True)

    if not row:
        return False, f"Incorrect password for username '{clean_username}'. If you forgot your password, please use the 'Reset / Update Password' tab."

    if row["role"] == "student" and row.get("member_status") == "Suspended":
        return False, "Your library membership is currently suspended. Please contact the librarian."

    # If librarian or admin has no full_name in members, format display name
    if not row.get("full_name"):
        if row["role"] == "admin":
            row["full_name"] = "System Administrator"
        elif row["role"] == "librarian":
            row["full_name"] = "Chief Librarian"
        else:
            row["full_name"] = row["username"]

    return True, row


def register_user(username: str, password: str, full_name: str, email: str, role: str = "student", phone: str = "", address: str = ""):
    """
    Register any new user (Admin, Librarian, or Student) and store all data persistently in MySQL.
    Creates records in both 'members' and 'users' tables transactionally.
    Returns (True, user_info) or (False, error_message).
    """
    username = username.strip()
    full_name = full_name.strip()
    email = email.strip()
    role = role.strip().lower()

    if role not in ["admin", "librarian", "student"]:
        role = "student"

    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if not password or len(password) < 4:
        return False, "Password must be at least 4 characters long."
    if not full_name:
        return False, "Please enter your full name."
    if not email or "@" not in email:
        return False, "Please enter a valid email address (e.g. user@example.com)."

    # Check for existing username (case-insensitive)
    existing_user = execute_query(
        "SELECT user_id, username FROM users WHERE LOWER(username) = LOWER(%s)",
        (username,),
        fetchone=True
    )
    if existing_user:
        return False, f"Username '{username}' is already registered in the database. Please choose a different username or log in."

    # Check for existing email in members (case-insensitive)
    existing_member = execute_query(
        "SELECT member_id, email FROM members WHERE LOWER(email) = LOWER(%s)",
        (email,),
        fetchone=True
    )
    if existing_member:
        return False, f"Email '{email}' is already registered with an existing library account."

    pwd_hash = hash_password(password)

    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # 1. Insert into members table
        # If student, member_type is Student. If admin/librarian, member_type is Faculty (Staff)
        member_type = "Student" if role == "student" else "Faculty"
        member_sql = """
            INSERT INTO members (full_name, email, phone, address, member_type, status, joined_on, expires_on)
            VALUES (%s, %s, %s, %s, %s, 'Active', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 2 YEAR))
        """
        cursor.execute(member_sql, (full_name, email, phone.strip(), address.strip(), member_type))
        new_member_id = cursor.lastrowid

        # 2. Insert into users table
        user_sql = """
            INSERT INTO users (username, password_hash, role, member_id)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(user_sql, (username, pwd_hash, role, new_member_id))
        new_user_id = cursor.lastrowid

        conn.commit()
        cursor.close()

        user_info = {
            "user_id": new_user_id,
            "username": username,
            "role": role,
            "member_id": new_member_id,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "address": address,
            "member_type": member_type,
            "member_status": "Active"
        }
        return True, user_info

    except Exception as e:
        conn.rollback()
        return False, f"Database registration failed: {str(e)}"
    finally:
        conn.close()


def register_student(username: str, password: str, full_name: str, email: str, phone: str = "", address: str = ""):
    """Convenience wrapper for registering a Student account."""
    return register_user(username, password, full_name, email, role="student", phone=phone, address=address)


def register_admin(username: str, password: str, full_name: str, email: str, role: str = "admin", phone: str = "", address: str = ""):
    """Convenience wrapper for registering an Administrator or Librarian account."""
    if role not in ["admin", "librarian"]:
        role = "admin"
    return register_user(username, password, full_name, email, role=role, phone=phone, address=address)


def reset_user_password(username: str, new_password: str):
    """
    Reset or update password for an existing username in the MySQL database.
    Returns (True, success_message) or (False, error_message).
    """
    username = username.strip()
    new_password = new_password.strip()

    if not username:
        return False, "Please enter your username."
    if not new_password or len(new_password) < 4:
        return False, "New password must be at least 4 characters long."

    # Check if user exists
    user_row = execute_query(
        "SELECT user_id, username, role FROM users WHERE LOWER(username) = LOWER(%s)",
        (username,),
        fetchone=True
    )
    if not user_row:
        return False, f"Username '{username}' was not found in the database. Please check your spelling."

    new_hash = hash_password(new_password)
    try:
        execute_non_query(
            "UPDATE users SET password_hash = %s WHERE LOWER(username) = LOWER(%s)",
            (new_hash, username)
        )
        return True, f"Password for '{user_row['username']}' ({user_row['role'].upper()}) was successfully updated in the database! You can now log in."
    except Exception as e:
        return False, f"Failed to update password: {str(e)}"


def get_all_system_users():
    """Retrieve all registered accounts across users and members table."""
    sql = """
        SELECT 
            u.user_id,
            u.username,
            u.role,
            u.created_at,
            m.member_id,
            m.full_name,
            m.email,
            m.phone,
            m.member_type,
            m.status AS member_status
        FROM users u
        LEFT JOIN members m ON u.member_id = m.member_id
        ORDER BY u.user_id DESC
    """
    return execute_query(sql) or []


def get_demo_accounts():
    """Returns sample demo accounts for quick testing."""
    return [
        {"role": "Admin", "username": "admin", "password": "admin123", "desc": "Admin Dashboard: Add books & view who took books"},
        {"role": "Librarian", "username": "librarian", "password": "admin123", "desc": "Librarian Hub: Circulation desk & operations"},
        {"role": "Student", "username": "aarav", "password": "student123", "desc": "Student Portal: Loans & E-Books study center"},
        {"role": "Student", "username": "diya", "password": "student123", "desc": "Student member account"},
        {"role": "Student", "username": "abc", "password": "student123", "desc": "Student member account"},
    ]
