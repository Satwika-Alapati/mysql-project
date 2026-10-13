"""
Email Notification Service for Digital Library System.
Supports real SMTP (Gmail, Outlook, custom SMTP) and Simulation Mode.
Always records all sent/attempted emails directly into the MySQL `notifications` table!
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
from database import execute_non_query, execute_query

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "library@university.edu")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Digital Library System")
EMAIL_SIMULATION_MODE = os.getenv("EMAIL_SIMULATION_MODE", "True").lower() in ("true", "1", "yes")


def send_library_email(
    member_id: int,
    recipient_email: str,
    subject: str,
    body_text: str,
    body_html: str = None,
    notif_type: str = "General",
    issue_id: int = None
):
    """
    Send an email to a library member.
    Saves record to MySQL `notifications` table with status 'Sent', 'Pending', or 'Failed'.
    """
    status = "Pending"
    error_msg = None
    sent_at = None

    if EMAIL_SIMULATION_MODE or not SMTP_USER or not SMTP_PASSWORD:
        # Simulation mode: log as Sent successfully in simulation
        status = "Sent"
        sent_at = datetime.now()
        error_msg = "Simulated delivery (Logged to Database)"
    else:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
            msg["To"] = recipient_email

            part1 = MIMEText(body_text, "plain")
            msg.attach(part1)

            if body_html:
                part2 = MIMEText(body_html, "html")
                msg.attach(part2)

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM_EMAIL, [recipient_email], msg.as_string())

            status = "Sent"
            sent_at = datetime.now()
        except Exception as e:
            status = "Failed"
            error_msg = str(e)[:250]

    # Save to notifications table in MySQL
    sql = """
        INSERT INTO notifications (member_id, issue_id, type, subject, message, status, sent_at, error)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        execute_non_query(sql, (
            member_id,
            issue_id,
            notif_type,
            subject,
            body_text,
            status,
            sent_at,
            error_msg
        ))
    except Exception as db_err:
        print(f"Error logging notification to database: {db_err}")

    return {
        "success": status == "Sent",
        "status": status,
        "mode": "Simulated" if (EMAIL_SIMULATION_MODE or not SMTP_USER) else "Live SMTP",
        "error": error_msg
    }


def send_issue_confirmation(
    member_id: int,
    member_name: str = "Member",
    email: str = "",
    book_title: str = "",
    barcode: str = "",
    due_date = None,
    issue_id: int = None
):
    """Send loan confirmation email to member."""
    subject = f"Book Issued: {book_title}"
    formatted_date = str(due_date)
    body_text = f"""Dear {member_name},

You have successfully borrowed '{book_title}' (Barcode: {barcode}).
Due Date: {formatted_date}

Please ensure the book is returned on or before the due date to avoid overdue fines.

Thank you,
Digital Library System
"""
    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
        <h2 style="color: #4f46e5; margin-top: 0;">Book Issue Confirmation</h2>
        <p>Dear <strong>{member_name}</strong>,</p>
        <p>You have successfully checked out the following book from the library:</p>
        <div style="background: #f8fafc; padding: 15px; border-radius: 6px; margin: 15px 0;">
            <p style="margin: 5px 0;"><strong>Title:</strong> {book_title}</p>
            <p style="margin: 5px 0;"><strong>Barcode:</strong> <code>{barcode}</code></p>
            <p style="margin: 5px 0; color: #dc2626;"><strong>Due Date:</strong> {formatted_date}</p>
        </div>
        <p style="font-size: 13px; color: #64748b;">Please return this book by the due date to avoid overdue fines.</p>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
        <p style="font-size: 12px; color: #94a3b8;">Digital Library & Book Circulation System</p>
    </div>
    """
    return send_library_email(member_id, email, subject, body_text, body_html, "Book Issued", issue_id)


def send_return_receipt(
    member_id: int,
    member_name: str = "Member",
    email: str = "",
    book_title: str = "",
    barcode: str = "",
    fine_amount: float = 0.0,
    condition: str = "Good"
):
    """Send return confirmation email to member."""
    subject = f"Book Returned: {book_title}"
    body_text = f"""Dear {member_name},

'{book_title}' (Barcode: {barcode}) has been successfully returned.
Condition: {condition}
Fine Assessed: ${fine_amount:.2f}

Thank you,
Digital Library System
"""
    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
        <h2 style="color: #10b981; margin-top: 0;">Book Return Receipt</h2>
        <p>Dear <strong>{member_name}</strong>,</p>
        <p>The following book has been checked back into the library:</p>
        <div style="background: #f8fafc; padding: 15px; border-radius: 6px; margin: 15px 0;">
            <p style="margin: 5px 0;"><strong>Title:</strong> {book_title}</p>
            <p style="margin: 5px 0;"><strong>Barcode:</strong> <code>{barcode}</code></p>
            <p style="margin: 5px 0;"><strong>Condition:</strong> {condition}</p>
            <p style="margin: 5px 0; color: {'#dc2626' if fine_amount > 0 else '#16a34a'};">
                <strong>Fine Amount:</strong> ${fine_amount:.2f}
            </p>
        </div>
        <p style="font-size: 13px; color: #64748b;">Thank you for using our library circulation services!</p>
    </div>
    """
    return send_library_email(member_id, email, subject, body_text, body_html, "Book Returned")


def send_overdue_warning(
    member_id: int,
    member_name: str = "Member",
    email: str = "",
    book_title: str = "",
    due_date = None,
    accrued_fine: float = 0.0,
    issue_id: int = None,
    days_overdue: int = 0
):
    """Send overdue notice email with explicit fine calculation to member."""
    subject = f"⚠️ OVERDUE NOTICE: '{book_title}' — Current Fine: ${accrued_fine:.2f}"
    body_text = f"""Dear {member_name},

This is an urgent circulation reminder that your borrowed book '{book_title}' is OVERDUE.

Loan Details:
- Due Date: {due_date}
- Days Overdue: {days_overdue} day(s) late
- Total Fine Accrued: ${accrued_fine:.2f}

Please return the book to the library circulation desk immediately to stop additional daily fine accumulation.

Thank you,
Digital Library System
"""
    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; padding: 22px; border: 2px solid #ef4444; background: #fff5f5; border-radius: 10px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
            <span style="font-size: 26px;">⚠️</span>
            <h2 style="color: #b91c1c; margin: 0;">Library Overdue & Fine Notice</h2>
        </div>
        <p>Dear <strong>{member_name}</strong>,</p>
        <p>Our circulation records show that the following borrowed title has passed its due date:</p>
        
        <div style="background: #ffffff; padding: 18px; border-radius: 8px; margin: 15px 0; border: 1px solid #fecaca; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <tr>
                    <td style="padding: 6px 0; color: #64748b;"><strong>Book Title:</strong></td>
                    <td style="padding: 6px 0; color: #1e293b; font-weight: 600;">{book_title}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; color: #64748b;"><strong>Original Due Date:</strong></td>
                    <td style="padding: 6px 0; color: #1e293b;">{due_date}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; color: #64748b;"><strong>Delayed Period:</strong></td>
                    <td style="padding: 6px 0; color: #dc2626; font-weight: 600;">{days_overdue} day(s) overdue</td>
                </tr>
                <tr style="border-top: 1px dashed #f87171;">
                    <td style="padding: 10px 0 4px 0; color: #b91c1c; font-size: 16px;"><strong>Current Fine Due:</strong></td>
                    <td style="padding: 10px 0 4px 0; color: #b91c1c; font-size: 18px; font-weight: 800;">${accrued_fine:.2f}</td>
                </tr>
            </table>
        </div>

        <p style="font-size: 13px; color: #475569; line-height: 1.5;">
            Daily fines accrue automatically for each delayed day until the book is checked in. 
            Please return the book to the counter as soon as possible to prevent further penalties.
        </p>
        <hr style="border: none; border-top: 1px solid #fee2e2; margin: 20px 0;">
        <p style="font-size: 12px; color: #94a3b8; margin: 0;">Digital Library & Book Circulation System • Automated Notice</p>
    </div>
    """
    return send_library_email(member_id, email, subject, body_text, body_html, "Overdue Notice", issue_id)


def send_all_overdue_reminders():
    """
    Finds all active overdue loans across the library, calculates each student's fine,
    dispatches email reminders, and logs them to MySQL database.
    Returns summary statistics.
    """
    sql = """
        SELECT 
            i.issue_id,
            i.member_id,
            m.full_name AS member_name,
            m.email,
            b.title AS book_title,
            c.barcode,
            i.due_date,
            DATEDIFF(CURDATE(), i.due_date) AS days_overdue,
            fn_calc_fine(i.due_date, CURDATE()) AS fine_accrued
        FROM issues i
        JOIN members m ON m.member_id = i.member_id
        JOIN book_copies c ON c.copy_id = i.copy_id
        JOIN books b ON b.book_id = c.book_id
        WHERE i.return_date IS NULL AND i.due_date < CURDATE()
        ORDER BY days_overdue DESC
    """
    overdues = execute_query(sql)
    if not overdues:
        return {"count": 0, "total_fines": 0.0, "details": []}

    sent_count = 0
    total_fines = 0.0
    details = []

    for item in overdues:
        fine_val = float(item["fine_accrued"] or 0.0)
        days_late = int(item["days_overdue"] or 0)
        res = send_overdue_warning(
            member_id=item["member_id"],
            member_name=item["member_name"],
            email=item["email"],
            book_title=item["book_title"],
            due_date=item["due_date"],
            accrued_fine=fine_val,
            issue_id=item["issue_id"],
            days_overdue=days_late
        )
        if res.get("success"):
            sent_count += 1
            total_fines += fine_val
            details.append({
                "member_name": item["member_name"],
                "book_title": item["book_title"],
                "days_overdue": days_late,
                "fine_accrued": fine_val
            })

    return {"count": sent_count, "total_fines": total_fines, "details": details}


def send_reservation_ready_notice(member_id: int, member_name: str, email: str, book_title: str, ready_until):
    """Send notice that reserved book is ready for pickup."""
    subject = f"Reserved Book Ready for Pickup: {book_title}"
    body_text = f"""Dear {member_name},

Great news! The book you reserved '{book_title}' is now available and held for you at the circulation desk.
Please pick it up before: {ready_until}.
After this date, the hold will expire.

Thank you,
Digital Library System
"""
    body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; padding: 20px; border: 1px solid #cbd5e1; border-radius: 8px;">
        <h2 style="color: #8b5cf6; margin-top: 0;">Your Reserved Book is Ready!</h2>
        <p>Dear <strong>{member_name}</strong>,</p>
        <p>Good news! Your reservation has been fulfilled and the book is waiting for you:</p>
        <div style="background: #f5f3ff; padding: 15px; border-radius: 6px; margin: 15px 0; border: 1px solid #ddd6fe;">
            <p style="margin: 5px 0;"><strong>Title:</strong> {book_title}</p>
            <p style="margin: 5px 0; color: #6d28d9;"><strong>Hold Expires On:</strong> {ready_until}</p>
        </div>
        <p>Please present your library card at the counter to check out the book.</p>
    </div>
    """
    return send_library_email(member_id, email, subject, body_text, body_html, "Reservation Ready")
