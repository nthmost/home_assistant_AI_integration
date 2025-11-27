"""Tests for main road trip handler."""

import pytest
from unittest.mock import Mock, patch
from saga_assistant.modules.road_trip.handler import RoadTripHandler
from saga_assistant.modules.road_trip.routing import Location


class TestRoadTripHandler:
    """Test RoadTripHandler."""

    @pytest.fixture
    def handler(self):
        """Create handler with mock home location."""
        home = Location(latitude=37.7749, longitude=-122.4194, address="home")
        return RoadTripHandler(home, unit_system='imperial')

    def test_handler_initialization(self, handler):
        """Test handler initialization."""
        assert handler.home_location.latitude == 37.7749
        assert handler.unit_system == 'imperial'

    def test_from_ha_config(self):
        """Test creating handler from HA config."""
        ha_config = {
            'latitude': 37.7749,
            'longitude': -122.4194,
            'unit_system': {'name': 'imperial'}
        }

        handler = RoadTripHandler.from_ha_config(ha_config)

        assert handler.home_location.latitude == 37.7749
        assert handler.unit_system == 'imperial'

    def test_parse_intent_distance_query(self, handler):
        """Test parsing distance query."""
        intent = handler._parse_intent("how far is the drive to Sacramento?")

        assert intent['type'] == 'distance'
        assert 'Sacramento' in intent['destination']

    def test_parse_intent_travel_time(self, handler):
        """Test parsing travel time query."""
        intent = handler._parse_intent("how long will it take to get to LA?")

        assert intent['type'] == 'travel_time'
        assert 'LA' in intent['destination']

    def test_parse_intent_best_departure(self, handler):
        """Test parsing best departure time query."""
        intent = handler._parse_intent("when should I leave for Tahoe?")

        assert intent['type'] == 'best_departure'
        assert 'Tahoe' in intent['destination']

    def test_parse_intent_poi(self, handler):
        """Test parsing POI query."""
        intent = handler._parse_intent("what landmarks are between here and Yosemite?")

        assert intent['type'] == 'poi'
        assert 'Yosemite' in intent['destination']

    def test_extract_time_constraint(self, handler):
        """Test extracting time constraints."""
        # After
        constraint = handler._extract_time_constraint("best time after 5pm")
        assert constraint == "after 5pm"

        # Before
        constraint = handler._extract_time_constraint("fastest drive before noon")
        assert constraint == "before noon"

        # None
        constraint = handler._extract_time_constraint("when should I leave?")
        assert constraint is None

    def test_extract_num_options(self, handler):
        """Test extracting number of options."""
        # Single number
        num = handler._extract_num_options("what are the 3 best times?")
        assert num == 3

        # Default
        num = handler._extract_num_options("when should I leave?")
        assert num == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
