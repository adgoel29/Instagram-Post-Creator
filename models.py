from pydantic import BaseModel, Field
from typing import List, Optional


class GenerateRequest(BaseModel):
    """Request model for generating an Instagram post."""
    topic: str = Field(..., description="Topic for the Instagram post")
    tone: str = Field(..., description="Tone of the post")


class GenerateResponse(BaseModel):
    """Response model for generated Instagram post."""
    id: int
    topic: str
    tone: str
    caption: str
    hashtags: List[str]
    image_url: str
    status: str
    created_at: str
    posted_at: Optional[str] = None


class PostRequest(BaseModel):
    """Request model for publishing a post."""
    post_id: int


class PostResponse(BaseModel):
    """Response model for post publication."""
    post_id: int
    status: str
    message: str
    posted_at: str
