import json
import logging
import os
import time
import requests
from typing import Optional
from config.settings import GEMINI_API_KEY
from prompts.system_prompt import SYSTEM_PROMPT
from models.trip_model import TripRequest, ItineraryResponse
from utils.sanitizers import extract_json
from pydantic import ValidationError
from utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Rate limiting: 60 requests per minute
rate_limiter = RateLimiter(60, 60)

def generate_itinerary(request: TripRequest) -> ItineraryResponse:
    """Generate travel itinerary with enhanced error handling and rate limiting."""
    # Rate limiting
    rate_limiter.wait_if_needed()
    
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        logger.error("GROQ_API_KEY not configured")
        raise ValueError("GROQ_API_KEY not set. Get free key at https://console.groq.com")

    # Build prompt with validation
    prompt = _build_prompt(request)
    
    # Log request for monitoring
    logger.info(f"Generating itinerary for {request.destination} ({request.num_days} days)")

    try:
        response = _make_api_request(prompt, api_key)
        return _parse_response(response)
        
    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        raise
    except requests.exceptions.Timeout:
        logger.error("API request timeout")
        raise ValueError("Request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        logger.error("API connection error")
        raise ValueError("Connection failed. Please check your internet and try again.")
    except Exception as e:
        logger.error(f"Unexpected error in generate_itinerary: {e}")
        raise Exception(f"Generation failed: {str(e)}")


def _build_prompt(request: TripRequest) -> str:
    """Build the prompt for the AI request."""
    prompt = (
        f"Destination: {request.destination} | Budget: {request.budget} | "
        f"Days: {request.num_days} | Group: {request.group_type} | "
        f"Style: {request.trip_style} | Accessibility: {request.accessibility} | "
        f"Food: {request.food_prefs} | Crowds: {request.crowd_tolerance} | "
        f"Weather: {request.weather_pref}"
    )

    if request.replanning_trigger and request.previous_itinerary:
        summary = []
        for d in request.previous_itinerary.get("days", []):
            acts = [a["title"] for a in d.get("activities", [])]
            summary.append(f"Day {d['day_number']} ({d['theme']}): {', '.join(acts)}")
        prompt += (
            f"\n\nREPLAN TRIGGER: {request.replanning_trigger}"
            f"\nExisting plan:\n" + "\n".join(summary) +
            "\nAdapt itinerary for this trigger. Fill adaptation_summary."
        )
    
    return prompt


def _make_api_request(prompt: str, api_key: str) -> requests.Response:
    """Make API request with proper error handling."""
    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Tripify/1.0"
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            timeout=30  # Reduced timeout for better UX
        )

        if response.status_code == 429:
            logger.warning("Rate limit hit")
            raise ValueError("Rate limit exceeded. Please wait 10 seconds and try again.")
        elif response.status_code == 401:
            logger.error("Invalid API key")
            raise ValueError("Invalid API key. Please check your configuration.")
        elif response.status_code != 200:
            logger.error(f"API error {response.status_code}: {response.text[:200]}")
            raise ValueError(f"Groq API error {response.status_code}: {response.text[:200]}")

        return response
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception: {e}")
        raise


def _parse_response(response: requests.Response) -> ItineraryResponse:
    """Parse API response with comprehensive error handling."""
    try:
        data = response.json()
        text = data["choices"][0]["message"]["content"]
        cleaned = extract_json(text)

        if not cleaned:
            logger.error("No JSON found in response")
            raise ValueError("No valid JSON found in AI response.")

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise ValueError("AI returned malformed JSON. Please try again.")

        try:
            return ItineraryResponse(**parsed)
        except ValidationError as e:
            logger.error(f"Pydantic validation error: {e}")
            raise ValueError("AI response validation failed. Please try again.")
            
    except (KeyError, IndexError) as e:
        logger.error(f"Response structure error: {e}")
        raise ValueError("Invalid API response structure. Please try again.")