from datetime import timedelta
import logging
from pydantic import BaseModel

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

from .hub import Hub
from .perific import LatestItemPackets, LatestPackets


class Device(BaseModel):
    id: int
    name: str
    type: str
    mac: str|None = None

class PerificCoordinator(DataUpdateCoordinator[list[LatestItemPackets]]):
    """Class to manage fetching Perific data."""

    def __init__(self, hass: HomeAssistant, hub: Hub) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Perific Coordinator",
            update_interval=timedelta(seconds=10),
            setup_method=self.setup,
            update_method=self.update,
        )
        self.hub = hub
        self.devices: list[Device] = []

    async def setup(self) -> None:
        try:
            data = await self.hub.fetch_devices()
            self.devices = [
                Device(id=item.id, name=item.name, type=item.item_type, mac=item.mac_address)
                for item in data
            ]
        except Exception as e:
            _LOGGER.exception("Failed to fetch devices: %s", e)
            self.devices = []

    async def update(self) -> list[LatestItemPackets]:
        try:
            return await self.hub.get_sensor_data()
        except Exception as e:
            _LOGGER.exception("Failed to update sensor data: %s", e)
            return []
   
    def get_device(self, device_id: int) -> Device | None:
        """Get a device by its ID."""
        for device in self.devices:
            if device.id == device_id:
                return device
        return None
    

    def get_device_data(self, device_id: int) -> LatestPackets | None:
        """Get the data for a specific device."""
        if not self.data:
            _LOGGER.warning("No data available in coordinator")
            return None
        for item in self.data:
            if item.item_id == device_id:
                return item.latest_packets
        return None
