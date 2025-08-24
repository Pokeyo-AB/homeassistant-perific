"""The Perific Meter integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .client import PerificHub
from .coordinator import PerificCoordinator
from .const import DOMAIN, API_URL

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Perific integration from a config entry."""
    _LOGGER.info("Starting setup for Perific integration.")
    hub = PerificHub(hass, API_URL, entry.data["username"], entry.data["password"])
    
    # Ensure credentials are valid before starting platforms
    _LOGGER.debug("Attempting to authenticate with the Perific API.")
    ok = await hub.authenticate()
    if not ok:
        _LOGGER.error("Perific: authentication failed. Please check your credentials.")
        return False
        
    _LOGGER.info("Perific: authentication successful. Setting up coordinator.")
    coordinator = PerificCoordinator(hass, hub)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
