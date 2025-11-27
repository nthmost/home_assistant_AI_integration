# Road Trip Planning Module

**Status:** ✅ Complete (v1.0)
**Type:** Saga Assistant Module
**Dependencies:** OSRM, Overpass API, TomTom/HERE (optional for traffic)

## Overview

The Road Trip Planning module enables Saga to answer questions about driving routes, travel times, traffic conditions, and points of interest. This module is fully voice-interactive and supports both detailed and quick response modes.

## Features

### 🚗 Route Calculation
- Calculate distance and travel time to any destination
- Support for geocoding addresses, cities, or landmarks
- Multi-API fallback (OSRM → GraphHopper → distance estimation)
- Automatic unit detection (miles for US, km elsewhere)

### 🚦 Traffic-Aware Timing
- Real-time traffic conditions for immediate departures
- Historical traffic patterns for future departure times
- Incident detection (accidents, road closures, etc.)
- Automatic travel time adjustment based on traffic severity

### ⏰ Smart Departure Time Optimization
- Find optimal departure time within 24-hour window
- Support for time constraints ("after 5pm", "before noon")
- Multiple alternative times ("3 best leaving times")
- Traffic-aware recommendations

### 🏞️ Points of Interest
- Natural landmarks along route (parks, viewpoints, beaches)
- Distance from route and estimated stop duration
- Powered by OpenStreetMap's Overpass API

### ⚡ Quick Question Mode
- Global power phrase: **"Quick question, [your query]"**
- Returns minimal, essential information only
- Works across ALL Saga modules

## Voice Commands

### Distance Queries
```
"How far is the drive to Sacramento?"
→ "The drive to Sacramento is 87 miles via I-80. Takes about 1 hour 30 minutes."

"Quick question, how far to LA?"
→ "382 miles, 6 hours"
```

### Best Departure Time
```
"When should I leave for Lake Tahoe?"
→ "The best time to leave for Lake Tahoe is 6:00am tomorrow. Travel time: 3 hours
   15 minutes via I-80. Avoid leaving between 7-9am due to heavy commute traffic."

"What's the fastest drive to Sacramento after 5pm?"
→ "Leave at 6:45pm. Travel time: 1 hour 45 minutes via I-80. Moderate traffic expected."

"What are the 3 best leaving times for San Jose tomorrow?"
→ "1. 5:30am tomorrow - 1 hour 15 minutes (light traffic)
   2. 10:00am tomorrow - 1 hour 30 minutes (moderate traffic)
   3. 7:00pm tomorrow - 1 hour 20 minutes (light traffic)"
```

### Travel Time
```
"How long will it take to get to San Francisco if I leave now?"
→ "The drive to San Francisco takes about 45 minutes via US-101. Heavy traffic
   on 101 northbound. Note: 2 incidents reported along the route."
```

### Points of Interest
```
"What are some interesting natural landmarks between here and Big Sur?"
→ "Along the route to Big Sur, you could stop at:
   1. Natural Bridges State Beach - 12 minutes off route, great for a 30-minute walk
   2. Point Lobos State Reserve - 5 minutes off route, stunning viewpoints
   3. Pfeiffer Beach - 8 minutes off route, purple sand and dramatic rocks"

"Quick question, landmarks to Yosemite?"
→ "Natural Bridges, Moaning Caverns, Knights Ferry"
```

## Quick Question Examples

| Normal Response | Quick Response |
|----------------|----------------|
| "The drive to Sacramento is 87 miles via I-80. Takes about 1 hour 30 minutes with current traffic." | "87 miles, 1.5 hours" |
| "The best time to leave for Lake Tahoe is 6:00am tomorrow. Travel time: 3 hours 15 minutes." | "6:00am tomorrow" |
| "If you leave at 7am, you'll arrive around 9:15am. Travel time: 2 hours 15 minutes via I-80." | "9:15am" |

## Configuration

### API Keys

Create a `.env` file or set environment variables:

```bash
# Optional: Traffic APIs (free tiers available)
TOMTOM_API_KEY=your_tomtom_key
HERE_API_KEY=your_here_key

# Optional: GraphHopper (if you want backup routing)
GRAPHHOPPER_API_KEY=your_graphhopper_key
```

### Free API Limits

- **OSRM** (routing): Unlimited, no API key required
- **Overpass API** (POI): Unlimited, no API key required
- **TomTom** (traffic): 2,500 requests/day free
- **HERE** (traffic): 250,000 transactions/month free
- **GraphHopper** (routing backup): Limited free tier

### Home Location

The module reads your home location from Home Assistant configuration:
```yaml
# configuration.yaml
homeassistant:
  latitude: 37.7749
  longitude: -122.4194
  unit_system: imperial  # or metric
```

## Architecture

### Module Structure
```
saga_assistant/modules/road_trip/
├── __init__.py          # Module exports
├── handler.py           # Main query handler
├── routing.py           # Route calculation, geocoding
├── traffic.py           # Traffic data integration
├── timing.py            # Departure time optimization
├── poi.py               # Points of interest queries
├── config.py            # API configuration
├── PRODUCT_SPEC.md      # Detailed product specification
├── README.md            # This file
└── tests/
    ├── test_routing.py
    ├── test_traffic.py
    ├── test_timing.py
    └── test_poi.py
```

### API Fallback Chain

**Routing:**
1. OSRM (free, OpenStreetMap-based)
2. GraphHopper (free tier)
3. Great circle distance estimate

**Traffic:**
1. TomTom Traffic API
2. HERE Traffic API
3. No traffic data (use base route time)

**POI:**
1. Overpass API (free, OpenStreetMap)
2. (No fallback - return empty)

**Geocoding:**
1. Nominatim (free, OpenStreetMap)
2. (Falls back to routing errors)

## Integration with Saga

### Basic Usage

```python
from saga_assistant.modules.road_trip import RoadTripHandler

# Initialize from Home Assistant config
handler = RoadTripHandler.from_ha_config(ha_config)

# Handle query
response = handler.handle_query("How far is the drive to Sacramento?")
print(response)

# Quick mode
response = handler.handle_query("How far to LA?", quick_mode=True)
print(response)  # "382 miles, 6 hours"
```

### With Intent Parser

The module integrates with Saga's intent parser to detect "quick question" automatically:

```python
from saga_assistant.intent_parser import IntentParser

parser = IntentParser(ha_client)
intent = parser.parse("quick question, how far to Sacramento?")

# intent.quick_mode is True
response = handler.handle_query(intent.data['query'], quick_mode=intent.quick_mode)
```

## Testing

Run the test suite:

```bash
# Run all tests
pipenv run pytest saga_assistant/modules/road_trip/tests/

# Run specific test file
pipenv run pytest saga_assistant/modules/road_trip/tests/test_routing.py

# Run with coverage
pipenv run pytest --cov=saga_assistant/modules/road_trip
```

## Limitations & Future Work

### Current Limitations
- No multi-stop trip planning (only A→B)
- No alternative route options (scenic, avoid tolls, etc.)
- No persistent trip memory
- No real-time location tracking
- Traffic data limited to API availability

### Future Enhancements (Bookmarked)
- **Persistence**: Remember frequently asked routes, save favorite destinations
- **Multi-stop planning**: "I'm going to X, then Y, then back home"
- **Voice preferences**: Set route preferences via voice commands
- **Advanced routing**: Scenic routes, avoid highways/tolls, EV charging stops
- **Notifications**: Alert when traffic changes for planned trips
- **Multi-modal**: Public transit, bike routes, walking directions

## Error Handling

### Geocoding Failures
```
"I couldn't find that location. Could you be more specific?
Try including the city or state."
```

### Routing Failures
```
"I couldn't calculate a route to that location.
It might be unreachable by car or too far away."
```

### API Unavailable
```
"I can't get current traffic data right now. Based on distance alone,
the drive to X is about 87 miles, typically takes 1.5 hours."
```

### Edge Cases
- **Destination = Home**: "You're already home!"
- **Very close (<5 miles)**: "That's just 2 miles away - about 5 minutes by car."
- **Very far (>500 miles)**: "That's a long drive - 847 miles. About 13 hours. Consider breaking it into multiple days."

## Logging

The module uses Python's `logging` module with appropriate levels:

```python
import logging

# Enable debug logging for development
logging.basicConfig(level=logging.DEBUG)

# Production: INFO or WARNING
logging.basicConfig(level=logging.INFO)
```

## Performance

- **Simple route query**: < 2 seconds
- **Traffic-aware query**: < 5 seconds
- **Departure time optimization**: 10-30 seconds (evaluates multiple time windows)
- **POI search**: < 10 seconds

## Contributing

When adding features or fixing bugs:

1. Update the product spec (`PRODUCT_SPEC.md`) if behavior changes
2. Add tests for new functionality
3. Update this README with new commands or features
4. Follow the project's Python standards (see `/CLAUDE.md`)

## Support

For issues or questions:
- Check the product spec: `PRODUCT_SPEC.md`
- Review test cases in `tests/`
- See main project docs: `/README.md`

---

**Built with ❤️ for Saga Assistant**
