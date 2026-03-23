# Instagram Post Generator

An AI-powered FastAPI application that generates Instagram posts with intelligent captions and images using HuggingFace models and LangChain.

## Features

- **Caption Generation**: Uses Qwen2.5-7B-Instruct to generate engaging captions and hashtags
- **Image Generation**: Generates custom images using FLUX.1-schnell or Stable Diffusion 3
- **Stateless API**: No storage - generate content on demand
- **Swagger Documentation**: Interactive API docs at `/docs`
- **Base64 Image Output**: Generated images returned as base64 encoded PNG
- **Error Handling**: Comprehensive error handling with descriptive messages

## Tech Stack

- **Framework**: FastAPI + Uvicorn
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
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
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

### Generate Instagram Post

**POST** `/generate-post`

Generate a new Instagram post with caption and image. No storage - content is generated on demand.

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
  "topic": "summer travel",
  "tone": "casual",
  "caption": "...",
  "hashtags": ["#travel", "#summer", ...],
  "image_base64": "iVBORw0KGgoAAAANS..."
}
```

### Health Check

**GET** `/health`

Check if the service is running.

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
