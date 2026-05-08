import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
    # Just a warning, not crashing here so Streamlit can start and show a friendly error
    pass
