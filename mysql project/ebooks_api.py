"""
E-Books API and Digital Study Center Module.
Integrates with Open Library API and Project Gutenberg (Gutendex)
to provide students with rich e-books discovery, reading materials,
and a personalized study workspace with persistent notes.
"""

import json
import urllib.parse
import urllib.request
import streamlit as st
from database import execute_query, execute_non_query


# Headers for polite public API requests
API_HEADERS = {
    "User-Agent": "DigitalLibraryCirculation/2.0 (student-academic-reader@digitallibrary.org)"
}

# Pre-curated academic & classic e-books for instantaneous zero-latency access
CURATED_EBOOKS = [
    {
        "id": "cs-algo-1",
        "title": "Introduction to Algorithms & Data Structures",
        "authors": "Thomas Cormen, Charles Leiserson",
        "subject": "Computer Science",
        "year": "2022",
        "cover_url": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400&q=80",
        "description": "Essential foundations of algorithms, sorting, graph traversal, greedy techniques, and algorithmic complexity.",
        "source": "Open Academic Archive",
        "read_url": "https://openlibrary.org/subjects/algorithms",
        "sample_content": """# Chapter 1: Foundations of Algorithms

An algorithm is any well-defined computational procedure that takes some value, or set of values, as input and produces some value, or set of values, as output.

### 1.1 Efficiency and Computational Complexity
Different algorithms devised to solve the same problem often differ dramatically in their efficiency. These differences can be much more significant than differences due to hardware or coding languages.

We measure performance using Big-O notation:
- **O(1)**: Constant time
- **O(log n)**: Logarithmic time (e.g., Binary Search)
- **O(n)**: Linear time (e.g., Linear Scan)
- **O(n log n)**: Linearithmic time (e.g., Merge Sort, Heapsort)
- **O(n²)**: Quadratic time (e.g., Bubble Sort, Insertion Sort)

### 1.2 Divide and Conquer Paradigm
The divide-and-conquer strategy solves a problem by breaking it into subproblems:
1. **Divide**: Break the problem into smaller instances.
2. **Conquer**: Recursively solve the subproblems.
3. **Combine**: Merge the subproblem solutions into a solution for the original problem.
"""
    },
    {
        "id": "cs-python-1",
        "title": "Python Programming & System Architecture",
        "authors": "Guido van Rossum, David Beazley",
        "subject": "Computer Science",
        "year": "2023",
        "cover_url": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=400&q=80",
        "description": "Comprehensive guide to Python internals, object-oriented design, database connectivity, and clean application structure.",
        "source": "Open Academic Archive",
        "read_url": "https://openlibrary.org/subjects/python_(computer_program_language)",
        "sample_content": """# Chapter 1: Modern Python Architecture

Python is an interpreted, high-level, dynamically typed language emphasizing readability and developer productivity.

### Key Architectural Concepts
1. **First-Class Functions**: Functions can be passed as arguments, returned from other functions, and assigned to variables.
2. **List & Dict Comprehensions**: Elegant, expressive constructs for data transformation.
3. **Context Managers (`with` statement)**: Guarantees deterministic resource cleanup (e.g., database connections, file streams).

```python
# Context management example
with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    records = cursor.fetchall()
```

### Relational Database Integration
When integrating Python with MySQL:
- Always use parameterized queries (`%s` placeholders) to prevent SQL Injection.
- Implement connection pools for high-concurrency Streamlit apps.
"""
    },
    {
        "id": "gutenberg-84",
        "title": "Frankenstein; Or, The Modern Prometheus",
        "authors": "Mary Wollstonecraft Shelley",
        "subject": "Literature & Ethics",
        "year": "1818",
        "cover_url": "https://www.gutenberg.org/cache/epub/84/pg84.cover.medium.jpg",
        "description": "The seminal gothic science-fiction masterpiece exploring human creation, responsibility, empathy, and scientific ethics.",
        "source": "Project Gutenberg (Full Book)",
        "read_url": "https://www.gutenberg.org/ebooks/84",
        "sample_content": """Letter 1
To Mrs. Saville, England.
St. Petersburgh, Dec. 11th, 17—.

You will rejoice to hear that no disaster has accompanied the commencement of an enterprise which you have regarded with such evil forebodings. I arrived here yesterday, and my first task is to assure my dear sister of my welfare and increasing confidence in the success of my undertaking.

I am already far north of London, and as I walk in the streets of Petersburgh, I feel a cold northern breeze play upon my cheeks, which braces my nerves and fills me with delight. Do you understand this feeling? This breeze, which has travelled from the regions towards which I am advancing, gives me a foretaste of those icy climes...
"""
    },
    {
        "id": "gutenberg-1497",
        "title": "The Republic",
        "authors": "Plato",
        "subject": "Philosophy & Politics",
        "year": "375 BC",
        "cover_url": "https://www.gutenberg.org/cache/epub/1497/pg1497.cover.medium.jpg",
        "description": "Socratic dialogue on justice, the order and character of the just city-state, and the nature of the philosopher king.",
        "source": "Project Gutenberg (Full Book)",
        "read_url": "https://www.gutenberg.org/ebooks/1497",
        "sample_content": """BOOK I.

I went down yesterday to the Piraeus with Glaucon the son of Ariston, that I might offer up my prayers to the goddess; and also because I wanted to see in what manner they would celebrate the festival, which was a new thing. I was delighted with the procession of the inhabitants; but that of the Thracians was equally, if not more, graceful.

When we had finished our prayers and viewed the spectacle, we turned in the direction of the city; and at that moment Polemarchus the son of Cephalus chanced to catch sight of us from a distance as we were starting on our way home...
"""
    },
    {
        "id": "gutenberg-3600",
        "title": "Relativity: The Special and General Theory",
        "authors": "Albert Einstein",
        "subject": "Physics & Science",
        "year": "1920",
        "cover_url": "https://www.gutenberg.org/cache/epub/3600/pg3600.cover.medium.jpg",
        "description": "Albert Einstein's own direct, accessible explanation of the special and general theories of relativity for students.",
        "source": "Project Gutenberg (Full Book)",
        "read_url": "https://www.gutenberg.org/ebooks/3600",
        "sample_content": """PART I: THE SPECIAL THEORY OF RELATIVITY

1. Physical Meaning of Geometrical Propositions

In your school days, you were certainly acquainted with the noble edifice of Euclid's geometry, and you remember with what respect you looked upon this magnificent structure. But if someone asked you: "Are these propositions true?" you might have been puzzled.

Geometry sets out from certain intuitive concepts, such as point, line, and plane, and from certain simple propositions (axioms). All other propositions are deduced by logical reasoning. But what is meant by the "truth" of these statements in real physical space?
"""
    },
    {
        "id": "gutenberg-1661",
        "title": "The Adventures of Sherlock Holmes",
        "authors": "Arthur Conan Doyle",
        "subject": "Literature & Mystery",
        "year": "1892",
        "cover_url": "https://www.gutenberg.org/cache/epub/1661/pg1661.cover.medium.jpg",
        "description": "Twelve classic detective stories showcasing the analytical deductive reasoning of Sherlock Holmes and Dr. John Watson.",
        "source": "Project Gutenberg (Full Book)",
        "read_url": "https://www.gutenberg.org/ebooks/1661",
        "sample_content": """I. A SCANDAL IN BOHEMIA

To Sherlock Holmes she is always THE woman. I have seldom heard him mention her under any other name. In his eyes she eclipses and predominates the whole of her sex. It was not that he felt any emotion akin to love for Irene Adler. All emotions were abhorrent to his cold, precise but admirably balanced mind.

He was, I take it, the most perfect reasoning and observing machine that the world has seen...
"""
    }
]


@st.cache_data(ttl=1800, show_spinner=False)
def search_openlibrary_api(query: str, limit: int = 12):
    """
    Search Open Library API for books matching the query.
    Returns list of parsed book dictionaries.
    """
    if not query or len(query.strip()) < 2:
        return []

    clean_q = urllib.parse.quote_plus(query.strip())
    url = f"https://openlibrary.org/search.json?q={clean_q}&limit={limit}"

    req = urllib.request.Request(url, headers=API_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=6) as response:
            data = json.loads(response.read().decode("utf-8"))
            docs = data.get("docs", [])
            results = []

            for doc in docs:
                cover_id = doc.get("cover_i")
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None
                key = doc.get("key", "").replace("/works/", "")
                authors = ", ".join(doc.get("author_name", [])) if doc.get("author_name") else "Unknown Author"
                publishers = ", ".join(doc.get("publisher", [])[:2]) if doc.get("publisher") else "Academic Press"
                isbns = doc.get("isbn", [])
                isbn = isbns[0] if isbns else ""
                subjects = doc.get("subject", [])[:4] if doc.get("subject") else ["General Reading"]
                ia = doc.get("ia", [])
                archive_url = f"https://archive.org/details/{ia[0]}" if ia and len(ia) > 0 else None

                results.append({
                    "id": f"ol-{key}",
                    "title": doc.get("title", "Untitled Book"),
                    "authors": authors,
                    "publisher": publishers,
                    "year": str(doc.get("first_publish_year", "N/A")),
                    "isbn": isbn,
                    "subject": subjects[0] if subjects else "General",
                    "subjects_list": subjects,
                    "cover_url": cover_url,
                    "read_url": f"https://openlibrary.org{doc.get('key')}" if doc.get("key") else "https://openlibrary.org",
                    "archive_url": archive_url,
                    "source": "Open Library API",
                    "description": f"Published in {doc.get('first_publish_year', 'N/A')}. Subjects: {', '.join(subjects)}.",
                    "sample_content": None
                })
            return results
    except Exception as e:
        print(f"OpenLibrary API error: {e}")
        return []


@st.cache_data(ttl=1800, show_spinner=False)
def search_gutendex_api(query: str):
    """
    Search Gutendex (Project Gutenberg) API for public domain full-text books.
    """
    if not query or len(query.strip()) < 2:
        return []

    clean_q = urllib.parse.quote_plus(query.strip())
    url = f"https://gutendex.com/books/?search={clean_q}"

    req = urllib.request.Request(url, headers=API_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=6) as response:
            data = json.loads(response.read().decode("utf-8"))
            results = []
            for b in data.get("results", [])[:10]:
                authors = ", ".join([a.get("name", "") for a in b.get("authors", [])]) or "Unknown Author"
                formats = b.get("formats", {})
                cover_url = formats.get("image/jpeg")
                read_url = formats.get("text/html") or formats.get("text/html; charset=utf-8") or f"https://www.gutenberg.org/ebooks/{b.get('id')}"
                txt_url = formats.get("text/plain; charset=utf-8") or formats.get("text/plain; charset=us-ascii")
                epub_url = formats.get("application/epub+zip")
                subjects = b.get("subjects", [])

                results.append({
                    "id": f"gt-{b.get('id')}",
                    "title": b.get("title", "Untitled"),
                    "authors": authors,
                    "publisher": "Project Gutenberg",
                    "year": "Classic / Public Domain",
                    "isbn": f"GT-{b.get('id')}",
                    "subject": subjects[0] if subjects else "Literature",
                    "subjects_list": subjects[:4],
                    "cover_url": cover_url,
                    "read_url": read_url,
                    "txt_url": txt_url,
                    "epub_url": epub_url,
                    "source": "Project Gutenberg (Full Text)",
                    "description": f"Downloads: {b.get('download_count', 0):,} readers worldwide. Full text free to study.",
                    "sample_content": None
                })
            return results
    except Exception as e:
        print(f"Gutendex API error: {e}")
        return []


def ensure_ebooks_table_exists():
    """Ensure the ebooks table exists in MySQL and seed with initial curated library if empty."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS ebooks (
        ebook_id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        author VARCHAR(255) NOT NULL,
        category VARCHAR(100) DEFAULT 'General',
        publication_year VARCHAR(50) DEFAULT '2024',
        isbn VARCHAR(50) NULL,
        cover_url TEXT NULL,
        read_url TEXT NULL,
        download_url TEXT NULL,
        format VARCHAR(50) DEFAULT 'PDF / EPUB',
        file_size VARCHAR(50) DEFAULT '3.5 MB',
        description TEXT NULL,
        content_preview LONGTEXT NULL,
        added_by VARCHAR(100) DEFAULT 'System',
        views_count INT DEFAULT 0,
        downloads_count INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    try:
        execute_non_query(create_table_sql)
        cnt = execute_query("SELECT COUNT(*) AS c FROM ebooks", fetchone=True)
        if cnt and cnt["c"] == 0:
            seed_data = [
                (
                    "Introduction to Algorithms & Data Structures",
                    "Thomas Cormen, Charles Leiserson",
                    "Computer Science",
                    "2022",
                    "978-0262033848",
                    "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400&q=80",
                    "https://openlibrary.org/subjects/algorithms",
                    "https://openlibrary.org/works/OL1869348W",
                    "PDF / Online",
                    "14.8 MB",
                    "Essential foundations of algorithms, sorting, graph traversal, greedy techniques, and algorithmic complexity.",
                    """# Chapter 1: Foundations of Algorithms

An algorithm is any well-defined computational procedure that takes some value, or set of values, as input and produces some value, or set of values, as output.

### 1.1 Efficiency and Computational Complexity
Different algorithms devised to solve the same problem often differ dramatically in their efficiency. These differences can be much more significant than differences due to hardware or coding languages.

We measure performance using Big-O notation:
- **O(1)**: Constant time
- **O(log n)**: Logarithmic time (e.g., Binary Search)
- **O(n)**: Linear time (e.g., Linear Scan)
- **O(n log n)**: Linearithmic time (e.g., Merge Sort, Heapsort)
- **O(n²)**: Quadratic time (e.g., Bubble Sort, Insertion Sort)

### 1.2 Divide and Conquer Paradigm
The divide-and-conquer strategy solves a problem by breaking it into subproblems:
1. **Divide**: Break the problem into smaller instances.
2. **Conquer**: Recursively solve the subproblems.
3. **Combine**: Merge the subproblem solutions into a solution for the original problem.""",
                    "System"
                ),
                (
                    "Python Programming & System Architecture",
                    "Guido van Rossum, David Beazley",
                    "Computer Science",
                    "2023",
                    "978-0134853987",
                    "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=400&q=80",
                    "https://openlibrary.org/subjects/python_(computer_program_language)",
                    "https://docs.python.org/3/tutorial/",
                    "PDF / Web",
                    "8.2 MB",
                    "Comprehensive guide to Python internals, object-oriented design, database connectivity, and clean application structure.",
                    """# Chapter 1: Modern Python Architecture

Python is an interpreted, high-level, dynamically typed language emphasizing readability and developer productivity.

### Key Architectural Concepts
1. **First-Class Functions**: Functions can be passed as arguments, returned from other functions, and assigned to variables.
2. **List & Dict Comprehensions**: Elegant, expressive constructs for data transformation.
3. **Context Managers (`with` statement)**: Guarantees deterministic resource cleanup (e.g., database connections, file streams).

### Relational Database Integration
When integrating Python with MySQL:
- Always use parameterized queries (`%s` placeholders) to prevent SQL Injection.
- Implement connection pools for high-concurrency Streamlit apps.""",
                    "System"
                ),
                (
                    "Deep Learning & Neural Networks Foundations",
                    "Ian Goodfellow, Yoshua Bengio, Aaron Courville",
                    "Artificial Intelligence",
                    "2023",
                    "978-0262035612",
                    "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=400&q=80",
                    "https://www.deeplearningbook.org/",
                    "https://www.deeplearningbook.org/",
                    "PDF / Online",
                    "22.4 MB",
                    "The definitive textbook on machine learning, backpropagation, convolutional networks, and generative modeling.",
                    """# Chapter 1: Introduction to Deep Learning

Deep learning is a specific subfield of machine learning: a new take on learning representations from data that puts the emphasis on learning successive layers of increasingly meaningful representations.

### Core Mathematical Pillars
1. **Linear Algebra**: Vectors, matrices, tensors, and eigenvalues.
2. **Probability Theory**: Uncertainty quantification and Bayes rule.
3. **Numerical Optimization**: Gradient descent, Adam optimizer, and learning rate scheduling.""",
                    "System"
                ),
                (
                    "Relativity: The Special and General Theory",
                    "Albert Einstein",
                    "Physics & Science",
                    "1920",
                    "GT-3600",
                    "https://www.gutenberg.org/cache/epub/3600/pg3600.cover.medium.jpg",
                    "https://www.gutenberg.org/ebooks/3600",
                    "https://www.gutenberg.org/ebooks/3600.epub.images",
                    "EPUB / Text",
                    "1.2 MB",
                    "Albert Einstein's own direct, accessible explanation of the special and general theories of relativity for students.",
                    """PART I: THE SPECIAL THEORY OF RELATIVITY

1. Physical Meaning of Geometrical Propositions
In your school days, you were certainly acquainted with the noble edifice of Euclid's geometry, and you remember with what respect you looked upon this magnificent structure. But if someone asked you: "Are these propositions true?" you might have been puzzled.

Geometry sets out from certain intuitive concepts, such as point, line, and plane, and from certain simple propositions (axioms). All other propositions are deduced by logical reasoning.""",
                    "System"
                ),
                (
                    "Frankenstein; Or, The Modern Prometheus",
                    "Mary Wollstonecraft Shelley",
                    "Literature",
                    "1818",
                    "GT-84",
                    "https://www.gutenberg.org/cache/epub/84/pg84.cover.medium.jpg",
                    "https://www.gutenberg.org/ebooks/84",
                    "https://www.gutenberg.org/ebooks/84.epub.images",
                    "EPUB / HTML",
                    "2.8 MB",
                    "The seminal gothic science-fiction masterpiece exploring human creation, responsibility, empathy, and scientific ethics.",
                    """Letter 1
To Mrs. Saville, England.
St. Petersburgh, Dec. 11th, 17—.

You will rejoice to hear that no disaster has accompanied the commencement of an enterprise which you have regarded with such evil forebodings. I arrived here yesterday, and my first task is to assure my dear sister of my welfare and increasing confidence in the success of my undertaking.

I am already far north of London, and as I walk in the streets of Petersburgh, I feel a cold northern breeze play upon my cheeks, which braces my nerves and fills me with delight.""",
                    "System"
                ),
                (
                    "The Republic",
                    "Plato",
                    "Philosophy",
                    "375 BC",
                    "GT-1497",
                    "https://www.gutenberg.org/cache/epub/1497/pg1497.cover.medium.jpg",
                    "https://www.gutenberg.org/ebooks/1497",
                    "https://www.gutenberg.org/ebooks/1497.epub.images",
                    "EPUB / Text",
                    "1.9 MB",
                    "Socratic dialogue on justice, the order and character of the just city-state, and the nature of the philosopher king.",
                    """BOOK I.

I went down yesterday to the Piraeus with Glaucon the son of Ariston, that I might offer up my prayers to the goddess; and also because I wanted to see in what manner they would celebrate the festival, which was a new thing. I was delighted with the procession of the inhabitants; but that of the Thracians was equally, if not more, graceful.""",
                    "System"
                ),
                (
                    "The Adventures of Sherlock Holmes",
                    "Arthur Conan Doyle",
                    "Literature & Mystery",
                    "1892",
                    "GT-1661",
                    "https://www.gutenberg.org/cache/epub/1661/pg1661.cover.medium.jpg",
                    "https://www.gutenberg.org/ebooks/1661",
                    "https://www.gutenberg.org/ebooks/1661.epub.images",
                    "EPUB / Text",
                    "2.1 MB",
                    "Twelve classic detective stories showcasing the analytical deductive reasoning of Sherlock Holmes and Dr. John Watson.",
                    """I. A SCANDAL IN BOHEMIA

To Sherlock Holmes she is always THE woman. I have seldom heard him mention her under any other name. In his eyes she eclipses and predominates the whole of her sex. It was not that he felt any emotion akin to love for Irene Adler. All emotions were abhorrent to his cold, precise but admirably balanced mind.

He was, I take it, the most perfect reasoning and observing machine that the world has seen...""",
                    "System"
                ),
                (
                    "Pride and Prejudice",
                    "Jane Austen",
                    "Literature",
                    "1813",
                    "GT-1342",
                    "https://www.gutenberg.org/cache/epub/1342/pg1342.cover.medium.jpg",
                    "https://www.gutenberg.org/ebooks/1342",
                    "https://www.gutenberg.org/ebooks/1342.epub.images",
                    "EPUB / Text",
                    "1.7 MB",
                    "Classic romantic novel detailing the emotional development of Elizabeth Bennet and Fitzwilliam Darcy.",
                    """Chapter 1

It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.

However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters.""",
                    "System"
                )
            ]
            for item in seed_data:
                execute_non_query(
                    """
                    INSERT INTO ebooks (title, author, category, publication_year, isbn, cover_url, read_url, download_url, format, file_size, description, content_preview, added_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    item
                )
    except Exception as e:
        print(f"Error ensuring ebooks table: {e}")


def get_db_ebooks(category_filter: str = "All", search_term: str = ""):
    """Fetch all ebooks stored in MySQL database."""
    ensure_ebooks_table_exists()
    sql = "SELECT * FROM ebooks WHERE 1=1"
    params = []
    if category_filter and category_filter != "All":
        sql += " AND category = %s"
        params.append(category_filter)
    if search_term and search_term.strip():
        st_term = f"%{search_term.strip()}%"
        sql += " AND (title LIKE %s OR author LIKE %s OR description LIKE %s OR category LIKE %s)"
        params.extend([st_term, st_term, st_term, st_term])
    sql += " ORDER BY ebook_id DESC"
    return execute_query(sql, params)


def add_ebook_to_db(title: str, author: str, category: str = "General",
                    publication_year: str = "2024", isbn: str = "",
                    cover_url: str = "", read_url: str = "",
                    download_url: str = "", format_type: str = "PDF / EPUB",
                    file_size: str = "3.5 MB", description: str = "",
                    content_preview: str = "", added_by: str = "User"):
    """Insert a new e-book into MySQL database."""
    ensure_ebooks_table_exists()
    if not title or not title.strip():
        return False, "E-Book title is required."
    if not author or not author.strip():
        return False, "Author is required."

    # Fallback cover
    final_cover = cover_url.strip() if cover_url and cover_url.strip() else "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80"
    final_read = read_url.strip() if read_url and read_url.strip() else "https://openlibrary.org"

    sql = """
        INSERT INTO ebooks (title, author, category, publication_year, isbn, cover_url, read_url, download_url, format, file_size, description, content_preview, added_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        _, new_id = execute_non_query(sql, (
            title.strip(),
            author.strip(),
            category.strip() if category else "General",
            publication_year.strip() if publication_year else "2024",
            isbn.strip() if isbn else f"EB-{int(new_id) if 'new_id' in locals() else 'NEW'}",
            final_cover,
            final_read,
            download_url.strip() if download_url else None,
            format_type.strip() if format_type else "PDF / EPUB",
            file_size.strip() if file_size else "3.5 MB",
            description.strip(),
            content_preview.strip(),
            added_by.strip() if added_by else "User"
        ))
        return True, f"E-Book '{title}' added to digital library! (ID: #{new_id})"
    except Exception as e:
        return False, f"Database error adding e-book: {str(e)}"


def increment_ebook_stat(ebook_id: int, stat_type: str = "views"):
    """Increment either views_count or downloads_count for an ebook in MySQL."""
    col = "downloads_count" if stat_type == "downloads" else "views_count"
    sql = f"UPDATE ebooks SET {col} = {col} + 1 WHERE ebook_id = %s"
    try:
        execute_non_query(sql, (ebook_id,))
    except Exception:
        pass


def delete_ebook_from_db(ebook_id: int):
    """Delete an e-book from MySQL."""
    sql = "DELETE FROM ebooks WHERE ebook_id = %s"
    try:
        execute_non_query(sql, (ebook_id,))
        return True, "E-Book deleted successfully from library collection."
    except Exception as e:
        return False, f"Error deleting e-book: {str(e)}"


def search_all_ebooks(query: str = "", category_filter: str = "All"):
    """
    Unified multi-source search combining MySQL Database E-Books, Curated collection,
    and public Open Library & Project Gutenberg APIs.
    """
    combined = []
    existing_titles = set()

    # 1. First, fetch persistent e-books stored in MySQL
    try:
        db_rows = get_db_ebooks(category_filter=category_filter, search_term=query)
        for r in db_rows:
            t_key = r["title"].strip().lower()
            existing_titles.add(t_key)
            combined.append({
                "id": f"db-{r['ebook_id']}",
                "db_id": r["ebook_id"],
                "is_db_stored": True,
                "title": r["title"],
                "authors": r["author"],
                "subject": r["category"],
                "year": r["publication_year"],
                "isbn": r["isbn"] or f"EB-{r['ebook_id']}",
                "cover_url": r["cover_url"] or "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80",
                "read_url": r["read_url"],
                "download_url": r["download_url"],
                "epub_url": r["download_url"],
                "format": r.get("format", "PDF / EPUB"),
                "file_size": r.get("file_size", "3.5 MB"),
                "description": r["description"] or "",
                "sample_content": r["content_preview"] or "",
                "source": f"Digital Library ({r.get('added_by', 'Collection')})",
                "views_count": r.get("views_count", 0),
                "downloads_count": r.get("downloads_count", 0),
                "added_by": r.get("added_by", "System"),
                "created_at": str(r.get("created_at", ""))
            })
    except Exception as e:
        print(f"Could not read from ebooks table: {e}")

    # 2. Add fallback curated ebooks if not already present
    for item in CURATED_EBOOKS:
        t_key = item["title"].strip().lower()
        if t_key not in existing_titles:
            match_cat = category_filter == "All" or category_filter.lower() in item["subject"].lower()
            match_q = (
                not query
                or query.lower() in item["title"].lower()
                or query.lower() in item["authors"].lower()
                or query.lower() in item["subject"].lower()
            )
            if match_cat and match_q:
                combined.append(item)
                existing_titles.add(t_key)

    # 3. If user provided a specific search query, fetch from Open Library and Gutendex
    if query and len(query.strip()) >= 2:
        ol_results = search_openlibrary_api(query.strip())
        gt_results = search_gutendex_api(query.strip())

        for item in gt_results + ol_results:
            t_key = item["title"].strip().lower()
            if t_key not in existing_titles:
                combined.append(item)
                existing_titles.add(t_key)

    return combined



@st.cache_data(ttl=3600, show_spinner=False)
def fetch_remote_text(url: str, max_chars: int = 15000):
    """Fetch sample text content from Project Gutenberg text URL with safety limit."""
    if not url:
        return ""
    req = urllib.request.Request(url, headers=API_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=7) as resp:
            raw = resp.read(max_chars).decode("utf-8", errors="ignore")
            return raw
    except Exception as e:
        return f"Could not stream text preview directly ({e}). Please click 'Open Full Reader' above."


# =============================================================================
# PERSISTENT STUDENT STUDY NOTES & BOOKMARKS (MYSQL DATABASE)
# =============================================================================

def save_study_note(member_id: int, book_title: str, book_author: str, ebook_id: str, notes: str):
    """Save or update student personal study notes in MySQL."""
    if not member_id or not notes.strip():
        return False, "Notes cannot be empty."

    # Check if a note for this book already exists
    existing = execute_query(
        "SELECT note_id FROM student_study_notes WHERE member_id = %s AND ebook_id = %s",
        (member_id, ebook_id),
        fetchone=True
    )

    if existing:
        sql = "UPDATE student_study_notes SET notes = %s, last_studied = CURRENT_TIMESTAMP WHERE note_id = %s"
        execute_non_query(sql, (notes.strip(), existing["note_id"]))
        return True, "Study notes updated successfully!"
    else:
        sql = """
            INSERT INTO student_study_notes (member_id, book_title, book_author, ebook_id, notes)
            VALUES (%s, %s, %s, %s, %s)
        """
        execute_non_query(sql, (member_id, book_title.strip(), book_author.strip(), ebook_id, notes.strip()))
        return True, "New study note created and saved!"


def get_study_notes(member_id: int):
    """Retrieve all study notes taken by a student member."""
    sql = """
        SELECT note_id, book_title, book_author, ebook_id, notes, last_studied
        FROM student_study_notes
        WHERE member_id = %s
        ORDER BY last_studied DESC
    """
    return execute_query(sql, (member_id,))


def delete_study_note(note_id: int, member_id: int):
    """Delete a specific study note."""
    sql = "DELETE FROM student_study_notes WHERE note_id = %s AND member_id = %s"
    execute_non_query(sql, (note_id, member_id))
    return True
