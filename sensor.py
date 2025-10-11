"""Platform for sensor integration."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass
)
from homeassistant.const import (
    UnitOfPower,
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfEnergy
)

from homeassistant.config_entries import ConfigEntry

from .const import (
    ATTR_POWER_L1,
    ATTR_POWER_L2,
    ATTR_POWER_L3,
    ATTR_VOLTAGE_L1,
    ATTR_VOLTAGE_L2,
    ATTR_VOLTAGE_L3,
    ATTR_CURRENT_L1,    
    ATTR_CURRENT_L2,
    ATTR_CURRENT_L3,
    ATTR_POWER_TOTAL,
    ATTR_ENERGY_TOTAL,
    ATTR_MAC_ADDRESS,
    ATTR_CREATION_TIME,
    ATTR_ID,
    ATTR_ITEM_CATEGORY,
    ATTR_ITEM_SUB_TYPE,
    ATTR_ITEM_TYPE,
    ATTR_NAME,
    ATTR_SYSTEM_NAME,
    ATTR_TIME_ZONE
)
from .coordinator import PerificCoordinator
from collections.abc import Callable
from dataclasses import dataclass
from .perific import ItemPacket

from .entity import PerificEntity

@dataclass(frozen=True, kw_only=True)
class PerificSensorEntityDescription(SensorEntityDescription):
    value_func: Callable[[ItemPacket], float | None]


def safe_get(data, attr, index):
    try:
        value = getattr(data, attr)
        if value:
            if index == -1:
                return value
            elif len(value) > index:
                return value[index]
    except Exception:
        return None
    return None


SENSOR_TYPES: tuple[PerificSensorEntityDescription, ...] = (
    PerificSensorEntityDescription(
        key=ATTR_VOLTAGE_L1,
        translation_key="voltage_l1",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=0,
        value_func=lambda data: safe_get(data.data, "huavg", 0),
    ),
    PerificSensorEntityDescription(
        key=ATTR_VOLTAGE_L2,
        translation_key="voltage_l2",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=0,
        value_func=lambda data: safe_get(data.data, "huavg", 1),
    ),
    PerificSensorEntityDescription(
        key=ATTR_VOLTAGE_L3,
        translation_key="voltage_l3",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=0,
        value_func=lambda data: safe_get(data.data, "huavg", 2),
    ),
    
    PerificSensorEntityDescription(
        key=ATTR_CURRENT_L1,
        translation_key="current_l1",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        value_func=lambda data: safe_get(data.data, "hiavg", 0),
    ),
    PerificSensorEntityDescription(
        key=ATTR_CURRENT_L2,
        translation_key="current_l2",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        value_func=lambda data: safe_get(data.data, "hiavg", 1),
    ),
    PerificSensorEntityDescription(
        key=ATTR_CURRENT_L3,
        translation_key="current_l3",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        value_func=lambda data: safe_get(data.data, "hiavg", 2),
    ),
    
    
    PerificSensorEntityDescription(
        key=ATTR_POWER_L1,
        translation_key="power_l1",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value_func=lambda data: (
            (safe_get(data.data, "hiavg", 0) or 0)
            * (safe_get(data.data, "huavg", 0) or 0)
            / 1000
        ),
    ),
    PerificSensorEntityDescription(
        key=ATTR_POWER_L2,
        translation_key="power_l2",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value_func=lambda data: (
            (safe_get(data.data, "hiavg", 1) or 0)
            * (safe_get(data.data, "huavg", 1) or 0)
            / 1000
        ),
    ),
    PerificSensorEntityDescription(
        key=ATTR_POWER_L3,
        translation_key="power_l3",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value_func=lambda data: (
            (safe_get(data.data, "hiavg", 2) or 0)
            * (safe_get(data.data, "huavg", 2) or 0)
            / 1000
        ),
    ),
    PerificSensorEntityDescription(
        key=ATTR_POWER_TOTAL,
        translation_key="power_total",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value_func=lambda data: sum(
            (safe_get(data.data, "hiavg", i) or 0)
            * (safe_get(data.data, "huavg", i) or 0)
            for i in range(3)
        )
        / 1000,
    ),
    PerificSensorEntityDescription(
        key=ATTR_ENERGY_TOTAL,
        translation_key="energy_total",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=3,
        value_func=lambda data: safe_get(data.data, "hwi", -1),
    ),
    PerificSensorEntityDescription(
        key=ATTR_MAC_ADDRESS,
        translation_key="mac_address",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        value_func=lambda data: None,  # Placeholder, not used
    ),
        PerificSensorEntityDescription(
        key=ATTR_CREATION_TIME,
        translation_key="creation_time",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        value_func=lambda data: None,  # Placeholder, not used
    ),
    PerificSensorEntityDescription(
        key=ATTR_ID,
        translation_key="item_id",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        value_func=lambda data: None,  # Placeholder, not used
    ),
    PerificSensorEntityDescription(
        key=ATTR_ITEM_CATEGORY,
        translation_key="item_category",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        value_func=lambda data: None,  # Placeholder, not used
    ),
    PerificSensorEntityDescription(
        key=ATTR_ITEM_SUB_TYPE,
        translation_key="item_sub_type",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        value_func=lambda data: None,  # Placeholder, not used
    ),
    PerificSensorEntityDescription(
        key=ATTR_ITEM_TYPE,
        translation_key="item_type",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        value_func=lambda data: None,  # Placeholder, not used
    ),
    PerificSensorEntityDescription(
        key=ATTR_NAME,
        translation_key="name",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        value_func=lambda data: None,  # Placeholder, not used
    ),
    PerificSensorEntityDescription(
        key=ATTR_SYSTEM_NAME,
        translation_key="system_name",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        value_func=lambda data: None,  # Placeholder, not used
    ),
    PerificSensorEntityDescription(
        key=ATTR_TIME_ZONE,
        translation_key="time_zone",
        device_class=None,
        state_class=None,
        native_unit_of_measurement=None,
        value_func=lambda data: None,  # Placeholder, not used
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensors for passed config_entry in HA."""
    coordinator = config_entry.runtime_data
    
    entities = []
    for device in coordinator.devices:
        sensors = []
        device_id = device.id
        if device.type == "Phase":
            sensors.extend([
                ATTR_CURRENT_L1,
                ATTR_CURRENT_L2,
                ATTR_CURRENT_L3,
                ATTR_VOLTAGE_L1,
                ATTR_VOLTAGE_L2,
                ATTR_VOLTAGE_L3,
                ATTR_POWER_L1,
                ATTR_POWER_L2,
                ATTR_POWER_L3,
                ATTR_POWER_TOTAL,
                ATTR_ENERGY_TOTAL,
                ATTR_MAC_ADDRESS,
                ATTR_CREATION_TIME,
                ATTR_ID,
                ATTR_ITEM_CATEGORY,
                ATTR_ITEM_SUB_TYPE,
                ATTR_ITEM_TYPE,
                ATTR_NAME,
                ATTR_SYSTEM_NAME,
                ATTR_TIME_ZONE
            ])
        
        for sensor_key in SENSOR_TYPES:
            if sensor_key.key in sensors:
                description = sensor_key
                entities.append(
                    PerificSensor(coordinator, device_id, description)
                )
    
    async_add_entities(entities)
        
class PerificSensor(PerificEntity, SensorEntity):
    entity_description: PerificSensorEntityDescription
    def __init__(self, coordinator: PerificCoordinator, device_id: int, description: PerificSensorEntityDescription) -> None:
        PerificEntity.__init__(self, coordinator, device_id)
        SensorEntity.__init__(self)
        self.entity_description = description
        self._attr_unique_id = f"{self.device.id}_{description.key}"
        self._attr_translation_key = description.translation_key
        self._attr_name = f"Perific {self.device.name} {description.translation_key.replace('_', ' ').capitalize()}"
       
    @property 
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        key = self.entity_description.key
        # Device metadata-based sensors
        if key == ATTR_MAC_ADDRESS:
            return self.device.mac
        if key == ATTR_ID:
            return self.device.id
        if key == ATTR_NAME:
            return self.device.name
        if key == ATTR_SYSTEM_NAME:
            return getattr(self.device, "system_name", None)
        if key == ATTR_ITEM_TYPE:
            return getattr(self.device, "type", None)
        if key == ATTR_ITEM_SUB_TYPE:
            return getattr(self.device, "item_sub_type", None)
        if key == ATTR_ITEM_CATEGORY:
            return getattr(self.device, "item_category", None)
        if key == ATTR_TIME_ZONE:
            return getattr(self.device, "time_zone", None)
        if key == ATTR_CREATION_TIME:
            return getattr(self.device, "creation_time", None)

        latest_data = self.coordinator.get_device_data(self.device.id)
        if not latest_data:
            return None
        try:
            if key == ATTR_ENERGY_TOTAL:
                return self.entity_description.value_func(latest_data.phase_minute)
            return self.entity_description.value_func(latest_data.phase_real_time)
        
        except Exception as e:
            _LOGGER.exception("Error in native_value computation for sensor '%s' on device '%s': %s", self.entity_description.key, self.device.id, e)
            return None
