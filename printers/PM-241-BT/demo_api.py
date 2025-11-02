#!/usr/bin/env python3
"""
Test script for Label Printer API
Run this from any machine that can reach nike.local:8000
"""
import requests
import json
import sys

# Configuration
BASE_URL = "http://nike.local:8001"  # Change to your server address
# Or use localhost for testing: BASE_URL = "http://localhost:8001"


def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_capabilities():
    """Test capabilities endpoint"""
    print("\n🔍 Testing capabilities endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/capabilities")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Printer: {data['printer_name']}")
    print(f"   Available: {data['available']}")
    print(f"   Supported DPI: {data['supported_dpi']}")
    print(f"   Default label sizes:")
    for name, size in data['default_label_sizes'].items():
        print(f"     - {name}: {size['width_mm']}mm × {size['height_mm']}mm")
    return response.status_code == 200


def test_print(text="TEST", width_mm=50, height_mm=50, border=False):
    """Test print endpoint"""
    print(f"\n🖨️  Testing print endpoint...")
    print(f"   Text: '{text}'")
    print(f"   Size: {width_mm}mm × {height_mm}mm")

    payload = {
        "text": text,
        "label_size": {
            "width_mm": width_mm,
            "height_mm": height_mm
        },
        "options": {
            "border": border,
            "dpi": 300
        }
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/print",
        json=payload
    )

    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    return response.status_code == 200


def main():
    """Run all tests"""
    print(f"🎯 Testing Label Printer API at {BASE_URL}\n")
    print("=" * 60)

    try:
        # Test health
        if not test_health():
            print("\n❌ Health check failed!")
            return 1

        # Test capabilities
        if not test_capabilities():
            print("\n❌ Capabilities check failed!")
            return 1

        # Test print (will fail if printer not available)
        print("\n" + "=" * 60)
        test_print("JUNTAWA", width_mm=50, height_mm=50, border=True)

        print("\n" + "=" * 60)
        print("\n✅ API tests completed!")
        print("\nNote: Print test may fail with 503 if printer is not available.")
        print("This is expected behavior when the printer is not connected.\n")

        return 0

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to {BASE_URL}")
        print("   Make sure the service is running and accessible.")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
