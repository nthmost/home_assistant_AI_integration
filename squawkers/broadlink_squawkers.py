"""
Squawkers McGraw Broadlink IR Control
Converts timing arrays to Broadlink format and provides control interface
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from saga_assistant.ha_client import HomeAssistantClient
from light_effects.broadlink_client import BroadlinkRemote
import base64
import time


def timing_to_pronto(timings: list, frequency: int = 38000) -> str:
    """
    Convert microsecond timing array to Pronto Hex format

    Args:
        timings: List of mark/space durations in microseconds
        frequency: Carrier frequency in Hz (default 38kHz)

    Returns:
        Pronto Hex string
    """
    # Pronto format:
    # [0000] [frequency code] [sequence1 length] [sequence2 length] [timing pairs...]

    # Calculate frequency code (1000000 / (frequency * 0.241246))
    freq_code = int(1000000 / (frequency * 0.241246))

    # Convert timings to Pronto units (each timing / 0.241246 / frequency code)
    pronto_timings = []
    for t in timings:
        # Convert microseconds to Pronto units
        pronto_value = int(round(t / 0.241246 / freq_code))
        pronto_timings.append(pronto_value)

    # Pronto format: learned code type (0000), frequency, one-time sequence length, repeat sequence length
    pronto_hex = [
        "0000",  # Learned IR code
        f"{freq_code:04X}",  # Frequency code
        f"{len(pronto_timings):04X}",  # One-time burst pair count
        "0000"  # Repeat burst pair count (0 = no repeat)
    ]

    # Add timing pairs
    for timing in pronto_timings:
        pronto_hex.append(f"{timing:04X}")

    return " ".join(pronto_hex)


def pronto_to_broadlink(pronto_hex: str) -> str:
    """
    Convert Pronto Hex to Broadlink base64 format

    Args:
        pronto_hex: Pronto Hex string

    Returns:
        Base64 encoded string for Broadlink
    """
    # Parse pronto hex
    parts = pronto_hex.split()
    frequency_code = int(parts[1], 16)

    # Extract timings (skip first 4 header values)
    timings = [int(p, 16) for p in parts[4:]]

    # Convert to microseconds for Broadlink
    # timing_us = timing * frequency_code * 0.241246
    timing_us = [int(t * frequency_code * 0.241246) for t in timings]

    # Broadlink format: little-endian pairs of bytes for each timing
    broadlink_data = bytearray()

    for timing in timing_us:
        # Split into 50us units (Broadlink resolution)
        timing_50us = int(timing / 50)

        # Encode as little-endian 16-bit value
        low_byte = timing_50us & 0xFF
        high_byte = (timing_50us >> 8) & 0xFF

        broadlink_data.append(low_byte)
        broadlink_data.append(high_byte)

    # Encode as base64
    return base64.b64encode(broadlink_data).decode('utf-8')


# IR Timing codes from https://github.com/playfultechnology/SquawkersMcGraw
# Format: {mark, space, mark, space, ...} in microseconds at 38kHz carrier

IR_CODES = {
    # Common commands across all modes
    "dance": [3000, 3000, 1000, 2000, 2000, 1000, 1000, 2000, 2000, 1000, 2000, 1000, 1000, 2000, 2000, 1000, 1000],
    "reset": [3000, 3000, 1000, 2000, 2000, 1000, 2000, 1000, 1000, 2000, 1000, 2000, 2000, 1000, 1000, 2000, 1000],

    # Response Mode
    "response_repeat": [3000, 3000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 2000, 1000, 1000, 2000, 2000, 1000, 1000],
    "response_a": [3000, 3000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 2000, 1000, 1000, 2000, 2000, 1000, 1000],
    "response_b": [3000, 3000, 1000, 2000, 1000, 2000, 1000, 2000, 2000, 1000, 1000, 2000, 2000, 1000, 1000, 2000, 1000],
    "response_c": [3000, 3000, 1000, 2000, 1000, 2000, 1000, 2000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 1000],
    "response_d": [3000, 3000, 1000, 2000, 1000, 2000, 2000, 1000, 1000, 2000, 2000, 1000, 1000, 2000, 1000, 2000, 1000],
    "response_e": [3000, 3000, 1000, 2000, 1000, 2000, 2000, 1000, 2000, 1000, 1000, 2000, 1000, 2000, 2000, 1000, 1000],
    "response_f": [3000, 3000, 1000, 2000, 1000, 2000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 1000, 2000, 1000],
    "response_record": [3000, 3000, 1000, 2000, 2000, 1000, 2000, 1000, 1000, 2000, 2000, 1000, 2000, 1000, 2000, 1000, 1000],

    # Command Mode
    "command_repeat": [3000, 3000, 1000, 2000, 2000, 1000, 1000, 2000, 1000, 2000, 1000, 2000, 2000, 1000, 2000, 1000, 1000],
    "command_a": [3000, 3000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 2000, 1000, 2000, 1000, 1000, 2000, 1000],
    "command_b": [3000, 3000, 1000, 2000, 1000, 2000, 1000, 2000, 2000, 1000, 1000, 2000, 2000, 1000, 2000, 1000, 1000],
    "command_c": [3000, 3000, 1000, 2000, 1000, 2000, 2000, 1000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 1000],
    "command_d": [3000, 3000, 1000, 2000, 1100, 2000, 2000, 1000, 1000, 2000, 2000, 1000, 1100, 2000, 2000, 1000, 1000],
    "command_e": [3000, 3000, 1000, 2000, 1000, 2000, 2000, 1000, 2000, 1000, 1000, 2000, 2000, 1000, 1000, 2000, 1000],
    "command_f": [3000, 3000, 1000, 2000, 1000, 2000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 1000],
    "command_record": [3000, 3000, 1000, 2000, 2000, 1000, 2000, 1000, 1000, 2000, 2000, 1000, 2000, 1000, 2000, 1000, 1000],

    # Gags Mode
    "gags_repeat": [3000, 3000, 1000, 2000, 2000, 1000, 1000, 2000, 1000, 2000, 1000, 2000, 2000, 1000, 2000, 1000, 1000],
    "gags_a": [3000, 3000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 2000, 1000, 2000, 1000, 2000, 1000, 1000],
    "gags_b": [3000, 3000, 1000, 2000, 1000, 2000, 1000, 2000, 2000, 1000, 2000, 1000, 1000, 2000, 1000, 2000, 1000],
    "gags_c": [3000, 3000, 1000, 2000, 1000, 2000, 2000, 1000, 1000, 2000, 1000, 2000, 1000, 2000, 2000, 1000, 1000],
    "gags_d": [3000, 3000, 1000, 2000, 1000, 2000, 2000, 1000, 1000, 2000, 2000, 1000, 2000, 1000, 1000, 2000, 1000],
    "gags_e": [3000, 3000, 1000, 2000, 1000, 2000, 2000, 1000, 2000, 1000, 1000, 2000, 2000, 1000, 2000, 1000, 1000],
    "gags_f": [3000, 3000, 1000, 2000, 2000, 1000, 1100, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 1000],
    "gags_record": [3000, 3000, 1000, 2000, 2000, 1000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 1000],
}


class SquawkersMcGraw:
    """Control interface for Squawkers McGraw animatronic parrot via Broadlink IR"""

    def __init__(self, client: HomeAssistantClient, entity_id: str = "remote.office_lights"):
        """
        Initialize Squawkers McGraw controller

        Args:
            client: HomeAssistantClient instance
            entity_id: Broadlink remote entity ID
        """
        self.remote = BroadlinkRemote(client, entity_id, "Squawkers McGraw")
        self.client = client

        # Track what behaviors we've discovered
        self.discovered_behaviors = {}

    def send_raw_timing(self, timings: list, repeat: int = 3, delay: float = 0.1):
        """
        Send raw timing array as IR signal

        Note: This requires the Broadlink to support raw timing format.
        If not supported, commands must be learned first.

        Args:
            timings: List of microsecond timing values
            repeat: Number of times to repeat (GitHub issue suggests multiple repeats)
            delay: Delay between repeats in seconds
        """
        # Convert to Pronto format
        pronto = timing_to_pronto(timings)
        print(f"Pronto Hex: {pronto}")

        # Convert to Broadlink format
        broadlink_b64 = pronto_to_broadlink(pronto)
        print(f"Broadlink Base64: {broadlink_b64}")

        # Send via Home Assistant
        # Note: This may require custom integration or learning mode
        print(f"⚠️  Raw IR sending not yet implemented - use learn mode instead")
        return None

    def test_command(self, command_name: str, repeat: int = 3):
        """
        Test a command by sending it multiple times

        Args:
            command_name: Name from IR_CODES dict
            repeat: Number of times to send (default 3, per GitHub issue advice)
        """
        if command_name not in IR_CODES:
            print(f"❌ Unknown command: {command_name}")
            print(f"Available commands: {', '.join(IR_CODES.keys())}")
            return

        print(f"🔊 Testing command: {command_name}")
        print(f"   Repeating {repeat} times with gentle pauses...")

        timings = IR_CODES[command_name]

        for i in range(repeat):
            print(f"   Attempt {i+1}/{repeat}...")
            self.send_raw_timing(timings, repeat=1)
            time.sleep(0.5)  # "Gentle pause" between repeats

        print(f"✅ Test complete for: {command_name}")
        print(f"📝 What happened? (Document the behavior)")

    def dance(self):
        """Trigger dance behavior"""
        return self.remote.send_command("dance", num_repeats=3, delay_secs=0.5)

    def reset(self):
        """Reset/stop current behavior"""
        return self.remote.send_command("reset", num_repeats=3, delay_secs=0.5)

    def response_mode_button(self, button: str):
        """
        Send Response Mode button command (A-F)

        Args:
            button: Button letter (A-F)
        """
        command = f"response_{button.lower()}"
        return self.remote.send_command(command, num_repeats=3, delay_secs=0.5)

    def command_mode_button(self, button: str):
        """
        Send Command Mode button command (A-F)

        Args:
            button: Button letter (A-F)
        """
        command = f"command_{button.lower()}"
        return self.remote.send_command(command, num_repeats=3, delay_secs=0.5)

    def gags_mode_button(self, button: str):
        """
        Send Gags Mode button command (A-F)

        Args:
            button: Button letter (A-F)
        """
        command = f"gags_{button.lower()}"
        return self.remote.send_command(command, num_repeats=3, delay_secs=0.5)

    def document_behavior(self, command_name: str, description: str):
        """
        Document what a command actually does

        Args:
            command_name: Command name from IR_CODES
            description: What behavior you observed
        """
        self.discovered_behaviors[command_name] = description
        print(f"📝 Documented: {command_name} -> {description}")

    def get_all_commands(self):
        """Return list of all available command names"""
        return list(IR_CODES.keys())

    def get_response_mode_commands(self):
        """Return list of Response Mode commands"""
        return [k for k in IR_CODES.keys() if k.startswith("response_")]

    def get_command_mode_commands(self):
        """Return list of Command Mode commands"""
        return [k for k in IR_CODES.keys() if k.startswith("command_")]

    def get_gags_mode_commands(self):
        """Return list of Gags Mode commands"""
        return [k for k in IR_CODES.keys() if k.startswith("gags_")]

    def print_all_codes(self):
        """Print all IR codes for reference"""
        print("\n" + "="*70)
        print("SQUAWKERS MCGRAW IR CODES")
        print("="*70)

        print("\n🎭 COMMON COMMANDS:")
        for cmd in ["dance", "reset"]:
            print(f"  {cmd:20} {IR_CODES[cmd]}")

        print("\n📻 RESPONSE MODE:")
        for cmd in self.get_response_mode_commands():
            print(f"  {cmd:20} {IR_CODES[cmd]}")

        print("\n🎮 COMMAND MODE:")
        for cmd in self.get_command_mode_commands():
            print(f"  {cmd:20} {IR_CODES[cmd]}")

        print("\n😂 GAGS MODE:")
        for cmd in self.get_gags_mode_commands():
            print(f"  {cmd:20} {IR_CODES[cmd]}")

        print("\n" + "="*70)


# Test/demo script
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()
    HA_URL = os.getenv("HA_URL", "http://homeassistant.local:8123")
    HA_TOKEN = os.getenv("HA_TOKEN")

    if not HA_TOKEN:
        print("❌ Error: HA_TOKEN not found in .env file")
        exit(1)

    # Initialize
    print("🦜 Squawkers McGraw Broadlink Control")
    print("="*70)

    client = HomeAssistantClient(HA_URL, HA_TOKEN)
    squawkers = SquawkersMcGraw(client)

    # Print all codes
    squawkers.print_all_codes()

    print("\n📋 NEXT STEPS:")
    print("1. Use Broadlink learning mode to capture each IR code")
    print("2. Test each command and document what it does")
    print("3. Update this script with discovered behaviors")
    print("4. Create voice control automations")

    print("\n💡 TIP: GitHub issue suggests repeating commands 'gently several times with pause'")
    print("   We've set default repeat=3 with 0.5s delay")
