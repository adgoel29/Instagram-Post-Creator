import os
import json
import re
import uuid
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from huggingface_hub import InferenceClient


def setup_caption_agent():
    """Set up the Caption Agent with LangChain and HuggingFace."""
    llm = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-7B-Instruct",
        task="text-generation",
        max_new_tokens=300,
        temperature=0.7,
    )
    model = ChatHuggingFace(llm=llm)
    return model


def generate_caption(topic: str, tone: str) -> dict:
    """
    Generate caption and hashtags using the Caption Agent.
    
    Args:
        topic: The topic for the Instagram post
        tone: whatever tone you want (e.g. "professional", "casual")
    
    Returns:
        Dictionary with 'caption' and 'hashtags' keys
    """
    model = setup_caption_agent()
    
    prompt_template = ChatPromptTemplate.from_template(
        """You are an expert Instagram content creator. Generate an engaging Instagram post caption and hashtags.

Topic: {topic}
Tone: {tone}

Return ONLY valid JSON in this exact format (no other text before or after):
{{
  "caption": "string (max 150 words)",
  "hashtags": ["list of 5-10 hashtags, each starting with #"]
}}

JSON:"""
    )
    
    prompt = prompt_template.format(topic=topic, tone=tone)
    
    try:
        response = model.invoke(prompt)
        
        # Extract JSON from response
        json_str = extract_json_from_response(response.content)
        caption_data = json.loads(json_str)
        
        # Validate the response structure
        if "caption" not in caption_data or "hashtags" not in caption_data:
            raise ValueError("Response missing required 'caption' or 'hashtags' fields")
        
        # Ensure hashtags is a list
        if not isinstance(caption_data["hashtags"], list):
            caption_data["hashtags"] = [str(caption_data["hashtags"])]
        
        return caption_data
    
    except (json.JSONDecodeError, ValueError) as e:
        # Fallback: Generate a basic caption and hashtags
        print(f"Warning: JSON parsing failed for topic '{topic}' and tone '{tone}': {str(e)}")
        print("Using fallback caption generation...")
        
        fallback_caption = f"Discover the beauty of {topic}. {tone.capitalize()} perspective on this amazing subject. #explore #create"
        fallback_hashtags = generate_fallback_hashtags(topic, tone)
        
        return {
            "caption": fallback_caption,
            "hashtags": fallback_hashtags
        }


def generate_fallback_hashtags(topic: str, tone: str) -> list:
    """
    Generate fallback hashtags if AI generation fails.
    
    Args:
        topic: The topic for the Instagram post
        tone: The tone of the post
    
    Returns:
        List of hashtags
    """
    # Base hashtags from topic
    topic_tags = []
    for word in topic.lower().split():
        if len(word) > 3:  # Only add meaningful words
            topic_tags.append(f"#{word}")
    
    # Tone-based hashtags
    tone_tags = {
        "sad": ["#emotional", "#reflective", "#deep"],
        "depressing": ["#emotional", "#reflective", "#deep"],
        "happy": ["#positive", "#joy", "#vibrant"],
        "casual": ["#casual", "#everyday", "#relatable"],
        "professional": ["#professional", "#quality", "#expert"],
        "funny": ["#humor", "#funny", "#laugh"],
        "inspiring": ["#inspiring", "#motivation", "#impact"],
    }
    
    tone_based = tone_tags.get(tone.lower(), ["#creative", "#content"])
    
    # Combine and limit to 8-10 tags
    all_tags = topic_tags + tone_based + ["#instagram", "#explore"]
    return list(dict.fromkeys(all_tags))[:10]  # Remove duplicates and limit to 10


def extract_json_from_response(response_text: str) -> str:
    """
    Extract JSON from the model's response with multiple fallback strategies.
    Try to find ```json ... ``` block first, then fallback to raw JSON extraction.
    
    Args:
        response_text: The raw response from the model
    
    Returns:
        JSON string
    
    Raises:
        ValueError: If JSON cannot be extracted or parsed
    """
    
    # Try 1: Look for ```json ... ``` code block
    json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1).strip()
        try:
            json.loads(json_str)  # Validate it's valid JSON
            return json_str
        except json.JSONDecodeError:
            pass  # Continue to next strategy
    
    # Try 2: Look for ``` ... ``` code block (without json label)
    json_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1).strip()
        try:
            json.loads(json_str)  # Validate it's valid JSON
            return json_str
        except json.JSONDecodeError:
            pass  # Continue to next strategy
    
    # Try 3: Find first { and last } - basic extraction
    start_idx = response_text.find('{')
    end_idx = response_text.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        json_str = response_text[start_idx:end_idx + 1].strip()
        try:
            json.loads(json_str)  # Validate it's valid JSON
            return json_str
        except json.JSONDecodeError:
            # Try to fix common issues
            json_str = fix_json_formatting(json_str)
            try:
                json.loads(json_str)  # Validate again
                return json_str
            except json.JSONDecodeError:
                pass  # Continue to next strategy
    
    raise ValueError(f"Could not extract valid JSON from model response: {response_text[:200]}...")


def fix_json_formatting(json_str: str) -> str:
    """
    Fix common JSON formatting issues from model responses.
    
    Args:
        json_str: Potentially malformed JSON string
    
    Returns:
        Fixed JSON string
    """
    # Remove trailing commas before ] or }
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Fix unquoted keys (basic approach)
    json_str = re.sub(r'(\{|,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
    
    # Fix single quotes to double quotes (be careful with apostrophes in text)
    # Only fix quotes that are clearly JSON structure quotes
    json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)
    json_str = re.sub(r"'([^']*)',", r'"\1",', json_str)
    
    return json_str


def setup_image_agent():
    """Set up the Image Agent with HuggingFace InferenceClient."""
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    client = InferenceClient(token=api_token)
    return client


def generate_image(topic: str, tone: str) -> str:
    """
    Generate an image using the Image Agent.
    
    Args:
        topic: The topic for the image
        tone: The tone/style for the image (e.g. "professional", "casual")
    
    Returns:
        Base64 encoded PNG image string
    """
    client = setup_image_agent()
    
    # Build image prompt
    image_prompt = f"A {tone} style Instagram photo about {topic}, high quality, aesthetic, 4k"
    
    # Try primary model first (FLUX.1-schnell)
    try:
        image = client.text_to_image(
            prompt=image_prompt,
            model="black-forest-labs/FLUX.1-schnell"
        )
    except Exception as e:
        # Fallback to Stable Diffusion 3 if available
        try:
            image = client.text_to_image(
                prompt=image_prompt,
                model="stabilityai/stable-diffusion-3-medium"
            )
        except Exception as fallback_error:
            raise RuntimeError(
                f"Image generation failed. Primary model error: {str(e)}. "
                f"Fallback error: {str(fallback_error)}. "
                f"Ensure your HuggingFace token has access to image generation models."
            )
    
    # Save image to disk
    os.makedirs("static/images", exist_ok=True)
    filename = f"static/images/{uuid.uuid4()}.png"
    image.save(filename)
    return filename
