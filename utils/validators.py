from typing import Tuple, List

def validate_trip_inputs(destination: str, num_days: int) -> Tuple[bool, List[str]]:
    """Validates the basic inputs for the trip planner."""
    errors = []
    
    if not destination or len(destination.strip()) < 2:
        errors.append("Destination must be at least 2 characters long.")
        
    if num_days < 1 or num_days > 14:
        errors.append("Number of days must be between 1 and 14.")
        
    return len(errors) == 0, errors
