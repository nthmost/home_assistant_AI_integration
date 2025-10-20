#!/usr/bin/env python3
"""
Zigbee Sensor Finder for AliExpress
Filters products that:
- Ship to 94118 (San Francisco)
- Are in stock
- Work with Home Assistant via Zigbee (no app required)
- Are actually available (not dead links)
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import quote_plus

# User agent to avoid blocking
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# Search categories
SEARCH_QUERIES = {
    'temp_humidity': [
        'Tuya Zigbee temperature humidity sensor LCD',
        'SONOFF SNZB-02D zigbee temperature',
        'Zigbee 3.0 temperature humidity sensor display',
    ],
    'motion': [
        'Tuya Zigbee PIR motion sensor',
        'SONOFF SNZB-03 zigbee motion',
        'Zigbee 3.0 motion sensor battery',
    ],
    'presence': [
        'Tuya Zigbee mmWave presence sensor',
        'Zigbee human presence detector radar',
    ],
    'door_window': [
        'Tuya Zigbee door window sensor',
        'SONOFF SNZB-04 zigbee door sensor',
        'Zigbee 3.0 door contact sensor',
    ],
    'multi_sensor': [
        'Tuya Zigbee 4 in 1 sensor motion temperature',
        'Zigbee multi sensor PIR humidity',
    ],
    'switches': [
        'Tuya Zigbee smart dimmer switch',
        'SONOFF zigbee mini switch',
        'Aqara wireless switch button',
    ],
}

# Required keywords to validate Zigbee compatibility
ZIGBEE_KEYWORDS = ['zigbee', 'zigbee 3.0', 'zigbee3.0']
HA_COMPATIBLE = ['home assistant', 'zigbee2mqtt', 'zha', 'no app required']
EXCLUDE_KEYWORDS = ['wifi only', 'requires app', 'cloud only', 'tuya app required']

def search_aliexpress(query, max_results=10):
    """
    Search AliExpress for products matching query
    Returns list of product info dicts
    """
    url = f"https://www.aliexpress.us/w/wholesale-{quote_plus(query)}.html"

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"  ⚠ Failed to search: {query} (status {response.status_code})")
            return []

        # Parse the page - AliExpress uses React/dynamic content
        # We'll look for common patterns in the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        products = []

        # Try to find product cards (this structure may change)
        # AliExpress often has JSON data embedded in script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'window._dida_config_' in script.string:
                # Try to extract product data from the config
                try:
                    # This is a simplified approach
                    text = script.string
                    if '"items":' in text:
                        # Found potential product data
                        pass
                except:
                    pass

        return products

    except requests.exceptions.Timeout:
        print(f"  ⚠ Timeout searching: {query}")
        return []
    except Exception as e:
        print(f"  ⚠ Error searching {query}: {e}")
        return []

def check_shipping_to_zip(product_url, zipcode='94118'):
    """
    Check if product ships to given zip code
    Note: This requires scraping individual product pages which may be blocked
    """
    # This would require selenium or similar to handle dynamic content
    # For now, return None (unknown)
    return None

def validate_product(product_info):
    """
    Check if product meets our criteria:
    - Has Zigbee in title/description
    - Mentions HA compatibility (bonus)
    - Doesn't require app-only
    """
    title_lower = product_info.get('title', '').lower()
    desc_lower = product_info.get('description', '').lower()
    combined = title_lower + ' ' + desc_lower

    # Must have Zigbee
    has_zigbee = any(kw in combined for kw in ZIGBEE_KEYWORDS)
    if not has_zigbee:
        return False, "No Zigbee mentioned"

    # Check for excludes
    has_exclude = any(kw in combined for kw in EXCLUDE_KEYWORDS)
    if has_exclude:
        return False, "Requires app or cloud only"

    return True, "OK"

def format_results(results):
    """Format results as markdown"""
    output = []
    output.append("# Zigbee Sensor Shopping List\n")
    output.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M')}\n")
    output.append("Ships to: 94118 (San Francisco, CA)\n")
    output.append("\n---\n\n")

    for category, products in results.items():
        if not products:
            continue

        category_name = category.replace('_', ' ').title()
        output.append(f"## {category_name}\n\n")

        for i, product in enumerate(products, 1):
            output.append(f"### {i}. {product['title']}\n")
            output.append(f"- **Price**: ${product.get('price', 'N/A')}\n")
            output.append(f"- **Link**: {product['url']}\n")
            output.append(f"- **In Stock**: {product.get('in_stock', 'Unknown')}\n")
            if product.get('ships_to_us'):
                output.append(f"- **Ships to US**: ✓\n")
            if product.get('ha_compatible'):
                output.append(f"- **HA Compatible**: Mentioned in listing\n")
            output.append("\n")

    return '\n'.join(output)

def main():
    """
    Main search and filter logic

    NOTE: AliExpress heavily uses JavaScript and dynamic content loading,
    making direct scraping difficult without browser automation (Selenium/Playwright).

    This script provides a framework but may need enhancement with:
    - Selenium/Playwright for dynamic content
    - AliExpress API (if available)
    - Manual verification of results
    """

    print("=" * 60)
    print("Zigbee Sensor Finder for AliExpress")
    print("=" * 60)
    print("\n⚠ NOTE: AliExpress uses heavy JavaScript rendering.")
    print("This script may need Selenium/Playwright for full functionality.")
    print("For now, it provides search URLs and criteria.\n")

    results = {}

    for category, queries in SEARCH_QUERIES.items():
        print(f"\n📦 Searching {category.replace('_', ' ').title()}...")
        results[category] = []

        for query in queries:
            print(f"  🔍 {query}")

            # Generate search URL
            search_url = f"https://www.aliexpress.us/w/wholesale-{quote_plus(query)}.html"

            # Add shipping filter to URL
            search_url += "?shipFromCountry=CN&shipToCountry=US"

            results[category].append({
                'title': query,
                'url': search_url,
                'price': 'See listing',
                'search_query': True,  # Mark as search URL
            })

            time.sleep(1)  # Be polite to servers

    # Generate output
    print("\n" + "=" * 60)
    print("Generating shopping guide...")
    print("=" * 60)

    # Create a simplified guide with search URLs
    output = []
    output.append("# Zigbee Sensor Shopping Guide for AliExpress\n")
    output.append(f"Generated: {time.strftime('%Y-%m-%d')}\n")
    output.append("Target Location: 94118 (San Francisco, CA)\n\n")

    output.append("## Requirements\n")
    output.append("✓ Zigbee 3.0 compatible\n")
    output.append("✓ Works with Home Assistant (ZHA or Zigbee2MQTT)\n")
    output.append("✓ No app required for operation\n")
    output.append("✓ Ships to US (94118)\n")
    output.append("✓ Currently in stock\n\n")

    output.append("## Search Strategy\n")
    output.append("Use these search URLs on AliExpress, then filter by:\n")
    output.append("1. **Price**: Low to High\n")
    output.append("2. **Shipping**: Ships from China, Ships to United States\n")
    output.append("3. **Check product title** for 'Zigbee 3.0' or 'ZigBee'\n")
    output.append("4. **Read reviews** mentioning Home Assistant or ZHA\n\n")

    output.append("---\n\n")

    for category, items in results.items():
        category_name = category.replace('_', ' ').title()
        output.append(f"## {category_name}\n\n")

        for item in items:
            output.append(f"### {item['title']}\n")
            output.append(f"**Search URL**: {item['url']}\n\n")
            output.append("**What to look for:**\n")
            output.append("- 'Zigbee 3.0' in title\n")
            output.append("- Reviews mentioning 'Home Assistant' or 'ZHA'\n")
            output.append("- Price under $15 for sensors, $25 for switches\n")
            output.append("- Free shipping or low shipping cost\n\n")

    # Write to file
    output_file = 'ZIGBEE_SHOPPING_GUIDE.md'
    with open(output_file, 'w') as f:
        f.write('\n'.join(output))

    print(f"\n✓ Shopping guide written to: {output_file}")
    print("\n💡 TIP: Open each search URL, then:")
    print("   1. Sort by 'Orders' or 'Price: Low to High'")
    print("   2. Check shipping to your ZIP")
    print("   3. Read reviews for HA compatibility mentions")

if __name__ == '__main__':
    main()
