import urllib.parse

def get_google_maps_search_url(query: str) -> str:
    """Generates a Google Maps search URL for a given query."""
    base_url = "https://www.google.com/maps/search/?api=1&query="
    return base_url + urllib.parse.quote(query)

def get_google_maps_directions_url(origin: str, destination: str) -> str:
    """Generates a Google Maps directions URL."""
    base_url = "https://www.google.com/maps/dir/?api=1"
    query = f"&origin={urllib.parse.quote(origin)}&destination={urllib.parse.quote(destination)}"
    return base_url + query
