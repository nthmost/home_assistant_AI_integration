#!/usr/bin/env python3
"""
Convert Squawkers IR timing codes to Broadlink base64 format
This allows sending codes WITHOUT learning from remote!
"""

import struct
from broadlink_squawkers import IR_CODES

def timing_to_broadlink_base64(timings, frequency=38000):
    """
    Convert microsecond timing array to Broadlink base64 format

    Broadlink format:
    - Byte 0: 0x26 (IR command)
    - Byte 1: repeat count (0x00 = once)
    - Bytes 2-3: length of pulse data
    - Bytes 4+: pulse pairs (mark, space) as little-endian uint16

    Each timing value is converted to units of ~30.5μs (2^-15 seconds)
    """
    import base64

    # Broadlink uses units of 2^-15 seconds (~30.5 microseconds)
    BROADLINK_UNIT = 32.84  # microseconds per unit (1000000 / 30.5)

    # Convert timings to Broadlink units
    pulse_data = []
    for timing_us in timings:
        # Convert microseconds to Broadlink units
        units = int(round(timing_us / BROADLINK_UNIT))
        # Pack as little-endian uint16
        pulse_data.append(struct.pack('<H', units))

    # Build the full packet
    packet = bytearray()
    packet.append(0x26)  # IR command type
    packet.append(0x00)  # Repeat count (0 = send once)

    # Length of pulse data (in bytes)
    pulse_bytes = b''.join(pulse_data)
    length = len(pulse_bytes)
    packet.extend(struct.pack('<H', length))  # Little-endian uint16

    # Add pulse data
    packet.extend(pulse_bytes)

    # Encode as base64
    return base64.b64encode(packet).decode('utf-8')


def main():
    print("\n" + "="*70)
    print("SQUAWKERS MCGRAW - BROADLINK BASE64 CODES")
    print("="*70)
    print("\nConverting timing arrays to Broadlink format...")
    print("These can be sent directly via Home Assistant!\n")

    converted = {}

    print("🎭 COMMON COMMANDS:")
    for cmd in ["dance", "reset"]:
        b64 = timing_to_broadlink_base64(IR_CODES[cmd])
        converted[cmd] = b64
        print(f"\n{cmd}:")
        print(f"  {b64}")

    print("\n" + "="*70)
    print("📻 RESPONSE MODE:")
    for letter in "ABCDEF":
        cmd = f"response_{letter.lower()}"
        b64 = timing_to_broadlink_base64(IR_CODES[cmd])
        converted[cmd] = b64
        print(f"\n{cmd}:")
        print(f"  {b64}")

    print("\n" + "="*70)
    print("🎮 COMMAND MODE:")
    for letter in "ABCDEF":
        cmd = f"command_{letter.lower()}"
        b64 = timing_to_broadlink_base64(IR_CODES[cmd])
        converted[cmd] = b64
        print(f"\n{cmd}:")
        print(f"  {b64}")

    print("\n" + "="*70)
    print("😂 GAGS MODE:")
    for letter in "ABCDEF":
        cmd = f"gags_{letter.lower()}"
        b64 = timing_to_broadlink_base64(IR_CODES[cmd])
        converted[cmd] = b64
        print(f"\n{cmd}:")
        print(f"  {b64}")

    print("\n" + "="*70)
    print(f"✅ Converted {len(converted)} commands to Broadlink format")
    print("="*70)

    # Save to file
    output_file = "broadlink_codes.txt"
    with open(output_file, "w") as f:
        f.write("# Squawkers McGraw Broadlink Base64 Codes\n")
        f.write("# Generated from timing arrays\n\n")
        for cmd, b64 in converted.items():
            f.write(f"{cmd}: {b64}\n")

    print(f"\n💾 Saved to: {output_file}")

    print("\n📝 NEXT STEP:")
    print("   Use these base64 codes with Home Assistant's remote.send_command")
    print("   Example:")
    print("   service: remote.send_command")
    print("   data:")
    print("     entity_id: remote.office_lights")
    print(f'     command: "{converted["dance"]}"')

    return converted


if __name__ == "__main__":
    converted_codes = main()
