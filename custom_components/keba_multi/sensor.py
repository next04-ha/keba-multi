from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower, UnitOfEnergy, UnitOfElectricCurrent, UnitOfElectricPotential
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import KebaCoordinator


@dataclass(frozen=True)
class KebaSensorDef:
    key: str
    name: str
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    unit: str | None = None
    transform: callable | None = None


SENSORS = [
    KebaSensorDef(
        key="P",
        name="Charging Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        unit=UnitOfPower.KILO_WATT,
        transform=lambda v: round((v or 0) / 1_000_000, 3),  # mW -> kW
    ),
    KebaSensorDef(
        key="E pres",
        name="Session Energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        transform=lambda v: round((v or 0) / 10_000, 3),  # 0.1Wh -> kWh
    ),
    KebaSensorDef(
        key="E total",
        name="Total Energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        transform=lambda v: round((v or 0) / 10_000, 3),
    ),
    KebaSensorDef(key="U1", name="Voltage L1", device_class=SensorDeviceClass.VOLTAGE, unit=UnitOfElectricPotential.VOLT),
    KebaSensorDef(
        key="I1",
        name="Current L1",
        device_class=SensorDeviceClass.CURRENT,
        unit=UnitOfElectricCurrent.AMPERE,
        transform=lambda v: round((v or 0) / 1000, 2),  # mA -> A
    ),
    KebaSensorDef(
        key="Curr user",
        name="User Current Limit",
        device_class=SensorDeviceClass.CURRENT,
        unit=UnitOfElectricCurrent.AMPERE,
        transform=lambda v: round((v or 0) / 1000, 2),  # mA -> A
    ),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: KebaCoordinator = data["coordinator"]
    host = data["host"]

    entities = [KebaUdpSensor(coordinator, host, s) for s in SENSORS]
    async_add_entities(entities)


class KebaUdpSensor(CoordinatorEntity[KebaCoordinator], SensorEntity):
    _attr_should_poll = False

    def __init__(self, coordinator: KebaCoordinator, host: str, definition: KebaSensorDef) -> None:
        super().__init__(coordinator)
        self._host = host
        self.entity_description = None
        self._def = definition

        self._attr_name = f"KEBA {host} {definition.name}"
        self._attr_unique_id = f"keba_{host}_{definition.key}".replace(" ", "_").lower()

        self._attr_device_class = definition.device_class
        self._attr_state_class = definition.state_class
        self._attr_native_unit_of_measurement = definition.unit

    @property
    def native_value(self) -> Any:
        v = self.coordinator.data.get(self._def.key)
        if self._def.transform:
            try:
                return self._def.transform(v)
            except Exception:  # noqa: BLE001
                return None
        return v
