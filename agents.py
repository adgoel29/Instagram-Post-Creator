import os
import json
import re
import base64
from io import BytesIO
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
    response = model.invoke(prompt)
    
    # Extract JSON from response
    json_str = extract_json_from_response(response.content)
    caption_data = json.loads(json_str)
    
    return caption_data


def extract_json_from_response(response_text: str) -> str:
    """
    Extract JSON from the model's response.
    Try to find ```json ... ``` block first, then fallback to raw JSON.
    
    Args:
        response_text: The raw response from the model
    
    Returns:
        JSON string
    """
    
    json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()
    
    # Fallback: find first { and last }
    start_idx = response_text.find('{')
    end_idx = response_text.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        return response_text[start_idx:end_idx + 1]
    
    raise ValueError("Could not extract JSON from model response")


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
    
    # Convert PIL image to base64 PNG
    image.save("output.png")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    return img_b64
