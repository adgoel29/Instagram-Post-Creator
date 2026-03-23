import sqlite3
from datetime import datetime

DB_NAME = "posts.db"


def init_db():
    """Initialize database and create posts table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            tone TEXT,
            caption TEXT,
            hashtags TEXT,
            image_url TEXT,
            status TEXT DEFAULT 'draft',
            created_at TEXT,
            posted_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def row_to_dict(cursor, row) -> dict:
    """Convert sqlite3 row to dict using cursor.description."""
    result = {}
    for i, col in enumerate(cursor.description):
        col_name = col[0]
        value = row[i]
        if col_name == "hashtags" and value:
            result[col_name] = value.split(",")
        else:
            result[col_name] = value
    return result


def save_post(topic: str, tone: str, caption: str, hashtags: list, image_url: str) -> int:
    """Save a new post to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    hashtags_str = ",".join(hashtags)
    created_at = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO posts (topic, tone, caption, hashtags, image_url, status, created_at, posted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (topic, tone, caption, hashtags_str, image_url, "draft", created_at, None))
    
    conn.commit()
    post_id = cursor.lastrowid
    conn.close()
    
    return post_id


def get_post(post_id: int) -> dict | None:
    """Retrieve a single post by ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    return row_to_dict(cursor, row) if row else None


def get_all_posts() -> list[dict]:
    """Retrieve all posts ordered by created_at descending."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM posts ORDER BY created_at DESC")
    rows = cursor.fetchall()
    
    conn.close()
    
    return [row_to_dict(cursor, row) for row in rows]


def mark_as_posted(post_id: int) -> dict:
    """Mark a post as published and set posted_at timestamp."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    posted_at = datetime.utcnow().isoformat()
    
    cursor.execute("""
        UPDATE posts SET status = ?, posted_at = ? WHERE id = ?
    """, ("posted", posted_at, post_id))
    
    conn.commit()
    conn.close()
    
    return get_post(post_id)
