import re
import json
import html
from typing import Optional


def sanitize_input(text: str) -> str:
    """Comprehensive input sanitization for security."""
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove potentially dangerous HTML/JS characters
    text = html.escape(text)
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Limit length to prevent buffer overflow
    if len(text) > 1000:
        text = text[:1000]
    
    return text


def sanitize_destination(destination: str) -> str:
    """Sanitize destination input with specific rules."""
    if not isinstance(destination, str):
        return ""
    
    # Basic sanitization
    destination = sanitize_input(destination)
    
    # Allow only letters, spaces, hyphens, apostrophes, and basic punctuation
    destination = re.sub(r'[^a-zA-Z\s\-\',.\u00C0-\uFFFF]', '', destination)
    
    # Remove multiple spaces
    destination = re.sub(r'\s+', ' ', destination)
    
    return destination.strip()


def sanitize_food_prefs(food_prefs: str) -> str:
    """Sanitize food preferences."""
    if not isinstance(food_prefs, str):
        return ""
    
    food_prefs = sanitize_input(food_prefs)
    
    # Allow common food-related characters
    food_prefs = re.sub(r'[^a-zA-Z0-9\s\-\',./\u00C0-\uFFFF]', '', food_prefs)
    
    return food_prefs.strip()


def extract_json(text: str) -> str:
    """
    Extracts a JSON string from text with enhanced security.
    Removes markdown fences and validates JSON structure.
    """
    if not isinstance(text, str) or not text.strip():
        return ""
    
    # Try to find content between triple backticks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text, re.IGNORECASE)
    if json_match:
        return json_match.group(1).strip()
    
    # If no backticks, try to find the first '{' and the last '}'
    start = text.find('{')
    end = text.rfind('}')
    
    if start != -1 and end != -1 and end > start:
        json_str = text[start:end+1].strip()
        
        # Basic JSON validation
        if json_str.startswith('{') and json_str.endswith('}'):
            return json_str
        
    return ""


def validate_json_structure(json_str: str) -> bool:
    """Validate JSON structure without parsing."""
    if not isinstance(json_str, str):
        return False
    
    json_str = json_str.strip()
    
    # Basic structural checks
    if not json_str.startswith('{') or not json_str.endswith('}'):
        return False
    
    # Check for balanced braces
    brace_count = 0
    for char in json_str:
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count < 0:
                return False
    
    return brace_count == 0


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for logging purposes."""
    if not isinstance(filename, str):
        return ""
    
    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'\.\.', '', filename)  # Remove directory traversal
    
    return filename.strip()


def is_safe_input(input_text: str, max_length: int = 1000) -> bool:
    """Check if input is safe for processing."""
    if not isinstance(input_text, str):
        return False
    
    # Length check
    if len(input_text) > max_length or len(input_text) < 1:
        return False
    
    # Check for dangerous patterns
    dangerous_patterns = [
        r'<script[^>]*>',
        r'javascript:',
        r'vbscript:',
        r'onload=',
        r'onerror=',
        r'onclick=',
        r'\x00',
        r'\r\n',
        r'\n\r',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, input_text, re.IGNORECASE):
            return False
    
    return True
