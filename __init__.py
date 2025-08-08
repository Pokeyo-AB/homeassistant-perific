"""The Perific Meter integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .hub import Hub
from .coordinator import PerificCoordinator
from .const import API_URL

# Pre-import the sensor platform to avoid blocking import_module
from . import sensor

_LOGGER = logging.getLogger(__name__)
_PLATFORMS: list[Platform] = [Platform.SENSOR]

type HubConfigEntry = ConfigEntry[PerificCoordinator]  # noqa: F821


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry) -> bool:
    """Set up Perific Meter from a config entry."""

    try:
        hub = Hub(API_URL)
        logged_in = await hub.authenticate(entry.data["username"], entry.data["password"])
        if not logged_in:
            LOGGER.error("Authentication failed for user: %s", entry.data["username"])
            return False
    
        entry.runtime_data = PerificCoordinator(hass, hub)
        await entry.runtime_data.async_config_entry_first_refresh()

        await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

        return True
    except Exception as e:
        _LOGGER.exception("Unexpected error during setup: %s", e)
        return False


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: HubConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
