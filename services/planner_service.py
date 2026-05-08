from models.trip_model import TripRequest, ItineraryResponse
from services.gemini_service import generate_itinerary
import logging

logger = logging.getLogger(__name__)

def create_or_adapt_itinerary(request: TripRequest) -> ItineraryResponse:
    """
    Orchestrates the itinerary generation process.
    This layer can be expanded to include pre-processing (like checking cache)
    or post-processing (like validating the generated locations against an external API).
    """
    logger.info(f"Generating itinerary for destination: {request.destination}, days: {request.num_days}")
    
    if request.replanning_trigger:
        logger.info(f"Dynamic replanning triggered by: {request.replanning_trigger}")
        
    try:
        response = generate_itinerary(request)
        return response
    except Exception as e:
        logger.error(f"Failed to generate itinerary: {e}")
        raise e
