import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from models import GenerateRequest, GenerateResponse
from agents import generate_caption, generate_image

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Instagram Post Generator",
    description="Generate Instagram posts with AI-powered captions and images using HuggingFace models",
    version="1.0.0"
)


@app.post("/generate-post", response_model=GenerateResponse, tags=["Post Generation"])
async def generate_post(request: GenerateRequest):
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
        image_base64 = generate_image(request.topic, request.tone)
        
        return GenerateResponse(
            topic=request.topic,
            tone=request.tone,
            caption=caption,
            hashtags=hashtags,
            image_base64=image_base64
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"JSON parsing error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate post: {str(e)}")



@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Instagram Post Generator is running"}
