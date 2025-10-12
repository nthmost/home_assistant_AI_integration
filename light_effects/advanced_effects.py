"""
Advanced light effects that simulate more complex patterns
"""

from ha_client import HomeAssistantClient, LightEffects
import time
import math
from typing import List, Tuple


class AdvancedEffects(LightEffects):
    """Extended effects that simulate complex patterns"""

    def wave_flow(self, colors: List[Tuple[int, int, int]],
                  wave_speed: float = 0.15,
                  duration: float = 30.0):
        """
        Simulate a flowing wave effect by rapidly cycling colors
        Creates the illusion of colors swimming up/down the tube

        Args:
            colors: List of colors to flow through
            wave_speed: Time between color changes (lower = faster)
            duration: How long to run the effect
        """
        self._running = True
        start_time = time.time()

        while self._running and (time.time() - start_time < duration):
            for i, color in enumerate(colors):
                if not self._running:
                    break

                # Quick color change to simulate segment movement
                self.client.light_turn_on(
                    self.entity_id,
                    rgb_color=list(color),
                    brightness=255
                )
                time.sleep(wave_speed)

    def sine_wave_colors(self, color1: Tuple[int, int, int],
                        color2: Tuple[int, int, int],
                        frequency: float = 1.0,
                        duration: float = 30.0):
        """
        Oscillate between two colors using a sine wave
        Creates a smooth back-and-forth flow

        Args:
            color1: First color
            color2: Second color
            frequency: How fast to oscillate (Hz)
            duration: How long to run
        """
        self._running = True
        start_time = time.time()
        frame_time = 0.05  # 20 FPS

        while self._running and (time.time() - start_time < duration):
            elapsed = time.time() - start_time

            # Calculate sine wave position (0 to 1)
            t = (math.sin(elapsed * frequency * 2 * math.pi) + 1) / 2

            # Interpolate between colors
            r = int(color1[0] + (color2[0] - color1[0]) * t)
            g = int(color1[1] + (color2[1] - color1[1]) * t)
            b = int(color1[2] + (color2[2] - color1[2]) * t)

            self.client.light_turn_on(
                self.entity_id,
                rgb_color=[r, g, b],
                brightness=255
            )
            time.sleep(frame_time)

    def cascade(self, duration: float = 30.0):
        """
        Cascade through rainbow colors rapidly
        Creates flowing appearance through rapid color cycling
        """
        # Create a palette that flows nicely
        cascade_colors = [
            (255, 0, 0),      # Red
            (255, 127, 0),    # Orange
            (255, 255, 0),    # Yellow
            (0, 255, 0),      # Green
            (0, 255, 127),    # Teal
            (0, 255, 255),    # Cyan
            (0, 127, 255),    # Light Blue
            (0, 0, 255),      # Blue
            (127, 0, 255),    # Purple
            (255, 0, 255),    # Magenta
            (255, 0, 127),    # Pink
        ]

        self.wave_flow(cascade_colors, wave_speed=0.12, duration=duration)

    def surge(self, surge_type: str = 'red', duration: float = 5.0, speed: float = 0.08):
        """
        Intense energy surge - rotates rapidly between 3 shades of a color family
        at maximum brightness. Creates visceral emotional response.

        Args:
            surge_type: Type of surge ('red', 'green', 'blue', 'purple', 'orange', 'cyan')
            duration: How long the surge lasts
            speed: Time between color changes (lower = more intense)
        """
        surge_palettes = {
            'red': [
                (255, 0, 0),      # Pure red - ANGER/ALERT
                (200, 0, 30),     # Deep crimson
                (255, 30, 30),    # Bright red
            ],
            'green': [
                (0, 255, 0),      # Pure green - LIFE FORCE
                (30, 200, 30),    # Forest green
                (100, 255, 100),  # Light green
            ],
            'blue': [
                (0, 100, 255),    # Electric blue - CLARITY/COLD
                (0, 150, 255),    # Sky blue
                (50, 180, 255),   # Bright blue
            ],
            'purple': [
                (150, 0, 255),    # Electric purple - MYSTERY/PSYCHIC
                (120, 0, 200),    # Deep purple
                (180, 50, 255),   # Bright purple
            ],
            'orange': [
                (255, 100, 0),    # Electric orange - EXCITEMENT/WARNING
                (255, 140, 0),    # Bright orange
                (200, 80, 0),     # Deep orange
            ],
            'cyan': [
                (0, 255, 255),    # Electric cyan - DIGITAL/TECH
                (0, 200, 200),    # Deep cyan
                (100, 255, 255),  # Bright cyan
            ],
        }

        if surge_type not in surge_palettes:
            raise ValueError(f"Unknown surge type: {surge_type}. Choose from: {list(surge_palettes.keys())}")

        colors = surge_palettes[surge_type]

        # Rapid rotation at max brightness
        self._running = True
        start_time = time.time()

        while self._running and (time.time() - start_time < duration):
            for color in colors:
                if not self._running:
                    break

                self.client.light_turn_on(
                    self.entity_id,
                    rgb_color=list(color),
                    brightness=255  # ALWAYS max brightness for surge
                )
                time.sleep(speed)

    def ocean_swim(self, duration: float = 30.0):
        """Ocean-themed swimming colors"""
        ocean_colors = [
            (0, 20, 80),      # Deep ocean
            (0, 50, 120),     # Deep blue
            (0, 100, 180),    # Medium blue
            (0, 150, 220),    # Light blue
            (50, 200, 255),   # Sky blue
            (100, 230, 255),  # Cyan
            (150, 240, 255),  # Light cyan
            (100, 230, 255),  # Cyan
            (50, 200, 255),   # Sky blue
            (0, 150, 220),    # Light blue
            (0, 100, 180),    # Medium blue
            (0, 50, 120),     # Deep blue
        ]

        self.wave_flow(ocean_colors, wave_speed=0.2, duration=duration)

    def fire_swim(self, duration: float = 30.0):
        """Fire-themed swimming colors"""
        fire_colors = [
            (50, 0, 0),       # Deep red
            (100, 20, 0),     # Dark orange
            (200, 50, 0),     # Orange-red
            (255, 100, 0),    # Orange
            (255, 150, 0),    # Light orange
            (255, 200, 0),    # Yellow-orange
            (255, 255, 0),    # Yellow
            (255, 255, 100),  # Light yellow
            (255, 200, 0),    # Yellow-orange
            (255, 150, 0),    # Light orange
            (255, 100, 0),    # Orange
            (200, 50, 0),     # Orange-red
        ]

        self.wave_flow(fire_colors, wave_speed=0.1, duration=duration)

    def aurora(self, duration: float = 30.0):
        """Aurora borealis effect - flowing greens and purples"""
        aurora_colors = [
            (0, 100, 50),     # Deep green
            (0, 200, 100),    # Green
            (50, 255, 150),   # Light green
            (100, 255, 200),  # Cyan-green
            (100, 200, 255),  # Light blue
            (150, 100, 255),  # Purple-blue
            (200, 50, 255),   # Purple
            (150, 100, 255),  # Purple-blue
            (100, 200, 255),  # Light blue
            (100, 255, 200),  # Cyan-green
            (50, 255, 150),   # Light green
            (0, 200, 100),    # Green
        ]

        self.wave_flow(aurora_colors, wave_speed=0.18, duration=duration)


# Standalone test
if __name__ == "__main__":
    HA_URL = "http://homeassistant.local:8123"
    HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwMTU0ZTE4MzQ5ZjA0NzhiYWNjNzEzOGI5MjA0Y2ViYyIsImlhdCI6MTc2MDI0Njc0NCwiZXhwIjoyMDc1NjA2NzQ0fQ.gomMUtxThNUPJTUTlz6mflDtRD_HUza8s7pQNLMVQZE"
    TUBE_LAMP = "light.tube_lamp"

    client = HomeAssistantClient(HA_URL, HA_TOKEN)
    effects = AdvancedEffects(client, TUBE_LAMP)

    print("Advanced Effects Demo")
    print("=" * 50)

    print("\n1. Multi-color Swim (20 seconds)")
    effects.multi_color_swim(duration=20.0)

    print("\n2. Ocean Swim (20 seconds)")
    effects.ocean_swim(duration=20.0)

    print("\n3. Fire Swim (20 seconds)")
    effects.fire_swim(duration=20.0)

    print("\n4. Aurora Effect (20 seconds)")
    effects.aurora(duration=20.0)

    print("\n✓ Demo complete!")
