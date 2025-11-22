#!/usr/bin/env python3
"""
Debug what's actually being sent to Home Assistant API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()
HA_URL = os.getenv("HA_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.getenv("HA_TOKEN")

# Test base64 code
test_code = "JgAiAFsAWwAeAD0APQAeAB4APQA9AB4APQAeAB4APQA9AB4AHgA="

print("Testing different API call formats...\n")

headers = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

# Test 1: With b64: prefix as list
print("Test 1: command as list with b64: prefix")
data1 = {
    "entity_id": "remote.office_lights",
    "command": [f"b64:{test_code}"]
}
print(f"Data: {data1}")
response = requests.post(f"{HA_URL}/api/services/remote/send_command", headers=headers, json=data1)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 2: Without b64: prefix
print("Test 2: command as list without b64: prefix")
data2 = {
    "entity_id": "remote.office_lights",
    "command": [test_code]
}
print(f"Data: {data2}")
response = requests.post(f"{HA_URL}/api/services/remote/send_command", headers=headers, json=data2)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 3: Just the base64 string (not in list)
print("Test 3: command as string with b64: prefix")
data3 = {
    "entity_id": "remote.office_lights",
    "command": f"b64:{test_code}"
}
print(f"Data: {data3}")
response = requests.post(f"{HA_URL}/api/services/remote/send_command", headers=headers, json=data3)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 4: With device parameter (like learned codes)
print("Test 4: With device parameter + b64: prefix")
data4 = {
    "entity_id": "remote.office_lights",
    "device": "Squawkers McGraw",
    "command": [f"b64:{test_code}"]
}
print(f"Data: {data4}")
response = requests.post(f"{HA_URL}/api/services/remote/send_command", headers=headers, json=data4)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")
