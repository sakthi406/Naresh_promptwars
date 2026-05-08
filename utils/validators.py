from typing import Tuple, List, Optional
import re


def validate_trip_inputs(destination: str, num_days: int) -> Tuple[bool, List[str]]:
    """Validates the basic inputs for the trip planner."""
    errors = []
    
    # Destination validation
    if not destination or len(destination.strip()) < 2:
        errors.append("Destination must be at least 2 characters long.")
    elif len(destination.strip()) > 100:
        errors.append("Destination must be less than 100 characters.")
    elif not re.match(r"^[a-zA-Z\s\-\',.]+$", destination.strip()):
        errors.append("Destination contains invalid characters. Use letters, spaces, and basic punctuation only.")
        
    # Days validation
    if not isinstance(num_days, int):
        errors.append("Number of days must be a whole number.")
    elif num_days < 1 or num_days > 14:
        errors.append("Number of days must be between 1 and 14.")
        
    return len(errors) == 0, errors


def validate_budget(budget: str) -> Tuple[bool, Optional[str]]:
    """Validate budget selection."""
    valid_budgets = ["Budget", "Moderate", "Luxury", "No Limit"]
    if budget not in valid_budgets:
        return False, f"Invalid budget. Choose from: {', '.join(valid_budgets)}"
    return True, None


def validate_group_type(group_type: str) -> Tuple[bool, Optional[str]]:
    """Validate group type selection."""
    valid_groups = ["Solo", "Couple", "Family with Kids", "Friends Group", "Seniors"]
    if group_type not in valid_groups:
        return False, f"Invalid group type. Choose from: {', '.join(valid_groups)}"
    return True, None


def validate_trip_style(trip_style: str) -> Tuple[bool, Optional[str]]:
    """Validate trip style selection."""
    valid_styles = ["Relaxed", "Action-Packed", "Cultural Deep-Dive", "Nature Focus"]
    if trip_style not in valid_styles:
        return False, f"Invalid trip style. Choose from: {', '.join(valid_styles)}"
    return True, None


def validate_accessibility(accessibility: str) -> Tuple[bool, Optional[str]]:
    """Validate accessibility selection."""
    valid_options = ["None", "Low Walking", "Wheelchair Accessible", "Stroller Friendly"]
    if accessibility not in valid_options:
        return False, f"Invalid accessibility option. Choose from: {', '.join(valid_options)}"
    return True, None


def validate_food_prefs(food_prefs: str) -> Tuple[bool, Optional[str]]:
    """Validate food preferences."""
    if len(food_prefs.strip()) > 200:
        return False, "Food preferences must be less than 200 characters."
    return True, None


def validate_crowd_tolerance(crowd_tolerance: str) -> Tuple[bool, Optional[str]]:
    """Validate crowd tolerance selection."""
    valid_options = ["High (Don't mind)", "Moderate", "Low (Avoid crowds)"]
    if crowd_tolerance not in valid_options:
        return False, f"Invalid crowd tolerance. Choose from: {', '.join(valid_options)}"
    return True, None


def validate_weather_pref(weather_pref: str) -> Tuple[bool, Optional[str]]:
    """Validate weather preference selection."""
    valid_options = ["Any", "Prefer Indoor if Hot/Rainy", "Love Outdoors Regardless"]
    if weather_pref not in valid_options:
        return False, f"Invalid weather preference. Choose from: {', '.join(valid_options)}"
    return True, None


def validate_complete_form(form_data: dict) -> Tuple[bool, List[str]]:
    """Validate complete form data."""
    errors = []
    
    # Validate destination and days
    is_valid, dest_errors = validate_trip_inputs(form_data.get('destination', ''), form_data.get('num_days', 0))
    if not is_valid:
        errors.extend(dest_errors)
    
    # Validate other fields
    validations = [
        (form_data.get('budget', ''), validate_budget),
        (form_data.get('group_type', ''), validate_group_type),
        (form_data.get('trip_style', ''), validate_trip_style),
        (form_data.get('accessibility', ''), validate_accessibility),
        (form_data.get('food_prefs', ''), validate_food_prefs),
        (form_data.get('crowd_tolerance', ''), validate_crowd_tolerance),
        (form_data.get('weather_pref', ''), validate_weather_pref),
    ]
    
    for value, validator in validations:
        is_valid, error = validator(value)
        if not is_valid and error:
            errors.append(error)
    
    return len(errors) == 0, errors
