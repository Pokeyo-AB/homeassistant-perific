"""Diagnostics support for Perific Meter integration."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import PerificCoordinator
from .hub import Hub

import logging

_LOGGER = logging.getLogger(__name__)

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    try:
        coordinator: PerificCoordinator = entry.runtime_data
        if coordinator is None:
            raise ValueError("Coordinator not initialized for this entry")

        hub: Hub = coordinator.hub

        # Mask sensitive fields in entry data
        entry_data = dict(entry.data)
        if "password" in entry_data:
            entry_data["password"] = "***"
        if "username" in entry_data:
            entry_data["username"] = entry_data["username"][:2] + "***"

        # Collect device information
        devices = [
            {
                "id": device.id,
                "name": device.name,
                "type": device.type,
                "mac": device.mac,
            }
            for device in coordinator.devices
        ]

        # Collect latest sensor data
        latest_data = [
            {
                "item_id": item.item_id,
                "latest_packets": item.latest_packets.dict(),
            }
            for item in coordinator.data or []
        ]

        # Include hub metadata
        hub_info = {
            "host": getattr(hub, "host", None),
            "authenticated": hub.token is not None,
        }

        return {
            "entry_data": entry_data,
            "hub": hub_info,
            "devices": devices,
            "latest_data": latest_data,
        }

    
    except Exception as e:
        _LOGGER.exception("Failed to generate diagnostics: %s", e)
        return {"error": str(e)}

