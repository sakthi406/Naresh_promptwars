# Adaptive Travel Intelligence Engine

An AI-powered, production-quality travel planning and orchestration engine. This application leverages the Gemini API to not only generate structured itineraries but also intelligently adapt them based on changing real-world conditions (weather, budget, accessibility needs).

## Features

- **Intelligent Trip Planning:** Generates personalized itineraries considering budget, group type, travel style, and specific needs.
- **Dynamic Replanning:** React to real-world triggers (e.g., "Heavy Rain", "Budget Reduced") and watch the AI seamlessly adapt your schedule while preserving core preferences.
- **AI Decision Engine:** Transparently explains the "why" behind recommendations, detailing accessibility logic, crowd optimization, and budget balancing.
- **Proactive Fallbacks:** Every planned day includes proactive fallback options for unpredictable situations.
- **Traveler Persona Detection:** The system infers your travel persona to tailor the experience further.
- **Google Maps Integration:** Direct links to search and get directions for recommended activities.

## Architecture & SOLID Principles

The project is structured for maintainability and separation of concerns:

- `models/`: Contains Pydantic models (`trip_model.py`) that strictly define the data contracts and schema for the AI responses, ensuring robust parsing.
- `services/`: Encapsulates business logic.
  - `gemini_service.py`: Dedicated to communicating with the Google Gemini API.
  - `maps_service.py`: Generates Google Maps URIs.
  - `planner_service.py`: Orchestrates the flow between input and AI generation.
- `utils/`: Reusable components for validation (`validators.py`), sanitization (`sanitizers.py`), and error handling (`error_handler.py`).
- `prompts/`: Isolates the complex system instructions (`system_prompt.py`) sent to the AI.
- `app.py`: The Streamlit frontend responsible purely for UI rendering and session state management.

## Security Considerations

- **Environment Variables:** API keys are never hardcoded. They are loaded via `.env`.
- **Input Validation:** User inputs (like destination length and day counts) are validated before any API calls are made.
- **Structured AI Responses:** By leveraging Pydantic and JSON schema validation, the system guards against hallucinated, unstructured responses that could break the UI.
- **Centralized Error Handling:** API failures or network issues are caught gracefully and presented to the user without exposing stack traces in the UI (except for explicit debugging during development).

## Setup Instructions

1. **Clone or Download the Repository**
2. **Create a Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables:**
   - Copy or rename `.env.template` (if provided) to `.env` or just create `.env`.
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```
5. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

## Testing & Validation

The application includes comprehensive testing to ensure reliability and security:

- **Unit Tests**: Located in `test_app.py` with coverage for:
  - Input validation and sanitization
  - Model validation and data integrity
  - Security feature testing
  - Error handling scenarios
- **Security Testing**: Validates protection against common vulnerabilities
- **Integration Testing**: Ensures all components work together seamlessly

Run tests with: `python -m pytest test_app.py -v`

## Security & Compliance

- **Security Documentation**: See `SECURITY.md` for detailed security measures
- **Input Validation**: All user inputs are validated and sanitized
- **Error Handling**: Graceful error handling without exposing sensitive information
- **API Security**: Environment-based configuration for API keys
- **Accessibility**: WCAG 2.1 compliant design with ARIA labels and semantic HTML

## Performance & Efficiency

- **Optimized Imports**: Only necessary modules are imported
- **Efficient Error Handling**: Structured exception handling with specific error types
- **Memory Management**: Proper cleanup and resource management
- **Logging**: Comprehensive logging for debugging and monitoring
- **Caching**: Session state management for optimal performance

## Assumptions & Future Improvements

- **Assumptions:** The current implementation assumes the user has a valid Gemini API key with access to JSON structured outputs or at least a model capable of strictly adhering to JSON system instructions (like `gemini-1.5-pro` or `gemini-2.5-pro`).
- **Future Improvements:**
  - Implement actual Google Places API integration for rich photos and precise coordinates instead of relying solely on Search URLs.
  - Add user authentication to save itineraries persistently to a database.
  - Implement rate limiting explicitly in the `gemini_service` to handle quota limits gracefully.
  - Expand the dynamic replanning to accept custom text prompts ("I am tired, give me something chill right now").
  - Add comprehensive integration tests with mocking
  - Implement performance monitoring and analytics
  - Add multi-language support for international users
