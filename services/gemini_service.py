import json
import logging
import os
import requests
from config.settings import GEMINI_API_KEY
from prompts.system_prompt import SYSTEM_PROMPT
from models.trip_model import TripRequest, ItineraryResponse
from utils.sanitizers import extract_json
from pydantic import ValidationError

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"

def generate_itinerary(request: TripRequest) -> ItineraryResponse:
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set. Get free key at https://console.groq.com")

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

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            timeout=60
        )

        if response.status_code == 429:
            raise ValueError("Rate limit. Wait 10 seconds and try again.")
        if response.status_code != 200:
            raise ValueError(f"Groq API error {response.status_code}: {response.text[:200]}")

        data = response.json()
        text = data["choices"][0]["message"]["content"]
        cleaned = extract_json(text)

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            raise ValueError("AI returned malformed JSON. Please try again.")

        try:
            return ItineraryResponse(**parsed)
        except ValidationError as e:
            logger.error(f"Validation: {e}")
            raise ValueError("AI response validation failed. Please try again.")

    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Generation failed: {str(e)}")