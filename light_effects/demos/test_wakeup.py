#!/usr/bin/env python3
"""
Test the wake-up light sequence
Runs the gradual brightening in accelerated time for testing
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'light_effects'))

from ha_client import HomeAssistantClient
from broadlink_client import OfficeLights
import time

HA_URL = "http://homeassistant.local:8123"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwMTU0ZTE4MzQ5ZjA0NzhiYWNjNzEzOGI5MjA0Y2ViYyIsImlhdCI6MTc2MDI0Njc0NCwiZXhwIjoyMDc1NjA2NzQ0fQ.gomMUtxThNUPJTUTlz6mflDtRD_HUza8s7pQNLMVQZE"

LIGHTS = ["light.tube_lamp", "light.rgbic_tv_light_bars"]

client = HomeAssistantClient(HA_URL, HA_TOKEN)
office = OfficeLights(client)

print("🌅 Wake-Up Light Test (Accelerated) - ALL 3 SYSTEMS")
print("=" * 60)
print("\nThis simulates the 1-hour wake-up sequence in 30 seconds")
print("Includes: Tube Lamp, Govee Light Bars, Office Lights (IR)\n")

# Step 1: Start dim and warm
print("☀️  Step 1: Starting all lights at 5% brightness, warm color...")

# Start Tube Lamp and Govee bars
for light in LIGHTS:
    client.light_turn_on(
        light,
        brightness=13,        # 5%
        color_temp_kelvin=2500,  # Warm
        transition=2
    )

# Start Office Lights to warm orange, then dim down
print("   Setting Office Lights to warm Orange...")
office.set_color("Orange")
time.sleep(0.5)

print("   Dimming Office Lights down...")
for i in range(5):
    office.brightness_down()
    time.sleep(0.2)

print("\n   All lights are now dim and warm (like early sunrise)")
print("   Waiting 10 seconds...\n")
time.sleep(10)

# Step 2: Gradual increase to 80%
print("☀️  Step 2: Gradually increasing to 80% brightness over 20 seconds...")
print("   (This would be 1 hour in the real automation)\n")

# Brighten Tube Lamp and Govee bars
for light in LIGHTS:
    client.light_turn_on(
        light,
        brightness=204,       # 80%
        color_temp_kelvin=4000,  # Cooler/daylight
        transition=20         # 20 seconds for testing (real: 3600)
    )

# Transition Office Lights to white and brighten
print("   Switching Office Lights to White...")
office.set_color("White")
time.sleep(1)

print("   Brightening Office Lights in steps...")
for i in range(10):
    office.brightness_up()
    time.sleep(2)  # Every 2 seconds (simulating the 6-minute intervals)

print("\n✅ Wake-up sequence complete!")
print("   All 3 light systems should now be bright with daylight colors:")
print("   • Tube Lamp: 80% brightness, 4000K")
print("   • Govee Light Bars: 80% brightness, 4000K")
print("   • Office Lights: White, maximum brightness")
print("\n💡 In the real automation, this takes 2 hours total starting at sunrise")
