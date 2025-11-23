#!/usr/bin/env python3
"""
Simple demo to show all Squawkers IR codes
"""

from broadlink_squawkers import IR_CODES

print("\n" + "="*70)
print("SQUAWKERS MCGRAW IR TIMING CODES")
print("="*70)
print("\nThese are the raw timing codes from the GitHub repo.")
print("They need to be LEARNED into your Broadlink before you can use them.\n")

print("🎭 COMMON COMMANDS:")
print(f"  dance:  {IR_CODES['dance']}")
print(f"  reset:  {IR_CODES['reset']}")

print("\n📻 RESPONSE MODE (6 buttons):")
for letter in "ABCDEF":
    cmd = f"response_{letter.lower()}"
    print(f"  {letter}: {IR_CODES[cmd]}")

print("\n🎮 COMMAND MODE (6 buttons):")
for letter in "ABCDEF":
    cmd = f"command_{letter.lower()}"
    print(f"  {letter}: {IR_CODES[cmd]}")

print("\n😂 GAGS MODE (6 buttons):")
for letter in "ABCDEF":
    cmd = f"gags_{letter.lower()}"
    print(f"  {letter}: {IR_CODES[cmd]}")

print("\n" + "="*70)
print("TOTAL: 20 commands available")
print("="*70)

print("\n❓ THE PROBLEM:")
print("   You need the original remote to learn these codes into Broadlink.")
print("   OR you need to build an ESP32 IR transmitter to generate them.")
print("\n💡 WHAT THE NUMBERS MEAN:")
print("   Each array is [mark, space, mark, space, ...] in microseconds")
print("   Example: [3000, 3000, ...] = 3ms IR on, 3ms off, etc.")
print("   Carrier frequency: 38kHz")

print("\n🛠️  NEXT STEPS:")
print("   1. Get original remote and use Broadlink learn mode, OR")
print("   2. Build ESP32 IR blaster to transmit these codes, OR")
print("   3. Try the light sensor control method instead")
print("\n   See: squawkers/BROADLINK_USAGE.md for full guide")
