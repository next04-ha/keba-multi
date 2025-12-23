from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import KebaCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: KebaCoordinator = data["coordinator"]
    host = data["host"]

    async_add_entities(
        [
            KebaChargingBinary(coordinator, host),
            KebaPluggedBinary(coordinator, host),
        ]
    )


class KebaChargingBinary(CoordinatorEntity[KebaCoordinator], BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_should_poll = False

    def __init__(self, coordinator: KebaCoordinator, host: str) -> None:
        super().__init__(coordinator)
        self._host = host
        self._attr_name = f"KEBA {host} Charging"
        self._attr_unique_id = f"keba_{host}_charging"

    @property
    def is_on(self) -> bool:
        # State 3 = charging :contentReference[oaicite:14]{index=14}
        return int(self.coordinator.data.get("State", -1)) == 3


class KebaPluggedBinary(CoordinatorEntity[KebaCoordinator], BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PLUG
    _attr_should_poll = False

    def __init__(self, coordinator: KebaCoordinator, host: str) -> None:
        super().__init__(coordinator)
        self._host = host
        self._attr_name = f"KEBA {host} Plugged"
        self._attr_unique_id = f"keba_{host}_plugged"

    @property
    def is_on(self) -> bool:
        # Plug != 0 means something is plugged :contentReference[oaicite:15]{index=15}
        return int(self.coordinator.data.get("Plug", 0)) != 0
