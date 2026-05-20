"""Platform for switch integration."""

from __future__ import annotations

import asyncio
import re
from typing import Any

import ayla_iot_unofficial
import ayla_iot_unofficial.device

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import NomaIQConfigEntry
from .const import DOMAIN
from .coordinator import NomaIQDataUpdateCoordinator

_EXCLUDED_SWITCH_PROPERTIES = {"light_control", "night_mode"}


def _is_outlet_property(property_name: str) -> bool:
    """Return True when the property name looks like a numbered outlet."""
    return re.fullmatch(r"outlet\d+", property_name) is not None


def _is_switch_property(
    device: ayla_iot_unofficial.device.Device,
    property_name: str,
    property_data: dict[str, Any],
) -> bool:
    """Return True when an Ayla property should be exposed as a switch."""
    if device.oem_model_number == "plug-2":
        return (
            _is_outlet_property(property_name)
            and property_data.get("base_type") == "boolean"
            and not property_data.get("read_only", True)
        )

    return (
        property_name not in _EXCLUDED_SWITCH_PROPERTIES
        and property_data.get("base_type") == "boolean"
        and not property_data.get("read_only", True)
    )


def _property_display_name(property_name: str, property_data: dict[str, Any]) -> str:
    """Build a readable entity name from Ayla property metadata."""
    if _is_outlet_property(property_name):
        return f"Outlet {property_name.removeprefix('outlet')}"

    raw_name = (
        property_data.get("display_name")
        or property_data.get("name")
        or property_name
    )
    return raw_name.replace("_", " ").strip().title()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NomaIQConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Noma IQ Switch platform."""
    coordinator: NomaIQDataUpdateCoordinator = entry.runtime_data
    entities: list[NomaIQSwitchEntity] = []

    for device in coordinator.data:
        for property_name, property_data in device.properties_full.items():
            if _is_switch_property(device, property_name, property_data):
                entities.append(
                    NomaIQSwitchEntity(coordinator, device, property_name, property_data)
                )

    if entities:
        async_add_entities(entities, update_before_add=False)


class NomaIQSwitchEntity(SwitchEntity):
    """Representation of a writable boolean Ayla property as a switch."""

    def __init__(
        self,
        coordinator: NomaIQDataUpdateCoordinator,
        device: ayla_iot_unofficial.device.Device,
        property_name: str,
        property_data: dict[str, Any],
    ) -> None:
        """Initialize the switch entity."""
        self.coordinator = coordinator
        self._device = device
        self._property_name = property_name
        self._is_outlet_property = _is_outlet_property(property_name)
        self._attr_name = _property_display_name(property_name, property_data)
        self._attr_has_entity_name = True
        self._attr_unique_id = (
            f"nomaiq_switch_{device.serial_number}_{property_name.lower()}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.serial_number)},
            name=device.name,
        )

    def _get_current_device(self) -> ayla_iot_unofficial.device.Device | None:
        """Get the current device from coordinator data."""
        data: list[ayla_iot_unofficial.device.Device] = self.coordinator.data
        return next(
            (d for d in data if d.serial_number == self._device.serial_number),
            None,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        device = self._get_current_device()
        if device is None:
            return None
        return device.get_property_value(self._property_name)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn device on."""
        value: bool | int = 1 if self._is_outlet_property else True
        await self._device.async_set_property_value(self._property_name, value)
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn device off."""
        value: bool | int = 0 if self._is_outlet_property else False
        await self._device.async_set_property_value(self._property_name, value)
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    async def async_update(self) -> None:
        """Update the switch state."""
        await self.coordinator.async_request_refresh()
