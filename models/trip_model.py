from pydantic import BaseModel, Field
from typing import List, Optional

class TripRequest(BaseModel):
    destination: str
    budget: str
    num_days: int
    group_type: str
    trip_style: str
    accessibility: str
    food_prefs: str
    crowd_tolerance: str
    weather_pref: str
    
    # Context for dynamic replanning
    previous_itinerary: Optional[dict] = None
    replanning_trigger: Optional[str] = None

class Activity(BaseModel):
    time: str = Field(..., description="e.g., 09:00 AM - 11:00 AM")
    title: str = Field(..., description="Name of the activity or place")
    description: str = Field(..., description="Details about the activity")
    cost_estimate: str = Field(..., description="Estimated cost, e.g., $20 or Free")
    accessibility_notes: str = Field(..., description="Notes regarding accessibility for this specific activity")

class FallbackPlan(BaseModel):
    trigger_condition: str = Field(..., description="e.g., Heavy Rain, Overcrowded")
    alternative_activity: Activity = Field(..., description="The alternative activity to do instead")

class DayPlan(BaseModel):
    day_number: int
    theme: str = Field(..., description="e.g., Historical Exploration")
    activities: List[Activity]
    fallback_plans: List[FallbackPlan] = Field(..., description="Proactive alternatives for this day")

class AIDecisionEngine(BaseModel):
    recommendation_reasoning: str = Field(..., description="Why these specific places were selected")
    accessibility_reasoning: str = Field(..., description="How accessibility needs were met")
    crowd_optimization_logic: str = Field(..., description="How crowd tolerance was factored in")
    budget_balancing_logic: str = Field(..., description="How the budget is managed across the trip")
    adaptation_summary: Optional[str] = Field(None, description="If replanning, a summary of what changed and why")

class ItineraryResponse(BaseModel):
    traveler_persona: str = Field(..., description="Inferred persona, e.g., Relaxed Explorer, Budget Backpacker")
    days: List[DayPlan]
    decision_engine: AIDecisionEngine
    total_cost_estimate: str = Field(..., description="Estimated total cost of the trip")
