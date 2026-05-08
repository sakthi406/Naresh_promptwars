import re
import json

def sanitize_input(text: str) -> str:
    """Basic sanitization to strip leading/trailing whitespace."""
    if not isinstance(text, str):
        return text
    return text.strip()

def extract_json(text: str) -> str:
    """
    Extracts a JSON string from text, removing markdown fences if present.
    Also handles text before or after the JSON block.
    """
    if not text:
        return ""
    
    # Try to find content between triple backticks
    # We look for ```json ... ``` or just ``` ... ```
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if json_match:
        return json_match.group(1).strip()
    
    # If no backticks, try to find the first '{' and the last '}'
    start = text.find('{')
    end = text.rfind('}')
    
    if start != -1 and end != -1 and end > start:
        return text[start:end+1].strip()
        
    return text.strip()
