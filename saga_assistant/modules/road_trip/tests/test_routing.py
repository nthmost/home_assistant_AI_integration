"""Tests for routing functionality."""

import pytest
from unittest.mock import Mock, patch
from saga_assistant.modules.road_trip.routing import (
    geocode,
    calculate_route,
    estimate_route_fallback,
    Location,
    Route,
    GeocodingError,
    RoutingError,
)


class TestGeocoding:
    """Test geocoding functionality."""

    def test_location_creation(self):
        """Test Location dataclass."""
        loc = Location(latitude=37.7749, longitude=-122.4194, address="San Francisco, CA")
        assert loc.latitude == 37.7749
        assert loc.longitude == -122.4194
        assert loc.address == "San Francisco, CA"
        assert loc.to_tuple() == (37.7749, -122.4194)

    @patch('saga_assistant.modules.road_trip.routing.requests.get')
    def test_geocode_nominatim_success(self, mock_get):
        """Test successful geocoding with Nominatim."""
        # Mock response
        mock_get.return_value.json.return_value = [{
            'lat': '37.7749',
            'lon': '-122.4194',
            'display_name': 'San Francisco, California, United States'
        }]
        mock_get.return_value.raise_for_status = Mock()

        result = geocode("San Francisco")

        assert isinstance(result, Location)
        assert result.latitude == 37.7749
        assert result.longitude == -122.4194
        assert "San Francisco" in result.address

    @patch('saga_assistant.modules.road_trip.routing.requests.get')
    def test_geocode_no_results(self, mock_get):
        """Test geocoding with no results."""
        mock_get.return_value.json.return_value = []
        mock_get.return_value.raise_for_status = Mock()

        with pytest.raises(GeocodingError):
            geocode("InvalidLocationXYZ123")


class TestRouting:
    """Test route calculation."""

    def test_route_properties(self):
        """Test Route dataclass properties."""
        route = Route(
            distance_miles=100.0,
            duration_seconds=7200,
            route_name="via I-80"
        )

        assert route.distance_km == pytest.approx(160.934, rel=0.01)
        assert route.duration_minutes == 120
        assert route.duration_hours == 2.0
        assert route.format_duration() == "2 hours"
        assert route.format_distance('imperial') == "100.0 miles"
        assert route.format_distance('metric') == "160.9 km"

    def test_route_duration_formatting(self):
        """Test various duration formats."""
        # Hours only
        route1 = Route(distance_miles=100, duration_seconds=3600, route_name="test")
        assert route1.format_duration() == "1 hour"

        # Hours and minutes
        route2 = Route(distance_miles=100, duration_seconds=5400, route_name="test")
        assert route2.format_duration() == "1 hour 30 minutes"

        # Minutes only
        route3 = Route(distance_miles=10, duration_seconds=1800, route_name="test")
        assert route3.format_duration() == "30 minutes"

    def test_estimate_route_fallback(self):
        """Test fallback route estimation."""
        start = Location(latitude=37.7749, longitude=-122.4194)  # SF
        end = Location(latitude=38.5816, longitude=-121.4944)    # Sacramento

        route = estimate_route_fallback(start, end)

        assert isinstance(route, Route)
        assert route.distance_miles > 0
        assert route.duration_seconds > 0
        assert route.route_name == "estimated route"


class TestIntegration:
    """Integration tests (require network)."""

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires network access")
    def test_full_route_calculation(self):
        """Test full route calculation from geocoding to routing."""
        # This test requires actual API access
        start = Location(latitude=37.7749, longitude=-122.4194)  # SF
        dest = geocode("Sacramento, CA")

        route = calculate_route(start, dest)

        assert route.distance_miles > 50  # At least 50 miles
        assert route.distance_miles < 200  # Less than 200 miles
        assert route.duration_seconds > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
