from __future__ import annotations

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_HOST, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .udp_client import KebaUdpClient
from .coordinator import KebaCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: tuple[Platform, ...] = (Platform.SENSOR, Platform.BINARY_SENSOR)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    # Shared UDP client (one socket, random local port)
    if "client" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["client"] = KebaUdpClient(asyncio.get_running_loop())
        await hass.data[DOMAIN]["client"].async_start()

    client: KebaUdpClient = hass.data[DOMAIN]["client"]

    host = entry.data[CONF_HOST]
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = KebaCoordinator(hass, client, host, scan_interval)

    # Optional: get device info once (report 1) to build better device name/serial. :contentReference[oaicite:9]{index=9}
    try:
        info = await client.send_and_wait_report(host, "1", "report 1", timeout=3.0)
        hass.data[DOMAIN].setdefault("info", {})[entry.entry_id] = info
    except Exception:  # noqa: BLE001
        _LOGGER.debug("report 1 not available for %s at setup", host)

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator, "host": host}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok and DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok
