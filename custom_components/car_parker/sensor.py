"""Sensors for Car Parker."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CarParkerCoordinator


def _get_status(data: dict) -> str | None:
    return data.get("status")


def _get_urgency(data: dict) -> str | None:
    return data.get("urgency")


def _get_next_sweep(data: dict) -> datetime | None:
    sweep = data.get("next_sweeping") or {}
    iso = sweep.get("start_iso")
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso)
    except ValueError:
        return None


def _get_next_sweep_label(data: dict) -> str | None:
    sweep = data.get("next_sweeping") or {}
    return sweep.get("when_label")


def _get_location(data: dict) -> str | None:
    loc = data.get("location")
    if not loc:
        return None
    parts = [loc.get("street")]
    if loc.get("block_limits"):
        parts.append(loc["block_limits"])
    if loc.get("side") and loc["side"] != "Unknown":
        parts.append(f"{loc['side']} side")
    return ", ".join(p for p in parts if p)


def _get_time_limit(data: dict) -> str | None:
    tl = data.get("time_limit")
    if not tl:
        return None
    if tl.get("hrlimit"):
        h = tl["hrlimit"]
        h_str = str(int(h)) if h == int(h) else str(h)
        out = f"{h_str}-hour parking"
        if tl.get("from_time") and tl.get("to_time"):
            out += f" {tl['from_time']}–{tl['to_time']}"
        if tl.get("days"):
            out += f" ({tl['days']})"
        return out
    return tl.get("regulation") or "Parking restriction"


SENSORS: tuple[
    tuple[SensorEntityDescription, Callable[[dict], Any]], ...
] = (
    (
        SensorEntityDescription(
            key="status",
            name="Car parker status",
            icon="mdi:car-info",
        ),
        _get_status,
    ),
    (
        SensorEntityDescription(
            key="urgency",
            name="Car parker urgency",
            icon="mdi:gauge",
        ),
        _get_urgency,
    ),
    (
        SensorEntityDescription(
            key="next_sweep",
            name="Next street sweep",
            device_class=SensorDeviceClass.TIMESTAMP,
            icon="mdi:broom",
        ),
        _get_next_sweep,
    ),
    (
        SensorEntityDescription(
            key="next_sweep_label",
            name="Next street sweep label",
            icon="mdi:calendar-clock",
        ),
        _get_next_sweep_label,
    ),
    (
        SensorEntityDescription(
            key="location",
            name="Parked location",
            icon="mdi:map-marker",
        ),
        _get_location,
    ),
    (
        SensorEntityDescription(
            key="time_limit",
            name="Parking time limit",
            icon="mdi:timer-sand",
        ),
        _get_time_limit,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: CarParkerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        CarParkerSensor(coordinator, entry, desc, fn) for desc, fn in SENSORS
    )


class CarParkerSensor(CoordinatorEntity[CarParkerCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CarParkerCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
        value_fn: Callable[[dict], Any],
    ):
        super().__init__(coordinator)
        self.entity_description = description
        self._value_fn = value_fn
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        return self._value_fn(self.coordinator.data or {})
