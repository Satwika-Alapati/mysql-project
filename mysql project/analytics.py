"""
Interactive Plotly Analytics & Visualizations for Digital Library System.
Generates rich visual charts for Popular Books, Catalog Breakdown, Circulation, and Fines.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from database import execute_query


def get_popular_books_chart():
    """Generates bar chart of the most popular books based on times borrowed."""
    sql = """
        SELECT title, category, times_borrowed, unique_members
        FROM v_popular_books
        ORDER BY times_borrowed DESC
        LIMIT 10
    """
    rows = execute_query(sql)
    if not rows:
        return None

    df = pd.DataFrame(rows)
    if df.empty or df["times_borrowed"].sum() == 0:
        return None

    fig = px.bar(
        df,
        x="times_borrowed",
        y="title",
        orientation="h",
        color="category",
        hover_data=["unique_members", "category"],
        labels={"times_borrowed": "Borrow Count", "title": "Book Title", "category": "Category"},
        title="Top 10 Most Borrowed Books",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        margin=dict(l=20, r=20, t=40, b=20),
        height=380,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def get_category_distribution_chart():
    """Generates donut chart of books and copies by category."""
    sql = """
        SELECT c.name AS category, COUNT(DISTINCT b.book_id) AS book_count, COUNT(cp.copy_id) AS copy_count
        FROM categories c
        LEFT JOIN books b ON b.category_id = c.category_id
        LEFT JOIN book_copies cp ON cp.book_id = b.book_id
        GROUP BY c.category_id, c.name
        HAVING book_count > 0
        ORDER BY copy_count DESC
    """
    rows = execute_query(sql)
    if not rows:
        return None

    df = pd.DataFrame(rows)
    fig = px.pie(
        df,
        names="category",
        values="copy_count",
        hole=0.45,
        title="Catalog Volume by Category (Physical Copies)",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )
    return fig


def get_copy_status_distribution_chart():
    """Generates bar chart of physical copy statuses (Available, Issued, Reserved, etc.)."""
    sql = """
        SELECT status, COUNT(*) AS count
        FROM book_copies
        GROUP BY status
        ORDER BY count DESC
    """
    rows = execute_query(sql)
    if not rows:
        return None

    df = pd.DataFrame(rows)
    colors = {
        "Available": "#10b981",  # Emerald
        "Issued": "#3b82f6",     # Blue
        "Reserved": "#f59e0b",   # Amber
        "Lost": "#6b7280",       # Gray
        "Damaged": "#ef4444"     # Red
    }
    bar_colors = [colors.get(s, "#8b5cf6") for s in df["status"]]

    fig = go.Figure(data=[
        go.Bar(
            x=df["status"],
            y=df["count"],
            marker_color=bar_colors,
            text=df["count"],
            textposition="auto"
        )
    ])
    fig.update_layout(
        title="Physical Book Copies Status Breakdown",
        xaxis_title="Copy Status",
        yaxis_title="Number of Physical Copies",
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def get_fines_summary_chart():
    """Generates pie chart of Fines status (Unpaid vs Paid vs Waived)."""
    sql = """
        SELECT status, COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total_amount
        FROM fines
        GROUP BY status
    """
    rows = execute_query(sql)
    if not rows:
        return None

    df = pd.DataFrame(rows)
    color_map = {
        "Unpaid": "#ef4444",
        "Paid": "#10b981",
        "Waived": "#6b7280"
    }
    fig = px.pie(
        df,
        names="status",
        values="total_amount",
        title="Fines Distribution by Amount ($)",
        color="status",
        color_discrete_map=color_map,
        hole=0.4
    )
    fig.update_traces(textposition="inside", textinfo="label+value+percent")
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def get_circulation_trends_chart():
    """Generates monthly borrowing volume trend."""
    sql = """
        SELECT DATE_FORMAT(issue_date, '%b %Y') AS month_label,
               COUNT(*) AS total_loans,
               SUM(CASE WHEN return_date IS NOT NULL THEN 1 ELSE 0 END) AS returned_loans
        FROM issues
        GROUP BY DATE_FORMAT(issue_date, '%Y-%m'), DATE_FORMAT(issue_date, '%b %Y')
        ORDER BY DATE_FORMAT(issue_date, '%Y-%m') ASC
        LIMIT 12
    """
    rows = execute_query(sql)
    if not rows:
        return None

    df = pd.DataFrame(rows)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["month_label"],
        y=df["total_loans"],
        name="Total Books Issued",
        marker_color="#6366f1"
    ))
    fig.add_trace(go.Bar(
        x=df["month_label"],
        y=df["returned_loans"],
        name="Returned Books",
        marker_color="#10b981"
    ))
    fig.update_layout(
        barmode="group",
        title="Circulation Activity Trends",
        xaxis_title="Period",
        yaxis_title="Count",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig
