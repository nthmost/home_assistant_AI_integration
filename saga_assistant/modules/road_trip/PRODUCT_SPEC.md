# Road Trip Planning Module - Product Specification

**Module Name:** Road Trip Planning
**Version:** 1.0
**Status:** Planning
**Last Updated:** November 26, 2025

## Overview

The Road Trip Planning module enables Saga to answer questions about driving routes, travel times, traffic conditions, and points of interest along the way. This module focuses on planning trips from the user's home location to various destinations.

## Core Principles

- **Planning-focused**: No real-time location tracking or navigation
- **Home-centric**: "here" always refers to the Home Assistant configured home location
- **LAN-first with selective external APIs**: Use free/low-cost APIs for traffic and routing data
- **Multi-API fallback**: Like the weather module, gracefully degrade when APIs fail
- **Voice-first interaction**: Natural language queries with comprehensive responses

## User Stories

### Basic Route Information
- "How far is the drive to X?"
- "How long will it take to drive to Y?"
- "What's the fastest route to Z?"

### Time-Sensitive Planning
- "When's the best time to leave if I'm driving to X?"
- "How long will it take to reach Y if I leave at 7am tomorrow morning?"
- "If I leave now, how long to get to Z?"
- "What's the shortest drive time to X after 5pm?"
- "What's the fastest drive to Y before noon?"
- "What are the 3 best leaving times to get to Z tomorrow?"

### Points of Interest
- "What are some interesting natural landmarks between here and X?"
- "Are there any good stopping points on the way to Y?"

### Quick Responses
- "Quick question, how far is the drive to X?" → "127 miles"
- "Quick question, when should I leave for Y?" → "6:45am"

## Feature Specifications

### 1. Route Calculation

**Inputs:**
- Destination (address, city, landmark name, or coordinates)
- Optional: departure time (default: now)
- Optional: constraints (after/before time, top N options)

**Outputs:**
- Distance (in miles for US locations, km elsewhere - auto-detected from HA config)
- Estimated travel time
- Primary route description (e.g., "via I-80 and CA-1")

**Behavior:**
- Always default to fastest/quickest route
- Future iterations may add: scenic, avoid highways, avoid tolls

### 2. Traffic-Aware Timing

**Real-Time Traffic (when "now" or immediate departure):**
- Check current traffic conditions
- Check for accidents/incidents along route
- Adjust travel time estimates accordingly
- Report significant delays or issues

**Historical/Typical Patterns:**
- Use historical data for future departure times
- Consider time-of-day patterns (rush hour, etc.)
- Use typical speeds when real-time data unavailable

**Fallback Strategy:**
- Primary: Real-time traffic API
- Secondary: Alternative traffic API
- Fallback: Distance + typical speed estimates (no traffic data)

### 3. Best Departure Time

**Default Behavior:**
- Return single best departure time (shortest total travel time)
- Check next 24 hours in reasonable intervals (every 30-60 minutes)

**With Constraints:**
- "after 5pm" → earliest time after 5pm with shortest travel time
- "before noon" → time before noon with shortest travel time
- "3 best times" → top 3 departure windows with estimated times

**Response Format (Detailed):**
```
The best time to leave for Sacramento is 6:30am tomorrow.
Travel time: 2 hours 15 minutes via I-80.
Light traffic expected. Arriving around 8:45am.

Alternative: Leave at 9:45am for 2 hours 30 minutes (moderate traffic).
```

**Response Format (Quick Question):**
```
6:30am tomorrow
```

### 4. Points of Interest (Natural Landmarks)

**Query Types:**
- Natural landmarks (parks, viewpoints, geological features)
- Ranger stations
- Stopping points (10 minutes to 2 hours duration)

**Filters:**
- Distance from route (default: within 5 miles)
- Suitable for short stops

**Data Sources:**
- National/State Parks
- Scenic viewpoints
- Notable natural features
- Trailheads with short hikes

**Response Format:**
```
Along the route to Yosemite, you could stop at:
1. Natural Bridges State Beach - 15 minutes off route, great for a 30-minute walk
2. Moaning Caverns - 8 miles off route, 45-minute tour available
3. Knights Ferry Recreation Area - 3 miles off route, riverside trails
```

### 5. "Quick Question" Power Phrase

**Global Feature** (applies to ALL Saga modules, not just Road Trip Planning)

**Behavior:**
- When user says "quick question" before their query
- Saga responds with minimal, essential information only
- No elaboration, no alternatives, just the core answer

**Intent Detection:**
- Add `quick_question` flag to intent detection layer
- All modules must respect this flag
- Override default verbose responses

**Examples:**

| Normal Question | Normal Response | Quick Question | Quick Response |
|----------------|----------------|----------------|----------------|
| "What's the weather?" | "Currently 72°F and sunny in San Francisco. High of 78°F today. Clear skies expected through evening. Light winds from the west at 8 mph." | "Quick question, what's the weather?" | "Sunny, 72°F" |
| "How far to LA?" | "The drive to Los Angeles is 382 miles via I-5. Takes about 6 hours with current traffic. Light traffic on I-5, moderate through the Grapevine." | "Quick question, how far to LA?" | "382 miles, 6 hours" |
| "When should I leave for Sacramento?" | "Best time to leave for Sacramento is 6:30am tomorrow. Travel time 2 hours 15 minutes via I-80. Light traffic expected." | "Quick question, when should I leave for Sacramento?" | "6:30am" |

**Implementation Location:**
- Intent detection layer (`saga_assistant/intent/`)
- Documented in main Saga architecture docs
- All modules must implement quick response mode

## Technical Architecture

### API Stack

**Routing & Directions:**
- **Primary:** OSRM (Open Source Routing Machine) - Free, OpenStreetMap-based
  - Self-hostable option available
  - Good for basic routing
- **Secondary:** GraphHopper - Free tier available
- **Tertiary:** Google Maps Directions API (fallback if needed)

**Traffic Data:**
- **Primary:** TomTom Traffic API
  - Free tier: 2,500 requests/day
  - Real-time traffic flow and incidents
- **Secondary:** HERE Traffic API
  - Free tier: 250k transactions/month (hobbyist)
- **Fallback:** Historical patterns + distance/speed estimates

**Points of Interest:**
- **Primary:** Overpass API (OpenStreetMap POI queries)
  - Completely free
  - Rich natural landmark data
  - National/state parks, viewpoints, etc.
- **Secondary:** Google Places API (if needed)

**Geocoding:**
- **Primary:** Nominatim (OpenStreetMap)
  - Free geocoding service
- **Secondary:** Google Geocoding API (fallback)

### Module Structure

```
saga_assistant/modules/road_trip/
├── __init__.py
├── PRODUCT_SPEC.md          # This file
├── README.md                # Technical documentation
├── handler.py               # Main intent handler
├── routing.py               # Route calculation logic
├── traffic.py               # Traffic data fetching
├── timing.py                # Departure time optimization
├── poi.py                   # Points of interest queries
├── config.py                # API keys and configuration
└── tests/
    ├── test_routing.py
    ├── test_traffic.py
    ├── test_timing.py
    └── test_poi.py
```

### Configuration

**Home Assistant Integration:**
- Read home location from HA configuration
- Use HA's zone configuration for "home"
- Auto-detect unit preferences (miles vs km) from HA locale

**User Preferences (Future):**
- Distance units override
- Preferred route types (fastest, scenic, etc.)
- POI categories of interest
- Traffic tolerance (avoid heavy traffic vs shortest time)

**API Configuration:**
```python
# config.py
ROUTING_APIS = {
    'osrm': {
        'enabled': True,
        'base_url': 'https://router.project-osrm.org',
        'priority': 1
    },
    'graphhopper': {
        'enabled': True,
        'api_key': None,  # Optional
        'priority': 2
    }
}

TRAFFIC_APIS = {
    'tomtom': {
        'enabled': True,
        'api_key': 'YOUR_KEY',
        'daily_limit': 2500,
        'priority': 1
    },
    'here': {
        'enabled': True,
        'api_key': 'YOUR_KEY',
        'monthly_limit': 250000,
        'priority': 2
    }
}
```

## Response Patterns

### Detailed Mode (Default)

**Distance Query:**
```
The drive to Sacramento is 87 miles via I-80.
Takes about 1 hour 30 minutes with current traffic.
Light traffic on I-80 eastbound.
```

**Best Time Query:**
```
The best time to leave for Lake Tahoe is 6:00am tomorrow.
Travel time: 3 hours 15 minutes via I-80.
Avoid leaving between 7-9am due to heavy commute traffic.
Arriving around 9:15am.
```

**POI Query:**
```
Along the route to Big Sur, you could stop at:

1. Natural Bridges State Beach
   - 12 minutes off route
   - Great for a 30-minute coastal walk

2. Point Lobos State Reserve
   - 5 minutes off route
   - Stunning viewpoints, 45-minute loop trail

3. Pfeiffer Beach
   - 8 minutes off route
   - Purple sand, dramatic rock formations
```

### Quick Question Mode

**Distance Query:**
```
87 miles, 1.5 hours
```

**Best Time Query:**
```
6:00am tomorrow
```

**POI Query:**
```
Natural Bridges, Point Lobos, Pfeiffer Beach
```

## Error Handling

### API Failures

**All APIs Unavailable:**
```
I can't get current traffic data right now. Based on distance alone,
the drive to X is about [distance] miles, typically takes [time] hours.
```

**Geocoding Failure:**
```
I couldn't find that location. Could you be more specific?
Try including the city or state.
```

**No Route Available:**
```
I couldn't calculate a driving route to that location.
It might be unreachable by car or too far away.
```

### Edge Cases

**Destination = Home:**
```
You're already home!
```

**Very Close Destination (<5 miles):**
```
That's just 2 miles away - about 5 minutes by car.
```

**Very Far Destination (>500 miles):**
```
That's a long drive - 847 miles to Seattle.
About 13 hours of driving. Consider breaking it into multiple days.
```

## Future Enhancements (Bookmarked)

### Persistence & Memory
- Remember frequently asked routes
- Save favorite destinations
- Multi-stop trip planning
- "I'm going to X, then Y, then back home"

### Voice Configuration
- Set preferences via voice commands
- "Saga, I prefer scenic routes"
- "Saga, always avoid toll roads"

### Advanced Route Options
- Scenic routes
- Avoid highways
- Avoid tolls
- EV charging stops
- Gas station planning

### Notifications
- "Alert me if traffic changes for my 7am trip to X"
- Integration with calendar for departure reminders

### Multi-Modal Transport
- Public transit options
- Bike routes
- Walking directions

## Testing Strategy

### Unit Tests
- Route calculation accuracy
- Traffic data parsing
- Time optimization algorithms
- POI filtering and ranking
- API fallback logic

### Integration Tests
- End-to-end query processing
- API failure scenarios
- Multi-API fallback chains
- "Quick question" mode across all query types

### Voice Interaction Tests
- Natural language understanding
- Ambiguous destination handling
- Time constraint parsing
- POI query variations

## Success Metrics

- Accurate travel time estimates (within 10% of actual)
- Fast response time (<2 seconds for cached routes, <5 seconds for new queries)
- API uptime >99% (with fallbacks)
- User satisfaction with "quick question" brevity
- User satisfaction with detailed response comprehensiveness

## Dependencies

- Home Assistant (for home location)
- OSRM / GraphHopper (routing)
- TomTom / HERE (traffic data)
- Overpass API (POI data)
- Saga intent detection layer (for quick question support)

## Timeline Estimate

- **Phase 1:** Basic routing and distance queries (2-3 days)
- **Phase 2:** Traffic integration and timing optimization (2-3 days)
- **Phase 3:** POI queries and natural landmarks (2-3 days)
- **Phase 4:** "Quick question" global feature (1-2 days)
- **Phase 5:** Testing and refinement (2-3 days)

**Total:** ~2 weeks for v1.0

---

**Notes for Future Conversation:**
- Voice-based Saga configuration system
- User preference management
- Long-term route memory and learning
