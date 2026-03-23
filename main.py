import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from dotenv import load_dotenv

from models import GenerateRequest, GenerateResponse, PostRequest, PostResponse
from agents import generate_caption, generate_image
from storage import init_db, save_post, get_post, get_all_posts, mark_as_posted

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Instagram Post Generator",
    description="Generate Instagram posts with AI-powered captions and images using HuggingFace models",
    version="1.0.0"
)
os.makedirs("static/images", exist_ok=True)  # create folder at startup if it doesn't exist
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse, tags=["Frontend"])
async def serve_frontend():
    """Serve the frontend UI."""
    return FileResponse("index.html")

init_db()


@app.post("/generate-post", response_model=GenerateResponse, tags=["Post Generation"])
async def generate_post(request: GenerateRequest, http_request: Request):
    """
    Generate a new Instagram post with AI caption and image.
    
    - **topic**: The subject/topic for the post
    - **tone**: Either "professional" or "casual"
    
    Returns generated caption, hashtags, and image.
    """
    try:
        # Call Caption Agent
        caption_data = generate_caption(request.topic, request.tone)
        caption = caption_data["caption"]
        hashtags = caption_data["hashtags"]
        
        # Call Image Agent
        filename = generate_image(request.topic, request.tone)
        
        # Build full URL
        base_url = str(http_request.base_url).rstrip("/")
        image_url = f"{base_url}/{filename}"
        
        # Save post to database
        post_id = save_post(
            topic=request.topic,
            tone=request.tone,
            caption=caption,
            hashtags=hashtags,
            image_url=image_url
        )
        post = get_post(post_id)
        return GenerateResponse(**post)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"JSON parsing error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate post: {str(e)}")


@app.post("/post", response_model=PostResponse, tags=["Post Generation"])
async def publish_post(request: PostRequest):
    """Publish a draft post to Instagram."""
    post = get_post(request.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["status"] == "posted":
        raise HTTPException(status_code=400, detail="Post already published")
    updated = mark_as_posted(request.post_id)
    return PostResponse(
        post_id=updated["id"],
        status=updated["status"],
        message="Post successfully published to Instagram!",
        posted_at=updated["posted_at"]
    )


@app.get("/posts", tags=["Posts"])
async def get_posts():
    """Retrieve all posts."""
    return get_all_posts()


@app.get("/posts/{post_id}", tags=["Posts"])
async def get_single_post(post_id: int):
    """Retrieve a single post by ID."""
    post = get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Instagram Post Generator is running"}
