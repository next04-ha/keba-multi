from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .udp_client import KebaUdpClient
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class KebaCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, client: KebaUdpClient, host: str, scan_interval: int):
        super().__init__(
            hass,
            _LOGGER,
            name=f"KEBA {host}",
            update_interval=timedelta(seconds=max(2, int(scan_interval or DEFAULT_SCAN_INTERVAL))),
        )
        self.client = client
        self.host = host

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            # report 2: state/plug/enable/currents :contentReference[oaicite:7]{index=7}
            r2 = await self.client.send_and_wait_report(self.host, "2", "report 2", timeout=3.0)
            # report 3: power/energy/volt/currents :contentReference[oaicite:8]{index=8}
            r3 = await self.client.send_and_wait_report(self.host, "3", "report 3", timeout=3.0)

            # Merge reports (r3 can override overlaps, but mostly different keys)
            data = {}
            data.update(r2)
            data.update(r3)
            return data
        except Exception as ex:  # noqa: BLE001
            raise UpdateFailed(str(ex)) from ex
