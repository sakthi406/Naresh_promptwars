import sys
import os
import json
from pydantic import ValidationError

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.sanitizers import extract_json
from models.trip_model import ItineraryResponse

def test_cases():
    print("Starting parser verification tests...\n")
    
    # Case 1: Pure JSON response
    case1 = '{"traveler_persona": "Relaxed Explorer", "days": [], "decision_engine": {"recommendation_reasoning": "Test", "accessibility_reasoning": "Test", "crowd_optimization_logic": "Test", "budget_balancing_logic": "Test", "adaptation_summary": null}, "total_cost_estimate": "$0"}'
    print(f"Testing Case 1 (Pure JSON)...")
    cleaned1 = extract_json(case1)
    try:
        parsed1 = json.loads(cleaned1)
        ItineraryResponse(**parsed1)
        print("[PASSED] Case 1\n")
    except Exception as e:
        print(f"[FAILED] Case 1: {e}\n")

    # Case 2: Markdown wrapped JSON
    case2 = """
Here is your itinerary:
```json
{
  "traveler_persona": "Budget Backpacker",
  "days": [],
  "decision_engine": {
    "recommendation_reasoning": "Test",
    "accessibility_reasoning": "Test",
    "crowd_optimization_logic": "Test",
    "budget_balancing_logic": "Test",
    "adaptation_summary": null
  },
  "total_cost_estimate": "$0"
}
```
Hope you enjoy!
"""
    print(f"Testing Case 2 (Markdown wrapped)...")
    cleaned2 = extract_json(case2)
    try:
        parsed2 = json.loads(cleaned2)
        ItineraryResponse(**parsed2)
        print("[PASSED] Case 2\n")
    except Exception as e:
        print(f"[FAILED] Case 2: {e}\n")

    # Case 3: Malformed JSON
    case3 = '{"traveler_persona": "Broken", "days": ['
    print(f"Testing Case 3 (Malformed JSON)...")
    cleaned3 = extract_json(case3)
    try:
        json.loads(cleaned3)
        print("[FAILED] Case 3 (Should have errored)\n")
    except json.JSONDecodeError:
        print("[PASSED] Case 3 (Correctly caught malformed JSON)\n")

    # Case 4: Missing required fields
    case4 = '{"traveler_persona": "Missing Fields"}'
    print(f"Testing Case 4 (Missing Fields)...")
    cleaned4 = extract_json(case4)
    try:
        parsed4 = json.loads(cleaned4)
        ItineraryResponse(**parsed4)
        print("[FAILED] Case 4 (Should have errored)\n")
    except ValidationError:
        print("[PASSED] Case 4 (Correctly caught validation error)\n")

if __name__ == "__main__":
    test_cases()
