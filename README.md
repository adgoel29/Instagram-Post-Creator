# Instagram Post Generator

An AI-powered FastAPI application with an interactive web UI that generates Instagram posts with intelligent captions and images using HuggingFace models. Posts are saved to a SQLite database and can be managed with draft/published status tracking.

## Features

- **Caption Generation**: Uses Qwen2.5-7B-Instruct to generate engaging captions and hashtags
- **Image Generation**: Generates custom images using FLUX.1-schnell or Stable Diffusion 3
- **Post Management**: Save posts as drafts and publish them with status tracking
- **Database Storage**: SQLite database stores all generated posts with metadata
- **Interactive Web UI**: Beautiful frontend to view, manage, and publish posts
- **Image Storage**: Generated images saved to `static/images/` folder
- **Swagger Documentation**: Interactive API docs at `/docs`
- **Error Handling**: Comprehensive error handling with descriptive messages

## Tech Stack

- **Framework**: FastAPI + Uvicorn
- **Frontend**: HTML/CSS/JavaScript with responsive design
- **Database**: SQLite3 with post management
- **LLM**: LangChain + HuggingFace Inference API
- **Models**:
  - Caption: `Qwen/Qwen2.5-7B-Instruct`
  - Image: `black-forest-labs/FLUX.1-schnell` (primary) or `stabilityai/stable-diffusion-3-medium` (fallback)
- **Data Validation**: Pydantic
- **Environment**: python-dotenv

## Project Structure

```
instagram_post_generator/
├── main.py              # FastAPI application and endpoints
├── agents.py            # Caption and Image generation agents
├── models.py            # Pydantic models for request/response
├── storage.py           # SQLite database operations
├── index.html           # Interactive web UI
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create from .env.example)
├── posts.db             # SQLite database (auto-created)
├── static/
│   └── images/          # Generated post images
└── README.md            # This file
```

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
cd instagram_post_generator
pip install -r requirements.txt
```

### 2. Set Up HuggingFace Token

Get your API token from [HuggingFace](https://huggingface.co/settings/tokens).

Update `.env` file:
```
HUGGINGFACEHUB_API_TOKEN=your_token_here
```

### 3. Run the Application

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

### 4. Access API Documentation

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Generate Instagram Post

**POST** `/generate-post`

Generate a new Instagram post with AI caption and image. Automatically saves as draft to database.

Request:
```json
{
  "topic": "summer travel",
  "tone": "casual"
}
```

Response:
```json
{
  "id": 1,
  "topic": "summer travel",
  "tone": "casual",
  "caption": "Exploring amazing destinations...",
  "hashtags": ["#travel", "#summer", "#adventure"],
  "image_url": "http://localhost:8000/static/images/post_123.png",
  "status": "draft",
  "created_at": "2026-03-24T10:30:00",
  "posted_at": null
}
```

### 2. Publish Post

**POST** `/post`

Publish a draft post (update status from draft to posted).

Request:
```json
{
  "post_id": 1
}
```

Response:
```json
{
  "post_id": 1,
  "status": "posted",
  "message": "Post successfully published to Instagram!",
  "posted_at": "2026-03-24T10:35:00"
}
```

### 3. Get All Posts

**GET** `/posts`

Retrieve all posts ordered by creation date (newest first).

Response:
```json
[
  {
    "id": 2,
    "topic": "food photography",
    "tone": "professional",
    "caption": "...",
    "hashtags": ["#food", "#photography"],
    "image_url": "http://localhost:8000/static/images/post_456.png",
    "status": "draft",
    "created_at": "2026-03-24T09:00:00",
    "posted_at": null
  },
  {
    "id": 1,
    "topic": "summer travel",
    "tone": "casual",
    "caption": "...",
    "hashtags": ["#travel", "#summer"],
    "image_url": "http://localhost:8000/static/images/post_123.png",
    "status": "posted",
    "created_at": "2026-03-24T08:00:00",
    "posted_at": "2026-03-24T10:35:00"
  }
]
```

### 4. Get Single Post

**GET** `/posts/{post_id}`

Retrieve a specific post by ID.

Response:
```json
{
  "id": 1,
  "topic": "summer travel",
  "tone": "casual",
  "caption": "...",
  "hashtags": ["#travel", "#summer"],
  "image_url": "http://localhost:8000/static/images/post_123.png",
  "status": "posted",
  "created_at": "2026-03-24T08:00:00",
  "posted_at": "2026-03-24T10:35:00"
}
```

### 5. Health Check

**GET** `/health`

Check if the service is running.

Response:
```json
{
  "status": "ok",
  "message": "Instagram Post Generator is running"
}
```

### 6. Serve Frontend

**GET** `/`

Serves the interactive web UI for managing posts.

## Database Schema

SQLite database (`posts.db`) with a single `posts` table:

```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT,
    tone TEXT,
    caption TEXT,
    hashtags TEXT,              -- Stored as comma-separated values
    image_url TEXT,
    status TEXT DEFAULT 'draft', -- Either 'draft' or 'posted'
    created_at TEXT,            -- ISO format timestamp
    posted_at TEXT              -- ISO format timestamp (NULL for drafts)
)
```

## Web UI Features

- **Generate Posts**: Create new posts with topic and tone inputs
- **View Current Post**: See the most recently generated post with image preview
- **Publish Posts**: Convert draft posts to published status
- **Browse History**: View all previously generated posts in a grid
- **Post Details**: Click any previous post to view full details and publish options
- **Status Tracking**: Visual indicators showing draft (orange) vs published (green) status
- **Responsive Design**: Works on desktop and mobile devices

Access the web UI at: `http://localhost:8000`

## Example Usage

### With cURL

```bash
# Generate a post
curl -X POST "http://localhost:8000/generate-post" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "machine learning",
    "tone": "professional"
  }'

# Check health
curl "http://localhost:8000/health"
```

### With Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Generate a post
response = requests.post(
    f"{BASE_URL}/generate-post",
    json={"topic": "AI", "tone": "professional"}
)
post = response.json()
print(f"Caption: {post['caption']}")
print(f"Hashtags: {post['hashtags']}")
```

## Error Handling

The API returns appropriate HTTP status codes:

- **200**: Success
- **400**: Bad request (e.g., post already published)
- **404**: Resource not found
- **500**: Server error (e.g., LLM or image generation failure)

## Environment Variables

- `HUGGINGFACEHUB_API_TOKEN`: Your HuggingFace API token (required)

## Notes

- **Stateless API**: No storage - each request generates fresh content
- **Image Generation**: May take 30-60 seconds depending on server load
- **HuggingFace Token**: Required for accessing both caption and image generation models
- **Tone Options**: Must be either "professional" or "casual"
- **Caption Length**: Limited to 150 words
- **Hashtags**: Generated with 5-10 hashtags per request

## Troubleshooting

### Import Errors

If you encounter import errors, ensure all dependencies are installed:
```bash
pip install --upgrade -r requirements.txt
```

### HuggingFace Token Issues (401 Error)

**If you get "Repository Not Found" or "Invalid username or password" errors:**

1. Verify your token is valid: https://huggingface.co/settings/tokens
2. **Remove quotes from `.env`** — should be `HUGGINGFACEHUB_API_TOKEN=hf_xxxxx` NOT `HUGGINGFACEHUB_API_TOKEN="hf_xxxxx"`
3. Ensure token has "Read" permission level (minimum)
4. The app automatically tries fallback models if the primary one fails
5. Regenerate a new token if issues persist
6. Restart the application after updating `.env`

### Slow Image Generation

- Image generation can be slow on the first run
- Consider timeout settings if using as a service

### JSON Parsing Errors

- The caption agent returns JSON that is parsed with custom extraction logic
- If you encounter parsing issues, check the LLM model is responding correctly

## License

MIT
