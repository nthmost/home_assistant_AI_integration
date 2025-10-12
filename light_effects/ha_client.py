"""
Home Assistant API Client
Provides a clean Python interface for controlling Home Assistant devices
"""

import requests
import time
from typing import Optional, Dict, List, Tuple, Any
import colorsys


class HomeAssistantClient:
    """Client for interacting with Home Assistant API"""

    def __init__(self, base_url: str, token: str):
        """
        Initialize the HA client

        Args:
            base_url: Base URL of Home Assistant (e.g., "http://homeassistant.local:8123")
            token: Long-lived access token
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def get_state(self, entity_id: str) -> Dict[str, Any]:
        """Get the current state of an entity"""
        response = requests.get(
            f"{self.base_url}/api/states/{entity_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_all_states(self) -> List[Dict[str, Any]]:
        """Get states of all entities"""
        response = requests.get(
            f"{self.base_url}/api/states",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def call_service(self, domain: str, service: str, service_data: Dict[str, Any]) -> List[Dict]:
        """
        Call a Home Assistant service

        Args:
            domain: Service domain (e.g., "light", "switch")
            service: Service name (e.g., "turn_on", "toggle")
            service_data: Service parameters
        """
        response = requests.post(
            f"{self.base_url}/api/services/{domain}/{service}",
            headers=self.headers,
            json=service_data
        )
        response.raise_for_status()
        return response.json()

    # Light control methods
    def light_turn_on(self, entity_id: str, **kwargs):
        """
        Turn on a light with optional parameters

        Kwargs:
            brightness: 0-255
            rgb_color: [r, g, b] tuple (0-255)
            color_temp_kelvin: Color temperature in Kelvin
            transition: Transition time in seconds
        """
        data = {"entity_id": entity_id}
        data.update(kwargs)
        return self.call_service("light", "turn_on", data)

    def light_turn_off(self, entity_id: str, transition: Optional[float] = None):
        """Turn off a light"""
        data = {"entity_id": entity_id}
        if transition is not None:
            data["transition"] = transition
        return self.call_service("light", "turn_off", data)

    def light_toggle(self, entity_id: str):
        """Toggle a light"""
        return self.call_service("light", "toggle", {"entity_id": entity_id})

    # Switch control methods
    def switch_turn_on(self, entity_id: str):
        """Turn on a switch"""
        return self.call_service("switch", "turn_on", {"entity_id": entity_id})

    def switch_turn_off(self, entity_id: str):
        """Turn off a switch"""
        return self.call_service("switch", "turn_off", {"entity_id": entity_id})

    def switch_toggle(self, entity_id: str):
        """Toggle a switch"""
        return self.call_service("switch", "toggle", {"entity_id": entity_id})


class LightEffects:
    """Collection of light effect functions"""

    def __init__(self, client: HomeAssistantClient, entity_id: str):
        self.client = client
        self.entity_id = entity_id
        self._running = False

    def stop(self):
        """Stop any running effects"""
        self._running = False

    def smooth_transition(self, from_rgb: Tuple[int, int, int],
                         to_rgb: Tuple[int, int, int],
                         duration: float = 2.0,
                         steps: int = 20):
        """
        Smoothly transition from one color to another

        Args:
            from_rgb: Starting RGB color (0-255)
            to_rgb: Target RGB color (0-255)
            duration: Total duration in seconds
            steps: Number of intermediate steps
        """
        self._running = True
        step_duration = duration / steps

        for i in range(steps + 1):
            if not self._running:
                break

            t = i / steps
            r = int(from_rgb[0] + (to_rgb[0] - from_rgb[0]) * t)
            g = int(from_rgb[1] + (to_rgb[1] - from_rgb[1]) * t)
            b = int(from_rgb[2] + (to_rgb[2] - from_rgb[2]) * t)

            self.client.light_turn_on(self.entity_id, rgb_color=[r, g, b])
            time.sleep(step_duration)

    def rainbow_cycle(self, duration_per_cycle: float = 10.0, cycles: int = 1, brightness: int = 255):
        """
        Cycle through rainbow colors

        Args:
            duration_per_cycle: How long one full rainbow cycle takes
            cycles: Number of complete cycles (None for infinite)
            brightness: Brightness level 0-255
        """
        self._running = True
        steps = 100
        step_duration = duration_per_cycle / steps

        cycle_count = 0
        while self._running and (cycles is None or cycle_count < cycles):
            for i in range(steps):
                if not self._running:
                    break

                hue = i / steps
                rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                rgb_255 = tuple(int(c * 255) for c in rgb)

                self.client.light_turn_on(
                    self.entity_id,
                    rgb_color=list(rgb_255),
                    brightness=brightness
                )
                time.sleep(step_duration)

            cycle_count += 1

    def pulse(self, color: Tuple[int, int, int],
              min_brightness: int = 50,
              max_brightness: int = 255,
              duration: float = 2.0,
              pulses: Optional[int] = None):
        """
        Pulse a color by varying brightness

        Args:
            color: RGB color tuple
            min_brightness: Minimum brightness
            max_brightness: Maximum brightness
            duration: Duration of one pulse cycle
            pulses: Number of pulses (None for infinite)
        """
        self._running = True
        steps = 50
        step_duration = duration / steps

        pulse_count = 0
        while self._running and (pulses is None or pulse_count < pulses):
            # Fade up
            for i in range(steps // 2):
                if not self._running:
                    break

                t = i / (steps // 2)
                brightness = int(min_brightness + (max_brightness - min_brightness) * t)
                self.client.light_turn_on(
                    self.entity_id,
                    rgb_color=list(color),
                    brightness=brightness
                )
                time.sleep(step_duration)

            # Fade down
            for i in range(steps // 2):
                if not self._running:
                    break

                t = i / (steps // 2)
                brightness = int(max_brightness - (max_brightness - min_brightness) * t)
                self.client.light_turn_on(
                    self.entity_id,
                    rgb_color=list(color),
                    brightness=brightness
                )
                time.sleep(step_duration)

            pulse_count += 1

    def gradient_flow(self, colors: List[Tuple[int, int, int]],
                     duration_per_color: float = 3.0,
                     loops: Optional[int] = None):
        """
        Flow through a gradient of colors

        Args:
            colors: List of RGB color tuples to cycle through
            duration_per_color: Time to transition between colors
            loops: Number of complete loops (None for infinite)
        """
        self._running = True

        loop_count = 0
        while self._running and (loops is None or loop_count < loops):
            for i in range(len(colors)):
                if not self._running:
                    break

                next_color = colors[(i + 1) % len(colors)]
                self.smooth_transition(colors[i], next_color, duration_per_color)

            loop_count += 1

    def strobe(self, color: Tuple[int, int, int],
               interval: float = 0.1,
               count: Optional[int] = None):
        """
        Strobe effect - rapid on/off flashing

        Args:
            color: RGB color for the strobe
            interval: Time between flashes in seconds
            count: Number of flashes (None for infinite)
        """
        self._running = True

        flash_count = 0
        while self._running and (count is None or flash_count < count):
            self.client.light_turn_on(self.entity_id, rgb_color=list(color), brightness=255)
            time.sleep(interval)
            self.client.light_turn_off(self.entity_id)
            time.sleep(interval)
            flash_count += 1


# Preset color palettes
COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "yellow": (255, 255, 0),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
    "pink": (255, 192, 203),
    "white": (255, 255, 255),
    "warm_white": (255, 220, 180),
    "cool_white": (200, 230, 255),
}

GRADIENTS = {
    "sunset": [(255, 100, 0), (255, 50, 100), (100, 0, 150), (0, 0, 100)],
    "ocean": [(0, 50, 100), (0, 100, 200), (0, 200, 255), (100, 255, 255)],
    "forest": [(0, 100, 0), (50, 150, 50), (100, 200, 0), (150, 255, 100)],
    "fire": [(255, 0, 0), (255, 100, 0), (255, 200, 0), (255, 255, 100)],
    "candy": [(255, 0, 255), (255, 100, 200), (100, 200, 255), (0, 255, 255)],
}
