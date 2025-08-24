"""DataUpdateCoordinator for Perific Meter integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import PerificHub, PerificDevice
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class PerificCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Perific Meter data update coordinator."""

    def __init__(self, hass: HomeAssistant, perific_hub: PerificHub) -> None:
        self.perific_hub = perific_hub
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.devices: list[PerificDevice] = []

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            # Discover devices once
            if not self.devices:
                self.devices = await self.perific_hub.async_get_devices()
                if not self.devices:
                    raise UpdateFailed("No devices found for the Perific account.")

            updated: dict[str, Any] = {}
            # Refresh metrics for each device
            for device in self.devices:
                await self.perific_hub.async_update_device_metrics(device)
                updated[str(device.id)] = device.metrics

            return updated
        except Exception as err:
            _LOGGER.error("Perific API error: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err
