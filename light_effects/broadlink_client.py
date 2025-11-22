"""
Broadlink IR Remote Control Client
Controls IR devices via Home Assistant Broadlink integration
"""

from saga_assistant.ha_client import HomeAssistantClient
import time


class BroadlinkRemote:
    """Wrapper for Broadlink IR remote control via Home Assistant"""

    def __init__(self, client: HomeAssistantClient, entity_id: str, device_name: str):
        """
        Initialize Broadlink remote controller

        Args:
            client: HomeAssistantClient instance
            entity_id: Remote entity ID (e.g., "remote.office_lights")
            device_name: Device name used when learning commands (e.g., "Office Lights")
        """
        self.client = client
        self.entity_id = entity_id
        self.device_name = device_name

    def send_command(self, command: str, num_repeats: int = 1, delay_secs: float = 0.4):
        """
        Send IR command

        Args:
            command: Command name (must be learned first)
            num_repeats: Number of times to repeat the command
            delay_secs: Delay between repeats
        """
        return self.client.call_service("remote", "send_command", {
            "entity_id": self.entity_id,
            "device": self.device_name,
            "command": [command],
            "num_repeats": num_repeats,
            "delay_secs": delay_secs
        })

    def learn_command(self, command: str, timeout: int = 20):
        """
        Learn a new IR command

        Args:
            command: Name for the command
            timeout: Seconds to wait for IR signal
        """
        return self.client.call_service("remote", "learn_command", {
            "entity_id": self.entity_id,
            "device": self.device_name,
            "command": [command],
            "command_type": "ir",
            "timeout": timeout
        })

    def delete_command(self, command: str):
        """Delete a learned command"""
        return self.client.call_service("remote", "delete_command", {
            "entity_id": self.entity_id,
            "device": self.device_name,
            "command": [command]
        })


class OfficeLights:
    """Specific wrapper for Office Lights IR control"""

    def __init__(self, client: HomeAssistantClient):
        self.remote = BroadlinkRemote(client, "remote.office_lights", "Office Lights")

        # All learned commands
        self._colors = [
            "Orange", "Marigold", "Gold", "Yellow",
            "Seafoam", "Turquoise", "Aquamarine", "Teal",
            "Lavender", "Cyan", "Fuschia", "Magenta",
            "Green", "Blue", "Red", "White"
        ]
        self._effects = ["Flash", "Strobe", "Fade", "Smooth"]
        self._brightness = ["Light+", "Light-"]

        self._known_commands = self._colors + self._effects + self._brightness

    def red(self):
        """Turn lights red"""
        return self.remote.send_command("Red")

    def brightness_up(self):
        """Increase brightness"""
        return self.remote.send_command("Light+")

    def brightness_down(self):
        """Decrease brightness"""
        return self.remote.send_command("Light-")

    def set_color(self, color: str):
        """
        Set color by name

        Args:
            color: Color name (must be a learned command)
        """
        return self.remote.send_command(color)

    def set_effect(self, effect: str):
        """
        Set effect by name (Flash, Strobe, Fade, Smooth)

        Args:
            effect: Effect name
        """
        return self.remote.send_command(effect)

    def flash(self):
        """Flash effect"""
        return self.remote.send_command("Flash")

    def strobe(self):
        """Strobe effect"""
        return self.remote.send_command("Strobe")

    def fade(self):
        """Fade effect"""
        return self.remote.send_command("Fade")

    def smooth(self):
        """Smooth effect"""
        return self.remote.send_command("Smooth")

    def color_cycle(self, colors: list = None, duration_per_color: float = 1.0):
        """
        Cycle through colors

        Args:
            colors: List of color names (defaults to all colors)
            duration_per_color: Seconds to show each color
        """
        if colors is None:
            colors = self._colors

        print(f"Cycling through {len(colors)} colors...")
        for color in colors:
            print(f"  → {color}")
            self.set_color(color)
            time.sleep(duration_per_color)

    def pulse_brightness(self, steps: int = 3, delay: float = 0.5):
        """Pulse brightness up and down"""
        print(f"Pulsing brightness {steps} times...")
        for i in range(steps):
            self.brightness_up()
            time.sleep(delay)
            self.brightness_down()
            time.sleep(delay)

    def get_known_commands(self):
        """Return list of known learned commands"""
        return self._known_commands.copy()

    def get_colors(self):
        """Return list of available colors"""
        return self._colors.copy()

    def get_effects(self):
        """Return list of available effects"""
        return self._effects.copy()


# Example usage
if __name__ == "__main__":
    HA_URL = "http://homeassistant.local:8123"
    HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwMTU0ZTE4MzQ5ZjA0NzhiYWNjNzEzOGI5MjA0Y2ViYyIsImlhdCI6MTc2MDI0Njc0NCwiZXhwIjoyMDc1NjA2NzQ0fQ.gomMUtxThNUPJTUTlz6mflDtRD_HUza8s7pQNLMVQZE"

    client = HomeAssistantClient(HA_URL, HA_TOKEN)
    office = OfficeLights(client)

    print("Office Lights IR Control Demo")
    print("=" * 50)

    print("\nKnown commands:", office.get_known_commands())

    print("\nTesting Red...")
    office.red()
    time.sleep(2)

    print("Pulsing brightness...")
    office.pulse_brightness(steps=2)

    print("\nDemo complete!")
