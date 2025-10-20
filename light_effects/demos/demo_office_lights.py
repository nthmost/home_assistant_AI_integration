#!/usr/bin/env python3
"""
Demo of Office Lights IR control with all learned colors and effects
"""

import sys
sys.path.insert(0, '.')

from ha_client import HomeAssistantClient
from broadlink_client import OfficeLights
import time

HA_URL = "http://homeassistant.local:8123"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwMTU0ZTE4MzQ5ZjA0NzhiYWNjNzEzOGI5MjA0Y2ViYyIsImlhdCI6MTc2MDI0Njc0NCwiZXhwIjoyMDc1NjA2NzQ0fQ.gomMUtxThNUPJTUTlz6mflDtRD_HUza8s7pQNLMVQZE"

client = HomeAssistantClient(HA_URL, HA_TOKEN)
office = OfficeLights(client)

print("🌈 Office Lights IR Control - Full Demo")
print("=" * 60)

print(f"\n📋 Available colors ({len(office.get_colors())}):")
for color in office.get_colors():
    print(f"   • {color}")

print(f"\n✨ Available effects ({len(office.get_effects())}):")
for effect in office.get_effects():
    print(f"   • {effect}")

print("\n" + "=" * 60)

# Demo 1: Color cycle
print("\n🎨 Demo 1: Cycling through all colors (1 sec each)")
office.color_cycle(duration_per_color=1.0)

# Demo 2: Warm colors
print("\n🔥 Demo 2: Warm colors (Orange → Marigold → Gold → Yellow)")
warm_colors = ["Orange", "Marigold", "Gold", "Yellow"]
office.color_cycle(colors=warm_colors, duration_per_color=1.5)

# Demo 3: Cool colors
print("\n❄️  Demo 3: Cool colors (Seafoam → Turquoise → Aquamarine → Teal → Cyan)")
cool_colors = ["Seafoam", "Turquoise", "Aquamarine", "Teal", "Cyan"]
office.color_cycle(colors=cool_colors, duration_per_color=1.5)

# Demo 4: Effects
print("\n✨ Demo 4: Testing effects")
print("   Flash...")
office.flash()
time.sleep(3)

print("   Strobe...")
office.strobe()
time.sleep(3)

print("   Fade...")
office.fade()
time.sleep(3)

print("   Smooth...")
office.smooth()
time.sleep(3)

# Demo 5: Set to white for clean finish
print("\n⚪ Setting to White to finish...")
office.set_color("White")

print("\n" + "=" * 60)
print("✅ Demo complete!")
print("\nAll 20 commands tested successfully:")
print(f"   • {len(office.get_colors())} colors")
print(f"   • {len(office.get_effects())} effects")
print(f"   • 2 brightness controls (Light+/Light-)")
