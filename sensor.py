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
)

from . import HubConfigEntry
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
)
from .coordinator import PerificCoordinator
from collections.abc import Callable
from dataclasses import dataclass
from .perific import ItemPacket

from .entity import PerificEntity

@dataclass(frozen=True, kw_only=True)
class PerificSensorEntityDescription(SensorEntityDescription):
    value_func: Callable[[ItemPacket], float | None]


SENSOR_TYPES: tuple[PerificSensorEntityDescription, ...] = (
    PerificSensorEntityDescription(
        key=ATTR_VOLTAGE_L1,
        translation_key="voltage_l1",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=0,
        value_func=lambda data: data.data.huavg[0],
    ),
    PerificSensorEntityDescription(
        key=ATTR_VOLTAGE_L2,
        translation_key="voltage_l2",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=0,
        value_func=lambda data: data.data.huavg[1],
    ),
    PerificSensorEntityDescription(
        key=ATTR_VOLTAGE_L3,
        translation_key="voltage_l3",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=0,
        value_func=lambda data: data.data.huavg[2],
    ),
    
    PerificSensorEntityDescription(
        key=ATTR_CURRENT_L1,
        translation_key="current_l1",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        value_func=lambda data: data.data.hiavg[0],
    ),
    PerificSensorEntityDescription(
        key=ATTR_CURRENT_L2,
        translation_key="current_l2",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        value_func=lambda data: data.data.hiavg[1],
    ),
    PerificSensorEntityDescription(
        key=ATTR_CURRENT_L3,
        translation_key="current_l3",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        value_func=lambda data: data.data.hiavg[2],
    ),
    
    
    PerificSensorEntityDescription(
        key=ATTR_POWER_L1,
        translation_key="power_l1",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value_func=lambda data: data.data.hiavg[0] * data.data.huavg[0] / 1000,
    ),
    PerificSensorEntityDescription(
        key=ATTR_POWER_L2,
        translation_key="power_l2",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value_func=lambda data: data.data.hiavg[1] * data.data.huavg[1] / 1000,
    ),
    PerificSensorEntityDescription(
        key=ATTR_POWER_L3,
        translation_key="power_l3",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value_func=lambda data: data.data.hiavg[2] * data.data.huavg[2] / 1000,
    ),
    PerificSensorEntityDescription(
        key=ATTR_POWER_TOTAL,
        translation_key="power_total",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=2,
        value_func=lambda data: (
            (data.data.hiavg[0] * data.data.huavg[0] +
            data.data.hiavg[1] * data.data.huavg[1] +
            data.data.hiavg[2] * data.data.huavg[2]) / 1000
        ),
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HubConfigEntry,
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
        latest_data = self.coordinator.get_device_data(self.device.id)
        if not latest_data:
            return None
        return self.entity_description.value_func(latest_data.phase_real_time)