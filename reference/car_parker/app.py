#!/usr/bin/env python3
"""
car-parker: SF street sweeping web app
"""

import logging
from pathlib import Path
from flask import Flask, jsonify, request, render_template
from parking import StreetSweepingLookup, ParkingManager
from parking_geo import TimeLimitLookup, SweepingGeoLookup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Module-level singletons, initialized on first request
_lookup: StreetSweepingLookup = None
_manager: ParkingManager = None
_timelimit: TimeLimitLookup = None
_sweeping_geo: SweepingGeoLookup = None


def get_manager() -> ParkingManager:
    global _lookup, _manager
    if _manager is None:
        _lookup = StreetSweepingLookup()
        _manager = ParkingManager(_lookup)
    return _manager


def get_geo():
    global _timelimit, _sweeping_geo
    if _timelimit is None:
        _timelimit = TimeLimitLookup()
        _sweeping_geo = SweepingGeoLookup()
    return _timelimit, _sweeping_geo


# ── Pages ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


# ── API ────────────────────────────────────────────────────────────────────

@app.route('/api/status')
def api_status():
    try:
        return jsonify(get_manager().get_status())
    except FileNotFoundError as e:
        return jsonify({'error': str(e), 'data_missing': True}), 503


@app.route('/api/park', methods=['POST'])
def api_park():
    """Save parking location.

    Accepts JSON with one of:
      { "lat": 37.77, "lng": -122.46 }                          ← GPS (preferred)
      { "text": "north side of Anza between 7th and 8th" }      ← free text
      { "street": "Anza St", "block": "...", "side": "North" }  ← picker
    """
    data = request.get_json(force=True)
    mgr = get_manager()
    time_limit = None

    if 'lat' in data and 'lng' in data:
        lat, lng = float(data['lat']), float(data['lng'])
        tl_lookup, sw_geo = get_geo()

        # Time limit
        tl = tl_lookup.find_nearest(lat, lng)
        if tl:
            time_limit = tl.to_dict()

        # Sweeping records from geometry
        sw_records = sw_geo.find_nearest_records(lat, lng)
        if sw_records:
            # Derive a ParkingLocation from the first sweeping record
            r = sw_records[0]
            from parking import ParkingLocation
            from datetime import datetime, timezone
            loc = ParkingLocation(
                street=r['corridor'],
                cross_street_1=None,
                cross_street_2=None,
                side=r.get('blockside', 'Unknown'),
                block_limits=r.get('limits'),
                timestamp=datetime.now(timezone.utc).isoformat(),
                raw_input=f"GPS {lat:.5f},{lng:.5f}",
            )
            mgr.save_parking_location(loc, extra={'time_limit': time_limit, 'lat': lat, 'lng': lng})
        else:
            # No sweeping record nearby — save minimal GPS state
            mgr.save_gps_location(lat, lng, time_limit)

    elif 'text' in data:
        location = mgr.parser.parse(data['text'])
        if not location:
            return jsonify({'error': 'Could not parse location. Try: "Anza between 7th and 8th" or use the dropdowns.'}), 400
        mgr.save_parking_location(location)
    elif 'street' in data:
        street = data['street']
        block = data.get('block') or None
        side = data.get('side', 'Unknown')
        matched = mgr.lookup.find_street(street)
        if not matched:
            return jsonify({'error': f'Street not found: {street}'}), 400
        mgr.save_structured_location(matched, block, side)
    else:
        return jsonify({'error': 'Provide lat/lng, text, or street field'}), 400

    return jsonify(mgr.get_status())


@app.route('/api/clear', methods=['POST'])
def api_clear():
    get_manager().clear_parking()
    return jsonify({'parked': False})


@app.route('/api/streets')
def api_streets():
    """Return street names, optionally filtered by prefix."""
    q = request.args.get('q', '').strip()
    mgr = get_manager()
    if q:
        streets = mgr.lookup.find_streets_prefix(q)
    else:
        streets = mgr.lookup.get_street_names()
    return jsonify(streets)


@app.route('/api/blocks')
def api_blocks():
    """Return block limits for a given street."""
    street = request.args.get('street', '').strip()
    if not street:
        return jsonify([])
    mgr = get_manager()
    blocks = mgr.lookup.get_all_blocks_for_street(street)
    return jsonify(blocks)


@app.route('/api/sides')
def api_sides():
    """Return valid sides for a street (+ optional block)."""
    street = request.args.get('street', '').strip()
    block = request.args.get('block', '').strip() or None
    if not street:
        return jsonify([])
    mgr = get_manager()
    sides = mgr.lookup.get_valid_sides(street, block)
    return jsonify(sides)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
