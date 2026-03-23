from datetime import datetime
from typing import Dict, Any, List

# In-memory storage for posts
posts_db: Dict[int, Dict[str, Any]] = {}
post_counter: int = 0


def create_post(topic: str, tone: str, caption: str, hashtags: List[str], image_base64: str) -> int:
    """Create a new post and store it in the database."""
    global post_counter
    post_counter += 1
    post_id = post_counter
    
    posts_db[post_id] = {
        "id": post_id,
        "topic": topic,
        "tone": tone,
        "caption": caption,
        "hashtags": hashtags,
        "image_base64": image_base64,
        "status": "draft",
        "created_at": datetime.now(),
        "posted_at": None,
    }
    return post_id


def get_post(post_id: int) -> Dict[str, Any] | None:
    """Retrieve a post by ID."""
    return posts_db.get(post_id)


def get_all_posts() -> List[Dict[str, Any]]:
    """Retrieve all posts."""
    return list(posts_db.values())


def update_post_status(post_id: int, status: str, posted_at: datetime = None) -> bool:
    """Update post status."""
    if post_id not in posts_db:
        return False
    posts_db[post_id]["status"] = status
    if posted_at:
        posts_db[post_id]["posted_at"] = posted_at
    return True
