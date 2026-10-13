"""
Database connection and operation utilities for Digital Library System.
Connects directly to MySQL and handles queries, transactions, and stored routines.
"""

import os
import mysql.connector
from mysql.connector import Error, pooling
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Satwika@2004")
DB_NAME = os.getenv("DB_NAME", "digital_library")


def get_connection():
    """Create and return a raw MySQL connection."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            autocommit=False,
            charset="utf8mb4"
        )
        return conn
    except Error as e:
        raise RuntimeError(f"Database connection error: {e}")


def test_connection():
    """Test if database is reachable and returns version."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        ver = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return True, f"Connected to MySQL {ver} ({DB_NAME} on {DB_HOST}:{DB_PORT})"
    except Exception as e:
        return False, str(e)


def execute_query(sql, params=None, fetchone=False, as_dict=True):
    """
    Execute a SELECT query and return rows.
    Returns list of dicts (or tuples) or a single dict/tuple.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=as_dict)
        cursor.execute(sql, params or ())
        if fetchone:
            res = cursor.fetchone()
        else:
            res = cursor.fetchall()
        cursor.close()
        return res
    finally:
        conn.close()


def execute_non_query(sql, params=None, commit=True):
    """
    Execute an INSERT, UPDATE, or DELETE query.
    Returns (rowcount, last_insert_id).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        rowcount = cursor.rowcount
        last_id = cursor.lastrowid
        if commit:
            conn.commit()
        cursor.close()
        return rowcount, last_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def call_procedure(proc_name, args=()):
    """
    Call a MySQL Stored Procedure by name.
    Returns (success, result_message_or_data).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc(proc_name, args)
        conn.commit()
        
        # Check if stored procedure returned any result sets
        results = []
        for result in cursor.stored_results():
            results.append(result.fetchall())
            
        cursor.close()
        return True, results if results else "Procedure executed successfully"
    except mysql.connector.Error as err:
        conn.rollback()
        # Clean up MySQL error message for user display
        msg = err.msg if hasattr(err, "msg") else str(err)
        return False, msg
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def run_maintenance():
    """Runs database maintenance routines like expiring reservations and daily checks."""
    try:
        call_procedure("sp_daily_maintenance")
        return True, "Maintenance executed"
    except Exception as e:
        return False, str(e)


def add_book_to_catalog(title: str, isbn: str, category_name: str, publisher_name: str,
                        author_names: list, publication_year: int = 2024, edition: str = "1st",
                        language: str = "English", price: float = 45.0, num_copies: int = 3,
                        shelf_location: str = "Stack A - Shelf 101"):
    """
    Add a book to the library catalog with category, publisher, authors,
    and automatically create physical book copies with barcodes.
    Returns (success: bool, result_or_book_id, message: str).
    """
    if not title or not title.strip():
        return False, None, "Book title is required."
    if not isbn or not isbn.strip():
        return False, None, "ISBN is required."

    title = title.strip()
    isbn = isbn.strip()
    category_name = (category_name or "General").strip()
    publisher_name = (publisher_name or "Academic Press").strip()

    # Normalize author names
    if isinstance(author_names, str):
        author_names = [a.strip() for a in author_names.split(",") if a.strip()]
    if not author_names:
        author_names = ["Unknown Author"]

    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # 1. Check if ISBN already exists
        cursor.execute("SELECT book_id, title FROM books WHERE isbn = %s", (isbn,))
        existing_book = cursor.fetchone()
        if existing_book:
            cursor.close()
            return False, existing_book["book_id"], f"A book with ISBN '{isbn}' already exists in catalog: '{existing_book['title']}'."

        # 2. Get or create Category
        cursor.execute("SELECT category_id FROM categories WHERE name = %s", (category_name,))
        cat_row = cursor.fetchone()
        if cat_row:
            cat_id = cat_row["category_id"]
        else:
            cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category_name,))
            cat_id = cursor.lastrowid

        # 3. Get or create Publisher
        cursor.execute("SELECT publisher_id FROM publishers WHERE name = %s", (publisher_name,))
        pub_row = cursor.fetchone()
        if pub_row:
            pub_id = pub_row["publisher_id"]
        else:
            cursor.execute("INSERT INTO publishers (name) VALUES (%s)", (publisher_name,))
            pub_id = cursor.lastrowid

        # 4. Insert Book
        insert_book_sql = """
            INSERT INTO books (isbn, title, publisher_id, category_id, publication_year, edition, language, price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_book_sql, (
            isbn, title, pub_id, cat_id, int(publication_year), edition or "1st", language or "English", float(price)
        ))
        book_id = cursor.lastrowid

        # 5. Handle Authors & Book-Author relationships
        for auth_name in author_names:
            auth_name = auth_name.strip()
            if not auth_name:
                continue
            cursor.execute("SELECT author_id FROM authors WHERE name = %s", (auth_name,))
            auth_row = cursor.fetchone()
            if auth_row:
                a_id = auth_row["author_id"]
            else:
                cursor.execute("INSERT INTO authors (name) VALUES (%s)", (auth_name,))
                a_id = cursor.lastrowid

            cursor.execute("INSERT IGNORE INTO book_authors (book_id, author_id) VALUES (%s, %s)", (book_id, a_id))

        # 6. Auto-generate physical copies with unique barcodes
        num_copies = max(1, min(int(num_copies), 50))
        for i in range(1, num_copies + 1):
            barcode = f"BC-{book_id:04d}-{i}"
            cursor.execute("""
                INSERT INTO book_copies (book_id, barcode, shelf_location, status, acquired_on)
                VALUES (%s, %s, %s, 'Available', CURDATE())
            """, (book_id, barcode, shelf_location or "General Stack"))

        conn.commit()
        cursor.close()
        return True, book_id, f"Book '{title}' successfully registered with {num_copies} physical copies (Barcodes: BC-{book_id:04d}-1 to BC-{book_id:04d}-{num_copies})!"
    except Exception as e:
        conn.rollback()
        return False, None, f"Database error adding book: {str(e)}"
    finally:
        conn.close()

