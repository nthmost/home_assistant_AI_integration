#!/usr/bin/env python3
"""
Demo script showing various light effects on the Tube Lamp
"""

from ha_client import HomeAssistantClient, LightEffects, COLORS, GRADIENTS
import time

# Configuration
HA_URL = "http://homeassistant.local:8123"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwMTU0ZTE4MzQ5ZjA0NzhiYWNjNzEzOGI5MjA0Y2ViYyIsImlhdCI6MTc2MDI0Njc0NCwiZXhwIjoyMDc1NjA2NzQ0fQ.gomMUtxThNUPJTUTlz6mflDtRD_HUza8s7pQNLMVQZE"
TUBE_LAMP = "light.tube_lamp"


def main():
    print("Home Assistant Light Effects Demo")
    print("=" * 50)

    # Initialize client
    client = HomeAssistantClient(HA_URL, HA_TOKEN)
    effects = LightEffects(client, TUBE_LAMP)

    # Make sure light is on
    print("Turning on Tube Lamp...")
    client.light_turn_on(TUBE_LAMP, brightness=255)
    time.sleep(1)

    # Demo 1: Rainbow cycle
    print("\n1. Rainbow Cycle (10 seconds)...")
    effects.rainbow_cycle(duration_per_cycle=10.0, cycles=1, brightness=255)

    # Demo 2: Sunset gradient
    print("\n2. Sunset Gradient (15 seconds)...")
    effects.gradient_flow(GRADIENTS["sunset"], duration_per_color=3.0, loops=1)

    # Demo 3: Ocean gradient
    print("\n3. Ocean Gradient (15 seconds)...")
    effects.gradient_flow(GRADIENTS["ocean"], duration_per_color=3.0, loops=1)

    # Demo 4: Pulse red
    print("\n4. Red Pulse (6 seconds)...")
    effects.pulse(COLORS["red"], min_brightness=50, max_brightness=255, duration=2.0, pulses=3)

    # Demo 5: Fire gradient
    print("\n5. Fire Gradient (12 seconds)...")
    effects.gradient_flow(GRADIENTS["fire"], duration_per_color=2.0, loops=1)

    # Demo 6: Smooth color transitions
    print("\n6. Color Transitions...")
    print("   Red -> Green")
    effects.smooth_transition(COLORS["red"], COLORS["green"], duration=2.0)
    print("   Green -> Blue")
    effects.smooth_transition(COLORS["green"], COLORS["blue"], duration=2.0)
    print("   Blue -> Purple")
    effects.smooth_transition(COLORS["blue"], COLORS["purple"], duration=2.0)

    # Demo 7: Candy gradient
    print("\n7. Candy Gradient (15 seconds)...")
    effects.gradient_flow(GRADIENTS["candy"], duration_per_color=3.0, loops=1)

    print("\n✓ Demo complete!")
    print("Returning to warm white...")
    client.light_turn_on(TUBE_LAMP, rgb_color=list(COLORS["warm_white"]), brightness=200)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
