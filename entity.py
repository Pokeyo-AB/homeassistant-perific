from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import PerificCoordinator, Device
from .const import DOMAIN

class PerificEntity(CoordinatorEntity[PerificCoordinator]):
    _attr_has_entity_name = True
    device: Device
    def __init__(self, coordinator: PerificCoordinator, device_id: int) -> None:
        super().__init__(coordinator)
        self.device = coordinator.get_device(device_id)
        if not self.device:
            raise ValueError(f"Device with ID {device_id} not found")
        
        self._attr_device_info = DeviceInfo(
            connections={(CONNECTION_NETWORK_MAC, self.device.mac)},
            identifiers={(DOMAIN, self.device.id)},
            manufacturer="Perific Technologies AB",
            model="Perific Max/One",
            name=self.device.name,
            #sw_version="1.0.0",
        )