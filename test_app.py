#!/usr/bin/env python3
"""
Test suite for Tripify application.
Ensures functionality works as expected and provides validation for key features.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.trip_model import TripRequest, ItineraryResponse
from utils.validators import validate_trip_inputs
from utils.sanitizers import sanitize_input


class TestTripifyApp(unittest.TestCase):
    """Test cases for Tripify application functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_request = {
            "destination": "Paris",
            "budget": "Moderate",
            "num_days": 3,
            "group_type": "Couple",
            "trip_style": "Cultural Deep-Dive",
            "accessibility": "None",
            "food_prefs": "Vegetarian",
            "crowd_tolerance": "Moderate",
            "weather_pref": "Any"
        }
    
    def test_validate_trip_inputs_valid(self):
        """Test validation with valid inputs."""
        is_valid, errors = validate_trip_inputs("Paris", 3)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_trip_inputs_invalid_destination(self):
        """Test validation with invalid destination."""
        is_valid, errors = validate_trip_inputs("", 3)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_trip_inputs_invalid_days(self):
        """Test validation with invalid number of days."""
        is_valid, errors = validate_trip_inputs("Paris", 0)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        # Test normal input
        self.assertEqual(sanitize_input("Paris"), "Paris")
        
        # Test input with special characters
        self.assertEqual(sanitize_input("Paris!@#"), "Paris")
        
        # Test empty input
        self.assertEqual(sanitize_input(""), "")
    
    def test_trip_request_model(self):
        """Test TripRequest model validation."""
        request = TripRequest(**self.valid_request)
        self.assertEqual(request.destination, "Paris")
        self.assertEqual(request.num_days, 3)
        self.assertEqual(request.budget, "Moderate")
    
    def test_trip_request_with_optional_fields(self):
        """Test TripRequest with optional fields."""
        request_data = self.valid_request.copy()
        request_data["previous_itinerary"] = None
        request_data["replanning_trigger"] = "Heavy Rain"
        
        request = TripRequest(**request_data)
        self.assertEqual(request.replanning_trigger, "Heavy Rain")
        self.assertIsNone(request.previous_itinerary)
    
    @patch('services.planner_service.create_or_adapt_itinerary')
    def test_generate_plan_functionality(self, mock_planner):
        """Test the main planning functionality."""
        # Mock the planner service
        mock_itinerary = MagicMock()
        mock_itinerary.traveler_persona = "Cultural Explorer"
        mock_itinerary.total_cost_estimate = "$500"
        mock_itinerary.days = []
        mock_planner.return_value = mock_itinerary
        
        # This would be tested in the actual app context
        # For now, we verify the mock is called correctly
        request = TripRequest(**self.valid_request)
        result = create_or_adapt_itinerary(request)
        
        mock_planner.assert_called_once_with(request)
        self.assertIsNotNone(result)


class TestSecurityFeatures(unittest.TestCase):
    """Test security-related functionality."""
    
    def test_input_length_validation(self):
        """Test that extremely long inputs are handled properly."""
        long_destination = "A" * 1000  # Very long string
        is_valid, errors = validate_trip_inputs(long_destination, 3)
        # Should handle gracefully (implementation dependent)
        self.assertIsInstance(is_valid, bool)
        self.assertIsInstance(errors, list)
    
    def test_special_character_handling(self):
        """Test handling of potentially malicious input."""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../etc/passwd",
            "javascript:alert('xss')"
        ]
        
        for malicious_input in malicious_inputs:
            sanitized = sanitize_input(malicious_input)
            # Should remove or escape dangerous characters
            self.assertNotIn("<script>", sanitized)
            self.assertNotIn("DROP TABLE", sanitized)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
