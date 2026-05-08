# pyrefly: ignore [missing-import]
import streamlit as st
import logging

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_api_error(e: Exception) -> None:
    """Handles exceptions from external APIs gracefully."""
    logger.error(f"API Error: {str(e)}")
    st.error(f"We encountered an issue communicating with the AI. Please try again later. Details: {str(e)}")

def handle_parsing_error(e: Exception) -> None:
    """Handles JSON parsing or validation errors."""
    logger.error(f"Parsing Error: {str(e)}")
    st.error("The AI generated an invalid response format. Please try rephrasing your request or replanning.")

def display_warning(msg: str) -> None:
    """Displays a user-friendly warning."""
    st.warning(msg)
