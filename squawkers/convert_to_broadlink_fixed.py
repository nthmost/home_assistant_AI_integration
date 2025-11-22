#!/usr/bin/env python3
"""
Convert Squawkers IR timing codes to Broadlink base64 format
Using the CORRECT formula from python-broadlink library
"""

import struct
import base64
from broadlink_squawkers import IR_CODES


def pulses_to_broadlink(pulses):
    """
    Convert microsecond timing array to Broadlink format

    Formula from python-broadlink: pulse * 269 / 8192
    Each value can be 1 or 2 bytes (if > 255, use big-endian with leading 0x00)
    """
    packet = bytearray()

    for pulse_us in pulses:
        # Convert microseconds to Broadlink units
        # Formula: pulse * 269 / 8192
        pulse_encoded = int(pulse_us * 269 / 8192)

        # If value fits in one byte
        if pulse_encoded <= 0xFF:
            packet.append(pulse_encoded)
        else:
            # Big-endian encoding with leading 0x00
            packet.append(0x00)
            packet.append((pulse_encoded >> 8) & 0xFF)  # High byte
            packet.append(pulse_encoded & 0xFF)         # Low byte

    return packet


def timing_to_broadlink_base64(timings):
    """
    Convert timing array to complete Broadlink base64 packet

    Packet structure:
    - Byte 0: 0x26 (IR command)
    - Byte 1: 0x00 (repeat count)
    - Bytes 2-3: Length of pulse data (little-endian)
    - Bytes 4+: Pulse data
    """
    # Encode the pulses
    pulse_data = pulses_to_broadlink(timings)

    # Build packet
    packet = bytearray()
    packet.append(0x26)  # IR command type
    packet.append(0x00)  # Repeat once

    # Length as little-endian uint16
    length = len(pulse_data)
    packet.extend(struct.pack('<H', length))

    # Add pulse data
    packet.extend(pulse_data)

    # Encode as base64
    return base64.b64encode(packet).decode('utf-8')


def main():
    print("\n" + "="*70)
    print("SQUAWKERS MCGRAW - CORRECTED BROADLINK CODES")
    print("="*70)
    print("\nUsing python-broadlink formula: pulse * 269 / 8192")
    print()

    converted = {}

    # Test with dance command first
    print("🎭 Testing DANCE command encoding:")
    dance_timings = IR_CODES["dance"]
    print(f"   Timings: {dance_timings}")

    dance_b64 = timing_to_broadlink_base64(dance_timings)
    converted["dance"] = dance_b64
    print(f"   Base64:  {dance_b64}")
    print()

    # Convert all commands
    print("Converting all commands...\n")

    for cmd_name, timings in IR_CODES.items():
        b64 = timing_to_broadlink_base64(timings)
        converted[cmd_name] = b64
        print(f"{cmd_name:20} {b64}")

    print("\n" + "="*70)
    print(f"✅ Converted {len(converted)} commands")
    print("="*70)

    # Save to file
    output_file = "broadlink_codes_fixed.txt"
    with open(output_file, "w") as f:
        f.write("# Squawkers McGraw Broadlink Base64 Codes (FIXED)\n")
        f.write("# Using python-broadlink formula: pulse * 269 / 8192\n\n")
        for cmd, b64 in converted.items():
            f.write(f"{cmd}: {b64}\n")

    print(f"\n💾 Saved to: {output_file}")

    return converted


if __name__ == "__main__":
    codes = main()
