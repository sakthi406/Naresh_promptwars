import streamlit as st
import logging
from typing import Optional, Dict, Any
from functools import wraps
import traceback

# Configure logging with proper formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tripify.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)


def log_user_action(action: str) -> None:
    """Log user actions for monitoring and debugging."""
    logger.info(f"User action: {action}")


def handle_streamlit_error(func):
    """Decorator to handle Streamlit errors gracefully."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            st.error(f"An unexpected error occurred. Please try again.")
            if st.session_state.get('debug_mode', False):
                with st.expander("Debug Information"):
                    st.code(traceback.format_exc())
            return None
    return wrapper


def handle_api_error(e: Exception) -> str:
    """Handles exceptions from external APIs gracefully."""
    error_msg = str(e)
    logger.error(f"API Error: {error_msg}")
    
    # Categorize errors for better user experience
    if "rate limit" in error_msg.lower():
        return "⏱️ Too many requests. Please wait a moment and try again."
    elif "timeout" in error_msg.lower():
        return "⏱️ Request timed out. Please check your connection and try again."
    elif "connection" in error_msg.lower():
        return "🔌 Connection failed. Please check your internet connection."
    elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
        return "🔑 Invalid API configuration. Please contact support."
    else:
        return f"🤖 Service temporarily unavailable. Please try again later."


def handle_parsing_error(e: Exception) -> str:
    """Handles JSON parsing or validation errors."""
    logger.error(f"Parsing Error: {str(e)}")
    return "📝 The AI generated an invalid response format. Please try rephrasing your request or replanning."


def display_warning(msg: str) -> None:
    """Displays a user-friendly warning with logging."""
    logger.warning(f"User warning: {msg}")
    st.warning(msg)


def display_success(msg: str) -> None:
    """Displays success message with logging."""
    logger.info(f"User success: {msg}")
    st.success(msg)


def validate_session_state() -> bool:
    """Validate session state integrity."""
    try:
        required_keys = ['itinerary', 'current_request']
        for key in required_keys:
            if key not in st.session_state:
                logger.warning(f"Missing session key: {key}")
                return False
        return True
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        return False


def get_user_context() -> Dict[str, Any]:
    """Get user context for logging and personalization."""
    return {
        'session_id': id(st.session_state),
        'has_itinerary': bool(st.session_state.get('itinerary')),
        'current_destination': st.session_state.get('current_request', {}).get('destination', 'Unknown')
    }


def log_performance_metric(metric_name: str, value: float, unit: str = 'seconds') -> None:
    """Log performance metrics for monitoring."""
    logger.info(f"Performance: {metric_name}={value}{unit}")
