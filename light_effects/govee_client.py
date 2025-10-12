"""
Govee API Client
Direct control of Govee devices via their cloud API
"""

import requests
import time
from typing import Dict, List, Tuple, Any, Optional


class GoveeClient:
    """Client for Govee cloud API"""

    BASE_URL = "https://developer-api.govee.com/v1"

    def __init__(self, api_key: str):
        """
        Initialize Govee client

        Args:
            api_key: Govee API key from the app
        """
        self.api_key = api_key
        self.headers = {
            "Govee-API-Key": api_key,
            "Content-Type": "application/json"
        }
        self._rate_limit_delay = 0.1  # Govee has rate limits

    def get_devices(self) -> List[Dict[str, Any]]:
        """Get list of all Govee devices"""
        response = requests.get(
            f"{self.BASE_URL}/devices",
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()

        if data.get('code') != 200:
            raise Exception(f"Govee API error: {data.get('message')}")

        return data.get('data', {}).get('devices', [])

    def get_device_state(self, device: str, model: str) -> Dict[str, Any]:
        """
        Get current state of a device

        Args:
            device: Device MAC address
            model: Device model (e.g., 'H6056')
        """
        response = requests.get(
            f"{self.BASE_URL}/devices/state",
            headers=self.headers,
            params={"device": device, "model": model}
        )
        response.raise_for_status()
        data = response.json()

        if data.get('code') != 200:
            raise Exception(f"Govee API error: {data.get('message')}")

        return data.get('data', {})

    def _send_command(self, device: str, model: str, cmd: Dict[str, Any]):
        """
        Send command to device

        Args:
            device: Device MAC address
            model: Device model
            cmd: Command dict with 'name' and 'value'
        """
        payload = {
            "device": device,
            "model": model,
            "cmd": cmd
        }

        response = requests.put(
            f"{self.BASE_URL}/devices/control",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()

        if data.get('code') != 200:
            raise Exception(f"Govee API error: {data.get('message')}")

        time.sleep(self._rate_limit_delay)
        return data

    def turn_on(self, device: str, model: str):
        """Turn device on"""
        return self._send_command(device, model, {"name": "turn", "value": "on"})

    def turn_off(self, device: str, model: str):
        """Turn device off"""
        return self._send_command(device, model, {"name": "turn", "value": "off"})

    def set_brightness(self, device: str, model: str, brightness: int):
        """
        Set brightness

        Args:
            brightness: 0-100
        """
        brightness = max(0, min(100, brightness))
        return self._send_command(device, model, {"name": "brightness", "value": brightness})

    def set_color(self, device: str, model: str, r: int, g: int, b: int):
        """
        Set RGB color

        Args:
            r, g, b: 0-255
        """
        color_value = {
            "r": max(0, min(255, r)),
            "g": max(0, min(255, g)),
            "b": max(0, min(255, b))
        }
        return self._send_command(device, model, {"name": "color", "value": color_value})

    def set_color_temp(self, device: str, model: str, kelvin: int):
        """
        Set color temperature

        Args:
            kelvin: Color temperature (device-specific range, typically 2000-9000)
        """
        return self._send_command(device, model, {"name": "colorTem", "value": kelvin})


class GoveeDevice:
    """Wrapper for a single Govee device"""

    def __init__(self, client: GoveeClient, device_id: str, model: str, name: str):
        self.client = client
        self.device_id = device_id
        self.model = model
        self.name = name

    def turn_on(self):
        """Turn on"""
        return self.client.turn_on(self.device_id, self.model)

    def turn_off(self):
        """Turn off"""
        return self.client.turn_off(self.device_id, self.model)

    def set_brightness(self, brightness: int):
        """Set brightness 0-100"""
        return self.client.set_brightness(self.device_id, self.model, brightness)

    def set_color(self, r: int, g: int, b: int):
        """Set RGB color"""
        return self.client.set_color(self.device_id, self.model, r, g, b)

    def set_color_temp(self, kelvin: int):
        """Set color temperature"""
        return self.client.set_color_temp(self.device_id, self.model, kelvin)

    def get_state(self):
        """Get current state"""
        return self.client.get_device_state(self.device_id, self.model)

    def __repr__(self):
        return f"GoveeDevice(name='{self.name}', model='{self.model}')"


# Example usage
if __name__ == "__main__":
    API_KEY = "2a9116d5-0bec-43a3-9791-4d1d577b212e"

    client = GoveeClient(API_KEY)

    # Discover devices
    devices = client.get_devices()
    print(f"Found {len(devices)} Govee devices:")

    for dev in devices:
        print(f"\n  Name: {dev['deviceName']}")
        print(f"  Model: {dev['model']}")
        print(f"  Device ID: {dev['device']}")
        print(f"  Supports: {', '.join(dev['supportCmds'])}")

        # Create device wrapper
        govee_dev = GoveeDevice(
            client,
            dev['device'],
            dev['model'],
            dev['deviceName']
        )

        # Test control
        print(f"\n  Testing {govee_dev.name}...")
        govee_dev.turn_on()
        time.sleep(1)
        govee_dev.set_color(255, 0, 0)
        print("  → Set to red")
        time.sleep(2)
        govee_dev.set_color(0, 255, 0)
        print("  → Set to green")
        time.sleep(2)
        govee_dev.set_color(0, 0, 255)
        print("  → Set to blue")
