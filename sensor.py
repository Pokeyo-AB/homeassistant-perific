"""Sensor entities for Perific integration."""
from __future__ import annotations
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    UnitOfPower,
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfFrequency,
    UnitOfEnergy,
    PERCENTAGE,
)
from homeassistant.helpers.typing import StateType
from homeassistant.helpers import device_registry as dr


from .entity import PerificEntity
from .coordinator import PerificCoordinator
from .client import PerificDevice
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

def get_metric_metadata(metric_key: str) -> dict[str, str] | None:
    """Return metadata for a metric key (supports L1/L2/L3/N)."""

    API_METRIC_MAP = {
        "voltage": {
            "name": "Voltage",
            "unit": UnitOfElectricPotential.VOLT,
            "device_class": "voltage",
            "state_class": "measurement",
        },
        "current": {
            "name": "Current",
            "unit": UnitOfElectricCurrent.AMPERE,
            "device_class": "current",
            "state_class": "measurement",
        },
        "current_avg_high": {
            "name": "Current (High Avg)",
            "unit": UnitOfElectricCurrent.AMPERE,
            "device_class": "current",
            "state_class": "measurement",
        },
        "current_avg": {
            "name": "Current (Avg)",
            "unit": UnitOfElectricCurrent.AMPERE,
            "device_class": "current",
            "state_class": "measurement",
        },
        "current_min": {
            "name": "Current (Min)",
            "unit": UnitOfElectricCurrent.AMPERE,
            "device_class": "current",
            "state_class": "measurement",
        },
        "current_max": {
            "name": "Current (Max)",
            "unit": UnitOfElectricCurrent.AMPERE,
            "device_class": "current",
            "state_class": "measurement",
        },
        "power": {
            "name": "Power",
            "unit": UnitOfPower.WATT,
            "device_class": "power",
            "state_class": "measurement",
        },
        "frequency": {
            "name": "Frequency",
            "unit": UnitOfFrequency.HERTZ,
            "device_class": "frequency",
            "state_class": "measurement",
        },
        "pf": {
            "name": "Power Factor",
            "unit": PERCENTAGE,
            "device_class": "power_factor",
            "state_class": "measurement",
        },
        "energy": {
            "name": "Energy",
            "unit": UnitOfEnergy.KILO_WATT_HOUR,
            "device_class": "energy",
            "state_class": "total_increasing",
        },
        "reactive_power_min": {
            "name": "Reactive Power (Min)",
            "unit": "var",
            "device_class": "reactive_power",
            "state_class": "measurement",
        },
        "reactive_power_max": {
            "name": "Reactive Power (Max)",
            "unit": "var",
            "device_class": "reactive_power",
            "state_class": "measurement",
        },
        "energy_positive_min": {
            "name": "Positive Energy (Min)",
            "unit": UnitOfEnergy.KILO_WATT_HOUR,
            "device_class": "energy",
            "state_class": "total_increasing",
        },
        "energy_positive_max": {
            "name": "Positive Energy (Max)",
            "unit": UnitOfEnergy.KILO_WATT_HOUR,
            "device_class": "energy",
            "state_class": "total_increasing",
        },
        "energy_positive_avg": {
            "name": "Positive Energy (Avg)",
            "unit": UnitOfEnergy.KILO_WATT_HOUR,
            "device_class": "energy",
            "state_class": "total_increasing",
        },
        "energy_negative_min": {
            "name": "Negative Energy (Min)",
            "unit": UnitOfEnergy.KILO_WATT_HOUR,
            "device_class": "energy",
            "state_class": "total_increasing",
        },
        "energy_negative_max": {
            "name": "Negative Energy (Max)",
            "unit": UnitOfEnergy.KILO_WATT_HOUR,
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    }

    # Split out phase suffix (_L1/_L2/_L3/_N)
    suffix = None
    if metric_key.endswith(("_L1", "_L2", "_L3", "_N")):
        metric_key, suffix = metric_key.rsplit("_", 1)

    # Find time resolution (phaserealtime / phaseminute / phasehour / phaseday)
    for source_prefix in ("phaserealtime_", "phaseminute_", "phasehour_", "phaseday_"):
        if metric_key.lower().startswith(source_prefix):
            source_name = source_prefix[:-1]  # drop trailing _
            metric_name = metric_key[len(source_prefix):]
            if metric_name in API_METRIC_MAP:
                friendly_source = {
                    "phaserealtime": "Real Time",
                    "phaseminute": "Minute",
                    "phasehour": "Hour",
                    "phaseday": "Day",
                }[source_name]
                meta = dict(API_METRIC_MAP[metric_name])
                # Add phase suffix if present
                if suffix:
                    meta["name"] = f"{friendly_source} {meta['name']} ({suffix})"
                else:
                    meta["name"] = f"{friendly_source} {meta['name']}"
                return meta
    return None


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: PerificCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []
    # Log the device information to aid debugging
    _LOGGER.debug("Starting sensor setup for Perific devices.")
    _LOGGER.debug("Found devices: '%s'", coordinator.devices)
    dev_reg = dr.async_get(hass)

    for device in coordinator.devices:
        _LOGGER.debug("Found device '%s' (%s) with %d metrics.",device.name,device.id,len(device.metrics))
        # explicitly register device in registry
        _LOGGER.debug("Found devices: '%s'", coordinator.devices)
        _LOGGER.debug("config_entry_id= '%s'", entry.entry_id)
        _LOGGER.debug("identifiers= '%s'", {(DOMAIN, str(device.id))})  # must match entity.py
        _LOGGER.debug("name= '%s'", device.name)
        _LOGGER.debug("manufacturer= '%s'", "Perific")
        _LOGGER.debug("model= '%s'", f"{device.item_type} ({device.item_sub_type})")
        _LOGGER.debug("sw_version= '%s'", device.fw)
        _LOGGER.debug("hw_version= '%s'", device.hw)
        _LOGGER.debug("connections= '%s'", {(dr.CONNECTION_NETWORK_MAC, device.mac)} if device.mac else set())
        _LOGGER.debug("configuration_url= '%s'", "https://app.enegic.com/")
        mac = (device.mac or "").upper()
        connections = ({(dr.CONNECTION_NETWORK_MAC, mac)}
            if mac and mac not in {"00:00:00:00:00:00", "02:00:00:00:00:00"}
            else set()
        )
        _LOGGER.debug("connections= '%s'", connections)
        dev_reg.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, str(device.id))},  # must match entity.py
            name=device.name,
            manufacturer="Perific",
            model=f"{device.item_type} ({device.item_sub_type})",
            sw_version=device.fw,
            hw_version=device.hw,
            #connections={(dr.CONNECTION_NETWORK_MAC, device.mac)} if device.mac else set(),
            connections=connections,
            configuration_url="https://app.enegic.com/",
        )
        for key in list(device.metrics.keys()):
            meta = get_metric_metadata(key)
            if meta:
                entities.append(PerificSensor(coordinator, device, key, meta))
    async_add_entities(entities)

class PerificSensor(PerificEntity, SensorEntity):
    """A single metric sensor for a Perific device."""

    def __init__(self, coordinator: PerificCoordinator, device: PerificDevice, metric_key: str, meta: dict[str, str]) -> None:
        super().__init__(coordinator, device)
        self._metric_key = metric_key
        self._attr_name = meta['name']
        #self._attr_unique_id = f"{device.id}_{device.name}_{metric_key}"
        self._attr_unique_id = f"{device.id}_{metric_key}"
        self._attr_native_unit_of_measurement = meta["unit"]
        self._attr_device_class = meta["device_class"]
        self._attr_state_class = meta["state_class"]

    @property
    def native_value(self) -> StateType:
        return self.device.metrics.get(self._metric_key)
