"""Base entity for Perific integration."""
from __future__ import annotations

import logging
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers import device_registry as dr

from .coordinator import PerificCoordinator
from .client import PerificDevice
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class PerificEntity(CoordinatorEntity[PerificCoordinator]):
    """Defines a base Perific entity."""

    def __init__(self, coordinator: PerificCoordinator, device: PerificDevice) -> None:
        """Initialize the Perific entity."""
        super().__init__(coordinator)
        self.device = device
        self._attr_has_entity_name = True

        # Expose additional attributes as state attributes on the entity
        self._attr_extra_state_attributes = {
            "time_zone": self.device.time_zone,
            "item_category": self.device.item_category,
            "creation_time": self.device.creation_time,
        }


    @property
    def device_info(self) -> DeviceInfo:
        """Return info for device registry."""
        _LOGGER.debug("Found devices: '%s' in Domain '%s'", str(self.device.id), DOMAIN)
        _LOGGER.debug("Found devices: '%s' in Domain '%s'", str(self.device.name), DOMAIN)
        _LOGGER.debug("with entrytype: '%s' ", dr.DeviceEntryType.SERVICE)
        _LOGGER.debug("Found self.devices: '%s' ", str(self.device))
        mac = (self.device.mac or "").upper()
        connections = ({(dr.CONNECTION_NETWORK_MAC, mac)}
        if mac and mac not in {"00:00:00:00:00:00", "02:00:00:00:00:00"}
        else set()
        )
        _LOGGER.debug("Found connections: '%s' ", connections)

        return DeviceInfo(
            #identifiers={(DOMAIN, str(self.device.id))},
            #identifiers={(DOMAIN, f"{self.device.id}_{self.device.name}")},
            #identifiers = {(DOMAIN, f"{self.device.id}_{self.device.name or self.device.id}")}
            #identifiers={(DOMAIN, f"perific_{self.device.id}_{self.device.name or self.device.id}")},
            identifiers={(DOMAIN, str(self.device.id))},
            name=self.device.name,
            manufacturer="Perific",
            model=f"{self.device.item_type} ({self.device.item_sub_type})",
            # Add other attributes for more detailed info
            sw_version=self.device.fw,
            hw_version=self.device.hw,
            #connections={(dr.CONNECTION_NETWORK_MAC, self.device.mac)},
            #connections={(dr.CONNECTION_NETWORK_MAC, self.device.mac)} if self.device.mac else set(),
            connections=connections,
            configuration_url="https://app.enegic.com/",
            # New attributes for a more complete device representation
            suggested_area="Garage" if self.device.item_category == "LocalVirtual" else None,
            entry_type=dr.DeviceEntryType.SERVICE
        )
