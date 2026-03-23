from pydantic import BaseModel, Field
from typing import List


class GenerateRequest(BaseModel):
    """Request model for generating an Instagram post."""
    topic: str = Field(..., description="Topic for the Instagram post")
    tone: str = Field(..., description="Tone of the post")


class GenerateResponse(BaseModel):
    """Response model for generated Instagram post."""
    topic: str
    tone: str
    caption: str
    hashtags: List[str]
    image_base64: str
