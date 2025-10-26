#!/usr/bin/env python3
"""
Home Assistant Light Dashboard

A Streamlit-based dashboard for controlling lights with:
- Grid and list view modes
- Room-based grouping
- Dynamic controls based on light capabilities
- Filtering of inactive lights (2+ weeks)
- Leverages Streamlit's reactive model for automatic state updates
"""

import streamlit as st
import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from homeassistant_api import Client
from homeassistant_api.models.entity import Entity

from ha_core import HomeAssistantInspector, load_credentials

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s [%(name)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configuration
INACTIVE_THRESHOLD_DAYS = 14  # Filter lights inactive for 2+ weeks

# Page config
st.set_page_config(
    page_title="Light Dashboard",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_inspector():
    """Initialize HA Inspector - fresh on every rerun for current state"""
    url, token = load_credentials()
    logger.info("🔄 Initializing fresh HomeAssistantInspector")
    return HomeAssistantInspector(url, token, log_level=40)  # ERROR level to reduce log spam


def is_light_active(entity: Entity, threshold_days: int = INACTIVE_THRESHOLD_DAYS) -> bool:
    """
    Check if a light has been active within the threshold period

    Args:
        entity: Entity object
        threshold_days: Number of days to consider as threshold

    Returns:
        True if light was active recently, False otherwise
    """
    if not hasattr(entity, 'state') or entity.state is None:
        return False

    # Check last_changed timestamp
    if hasattr(entity.state, 'last_changed'):
        last_changed = entity.state.last_changed
        # Parse ISO format datetime
        if isinstance(last_changed, str):
            try:
                last_changed = datetime.fromisoformat(last_changed.replace('Z', '+00:00'))
            except:
                return True  # If can't parse, include it

        threshold = datetime.now(last_changed.tzinfo) - timedelta(days=threshold_days)
        return last_changed > threshold

    return True  # If no timestamp info, include it


def get_room_from_entity(entity: Entity) -> Optional[str]:
    """
    Extract room/area name from entity

    Args:
        entity: Entity object

    Returns:
        Room name or None if no room assigned
    """
    # Try area_id first
    if hasattr(entity, 'area_id') and entity.area_id:
        return entity.area_id.replace('_', ' ').title()

    # Try attributes
    if hasattr(entity, 'state') and hasattr(entity.state, 'attributes'):
        attrs = entity.state.attributes
        if 'area' in attrs:
            return attrs['area'].replace('_', ' ').title()
        if 'room' in attrs:
            return attrs['room'].replace('_', ' ').title()

    # Try parsing entity_id (e.g., light.living_room_lamp -> "Living Room")
    entity_id = entity.entity_id
    if '.' in entity_id:
        parts = entity_id.split('.')[1].split('_')
        # Look for common room keywords
        room_keywords = ['living', 'bedroom', 'kitchen', 'bathroom', 'office',
                        'dining', 'garage', 'hallway', 'closet', 'laundry']
        for keyword in room_keywords:
            if keyword in parts:
                idx = parts.index(keyword)
                # Take keyword and next word if it exists (e.g., "living room")
                room_parts = parts[idx:idx+2] if idx+1 < len(parts) else [parts[idx]]
                return ' '.join(room_parts).title()

    return None


def group_lights_by_room(lights: List[Entity]) -> Dict[str, List[Entity]]:
    """
    Group lights by room, with ungrouped lights at the end

    Args:
        lights: List of light entities

    Returns:
        Dictionary mapping room names to light entities
    """
    grouped = defaultdict(list)

    for light in lights:
        room = get_room_from_entity(light)
        if room:
            grouped[room].append(light)
        else:
            grouped["Ungrouped"].append(light)

    # Sort rooms alphabetically, but keep "Ungrouped" at the end
    sorted_groups = {}
    for room in sorted(grouped.keys()):
        if room != "Ungrouped":
            sorted_groups[room] = grouped[room]

    if "Ungrouped" in grouped:
        sorted_groups["Ungrouped"] = grouped["Ungrouped"]

    return sorted_groups


def get_light_capabilities(entity: Entity) -> Dict[str, bool]:
    """
    Determine what capabilities a light has

    Args:
        entity: Light entity

    Returns:
        Dictionary of capability flags
    """
    capabilities = {
        'brightness': False,
        'color': False,
        'color_temp': False,
    }

    if not hasattr(entity.state, 'attributes'):
        return capabilities

    attrs = entity.state.attributes

    # Check for brightness
    if 'brightness' in attrs or 'supported_color_modes' in attrs:
        supported_modes = attrs.get('supported_color_modes', [])
        if supported_modes:
            capabilities['brightness'] = True

    # Check for color support
    if 'rgb_color' in attrs or 'hs_color' in attrs:
        capabilities['color'] = True

    if 'supported_color_modes' in attrs:
        modes = attrs['supported_color_modes']
        if any(mode in modes for mode in ['rgb', 'rgbw', 'rgbww', 'hs']):
            capabilities['color'] = True

    # Check for color temperature
    if 'color_temp' in attrs or 'color_temp_kelvin' in attrs:
        capabilities['color_temp'] = True

    if 'supported_color_modes' in attrs:
        modes = attrs['supported_color_modes']
        if 'color_temp' in modes:
            capabilities['color_temp'] = True

    return capabilities


def get_friendly_name(entity: Entity) -> str:
    """Get friendly display name for entity"""
    if hasattr(entity.state, 'attributes') and 'friendly_name' in entity.state.attributes:
        return entity.state.attributes['friendly_name']
    return entity.entity_id.split('.')[1].replace('_', ' ').title()


def is_light_on(entity: Entity) -> bool:
    """Check if light is currently on"""
    if hasattr(entity, 'state') and hasattr(entity.state, 'state'):
        state_value = entity.state.state.lower() == 'on'
        logger.debug(f"💡 {entity.entity_id}: state={entity.state.state} → is_on={state_value}")
        return state_value
    logger.warning(f"⚠️  {entity.entity_id}: No state attribute found")
    return False


def get_brightness(entity: Entity) -> Optional[int]:
    """Get current brightness (0-255)"""
    if hasattr(entity.state, 'attributes') and 'brightness' in entity.state.attributes:
        return entity.state.attributes['brightness']
    return None


def get_rgb_color(entity: Entity) -> Optional[Tuple[int, int, int]]:
    """Get current RGB color"""
    if hasattr(entity.state, 'attributes') and 'rgb_color' in entity.state.attributes:
        return tuple(entity.state.attributes['rgb_color'])
    return None


def render_light_grid(lights: List[Entity], inspector: HomeAssistantInspector):
    """Render lights in a compact grid view"""
    cols = st.columns(6)  # 6 lights per row

    for idx, light in enumerate(lights):
        col = cols[idx % 6]

        with col:
            name = get_friendly_name(light)
            is_on = is_light_on(light)
            capabilities = get_light_capabilities(light)

            # Create a card-like container
            with st.container():
                st.markdown(f"**{name}**")

                # Status indicator (informational only)
                if is_on:
                    st.markdown("🟢 <span style='color: #00FF00;'>**ON**</span>", unsafe_allow_html=True)
                else:
                    st.markdown("⚫ <span style='color: #888888;'>**OFF**</span>", unsafe_allow_html=True)

                # Separate ON/OFF buttons
                col_on, col_off = st.columns(2)

                with col_on:
                    if st.button("ON", key=f"on_{light.entity_id}_{idx}", use_container_width=True):
                        from homeassistant_api.errors import HomeassistantAPIError

                        # Determine domain from entity_id
                        domain = light.entity_id.split('.')[0]
                        logger.info(f"💡 ON button pressed: {light.entity_id} (domain: {domain})")
                        try:
                            inspector.client.trigger_service(
                                domain=domain,
                                service="turn_on",
                                entity_id=light.entity_id
                            )
                            logger.info(f"✅ turn_on successful for {light.entity_id}")
                            time.sleep(0.3)
                            st.rerun()
                        except HomeassistantAPIError as e:
                            logger.error(f"❌ turn_on FAILED: {e}")
                            st.error(f"Failed: {e}")

                with col_off:
                    if st.button("OFF", key=f"off_{light.entity_id}_{idx}", use_container_width=True):
                        from homeassistant_api.errors import HomeassistantAPIError

                        # Determine domain from entity_id
                        domain = light.entity_id.split('.')[0]
                        logger.info(f"💡 OFF button pressed: {light.entity_id} (domain: {domain})")
                        try:
                            inspector.client.trigger_service(
                                domain=domain,
                                service="turn_off",
                                entity_id=light.entity_id
                            )
                            logger.info(f"✅ turn_off successful for {light.entity_id}")
                            time.sleep(0.3)
                            st.rerun()
                        except HomeassistantAPIError as e:
                            logger.error(f"❌ turn_off FAILED: {e}")
                            st.error(f"Failed: {e}")

                # Brightness slider if supported
                if capabilities['brightness'] and is_on:
                    brightness = get_brightness(light) or 255
                    new_brightness = st.slider(
                        "💡",
                        0, 255, brightness,
                        key=f"brightness_{light.entity_id}_{idx}",
                        label_visibility="collapsed"
                    )

                    if abs(new_brightness - brightness) > 5:  # Debounce small changes
                        from homeassistant_api.errors import HomeassistantAPIError

                        logger.info(f"💡 BRIGHTNESS CHANGED: {light.entity_id}: {brightness} → {new_brightness}")
                        try:
                            inspector.client.trigger_service(
                                domain="light",
                                service="turn_on",
                                entity_id=light.entity_id,
                                brightness=new_brightness
                            )
                            logger.info(f"✅ Brightness set successfully")
                        except HomeassistantAPIError as e:
                            logger.error(f"❌ Brightness change FAILED: {e}")
                            st.error(f"Brightness control failed: {e}")
                        time.sleep(0.5)  # Give HA time to process

                st.divider()


def render_light_list(lights: List[Entity], inspector: HomeAssistantInspector):
    """Render lights in a list view (like Finder list mode)"""
    for light in lights:
        name = get_friendly_name(light)
        is_on = is_light_on(light)
        capabilities = get_light_capabilities(light)

        # Create columns for list view
        col1, col2, col3, col4 = st.columns([3, 1, 2, 2])

        with col1:
            st.write(f"💡 **{name}**")

        with col2:
            # Separate ON/OFF buttons
            btn_col1, btn_col2 = st.columns(2)

            with btn_col1:
                if st.button("ON", key=f"list_on_{light.entity_id}", use_container_width=True):
                    from homeassistant_api.errors import HomeassistantAPIError

                    # Determine domain from entity_id
                    domain = light.entity_id.split('.')[0]
                    logger.info(f"💡 ON button pressed: {light.entity_id} (domain: {domain})")
                    try:
                        inspector.client.trigger_service(
                            domain=domain,
                            service="turn_on",
                            entity_id=light.entity_id
                        )
                        logger.info(f"✅ turn_on successful for {light.entity_id}")
                        time.sleep(0.3)
                        st.rerun()
                    except HomeassistantAPIError as e:
                        logger.error(f"❌ turn_on FAILED: {e}")
                        st.error(f"Failed: {e}")

            with btn_col2:
                if st.button("OFF", key=f"list_off_{light.entity_id}", use_container_width=True):
                    from homeassistant_api.errors import HomeassistantAPIError

                    # Determine domain from entity_id
                    domain = light.entity_id.split('.')[0]
                    logger.info(f"💡 OFF button pressed: {light.entity_id} (domain: {domain})")
                    try:
                        inspector.client.trigger_service(
                            domain=domain,
                            service="turn_off",
                            entity_id=light.entity_id
                        )
                        logger.info(f"✅ turn_off successful for {light.entity_id}")
                        time.sleep(0.3)
                        st.rerun()
                    except HomeassistantAPIError as e:
                        logger.error(f"❌ turn_off FAILED: {e}")
                        st.error(f"Failed: {e}")

        with col3:
            # Brightness slider if supported
            if capabilities['brightness'] and is_on:
                brightness = get_brightness(light) or 255
                new_brightness = st.slider(
                    "Brightness",
                    0, 255, brightness,
                    key=f"list_brightness_{light.entity_id}",
                    label_visibility="collapsed"
                )

                if abs(new_brightness - brightness) > 5:
                    inspector.client.trigger_service(
                        domain="light",
                        service="turn_on",
                        entity_id=light.entity_id,
                        brightness=new_brightness
                    )
                    time.sleep(0.5)  # Give HA time to process
            else:
                st.write("—")

        with col4:
            # Color picker if supported
            if capabilities['color'] and is_on:
                rgb = get_rgb_color(light)
                if rgb:
                    color_hex = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
                else:
                    color_hex = "#FFFFFF"

                new_color = st.color_picker(
                    "Color",
                    color_hex,
                    key=f"list_color_{light.entity_id}",
                    label_visibility="collapsed"
                )

                # Convert hex to RGB
                new_rgb = tuple(int(new_color[i:i+2], 16) for i in (1, 3, 5))

                if new_rgb != rgb:
                    inspector.client.trigger_service(
                        domain="light",
                        service="turn_on",
                        entity_id=light.entity_id,
                        rgb_color=list(new_rgb)
                    )
                    time.sleep(0.5)  # Give HA time to process
            else:
                st.write("—")

        st.divider()


def main():
    """Main Streamlit app"""

    # Sidebar configuration
    with st.sidebar:
        st.title("⚙️ Dashboard Settings")

        # View mode selector
        view_mode = st.radio(
            "View Mode",
            ["Grid View", "List View"],
            index=0
        )

        # Manual refresh button
        if st.button("🔄 Refresh Now"):
            logger.info("🔄 Manual refresh requested by user")
            st.rerun()  # Explicit user action - one of the rare valid uses

        st.divider()

        # Info
        st.caption(f"Showing lights active in the last {INACTIVE_THRESHOLD_DAYS} days")

    # Main content
    st.title("💡 Light Dashboard")

    # Get inspector (fresh on every Streamlit rerun = fresh state)
    from homeassistant_api.errors import HomeassistantAPIError
    from requests.exceptions import ConnectionError, Timeout

    try:
        inspector = get_inspector()
    except (HomeassistantAPIError, ConnectionError, Timeout) as e:
        st.error(f"Failed to connect to Home Assistant: {e}")
        logger.error(f"❌ Connection failed: {e}")
        return

    # Get all lights AND remotes (fresh from HA via fresh inspector)
    all_lights = inspector.lights
    all_remotes = inspector.get_entities_by_domain('remote')

    # Combine lights and remotes (remotes that act like lights, e.g., Broadlink IR)
    all_controllable = all_lights + all_remotes

    logger.info(f"📊 Retrieved {len(all_lights)} lights + {len(all_remotes)} remotes = {len(all_controllable)} total controllable entities")

    if not all_controllable:
        st.warning("No controllable entities found in Home Assistant")
        logger.warning("⚠️  No lights or remotes found!")
        return

    # Filter active entities
    active_entities = [entity for entity in all_controllable if is_light_active(entity)]
    logger.info(f"📊 {len(active_entities)} entities active (within {INACTIVE_THRESHOLD_DAYS} days)")

    # Log current state of all active entities
    on_entities = [entity for entity in active_entities if is_light_on(entity)]
    logger.info(f"💡 Currently ON: {len(on_entities)} entities")
    for entity in on_entities:
        logger.info(f"   ✓ {entity.entity_id}: {entity.state.state}")

    # Group by room
    grouped_lights = group_lights_by_room(active_entities)

    # Display stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Entities", len(all_controllable))
        st.caption(f"{len(all_lights)} lights, {len(all_remotes)} remotes")
    with col2:
        st.metric("Active Entities", len(active_entities))
    with col3:
        on_count = sum(1 for entity in active_entities if is_light_on(entity))
        st.metric("Currently On", on_count)

    st.divider()

    # Render grouped lights
    for room, lights in grouped_lights.items():
        with st.expander(f"📍 {room} ({len(lights)} lights)", expanded=True):
            if view_mode == "Grid View":
                render_light_grid(lights, inspector)
            else:
                render_light_list(lights, inspector)

    # No auto-refresh needed - Streamlit reruns on every interaction
    # Fresh state is fetched at the top of main() on each rerun


if __name__ == "__main__":
    main()
