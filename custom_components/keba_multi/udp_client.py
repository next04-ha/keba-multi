from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from .const import UDP_PORT

_LOGGER = logging.getLogger(__name__)


class KebaUdpClient(asyncio.DatagramProtocol):
    """Single UDP client shared by all KEBA hosts."""

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._transport: asyncio.DatagramTransport | None = None
        self._waiters: dict[tuple[str, str], asyncio.Future[dict[str, Any]]] = {}
        self._last: dict[str, dict[str, Any]] = {}

    async def async_start(self) -> None:
        if self._transport is not None:
            return

        # IMPORTANT: bind to random local port to support multiple stations
        transport, _ = await self._loop.create_datagram_endpoint(
            lambda: self,
            local_addr=("0.0.0.0", 0),
        )
        self._transport = transport
        sockname = transport.get_extra_info("sockname")
        _LOGGER.debug("KEBA UDP socket bound on %s", sockname)

    def connection_lost(self, exc: Exception | None) -> None:
        _LOGGER.debug("UDP connection lost: %s", exc)

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        host, _port = addr
        text = data.decode(errors="ignore").strip()

        # Replies are JSON-ish, each line terminated with LF in the payload. :contentReference[oaicite:5]{index=5}
        # We try to parse as JSON object; if it fails, keep raw.
        payload: dict[str, Any] | None = None
        if text.startswith("{") and text.endswith("}"):
            try:
                payload = json.loads(text)
            except Exception:  # noqa: BLE001
                payload = None

        if payload is None:
            # Example non-JSON replies: "TCH-OK :done" or firmware string from "i". :contentReference[oaicite:6]{index=6}
            payload = {"raw": text}

        self._last[host] = payload

        # If this is a report, resolve the waiter by (host, report_id)
        report_id = str(payload.get("ID")) if "ID" in payload else None
        if report_id:
            key = (host, report_id)
            fut = self._waiters.pop(key, None)
            if fut and not fut.done():
                fut.set_result(payload)

    async def send_and_wait_report(
        self, host: str, report_id: str, command: str, timeout: float = 3.0
    ) -> dict[str, Any]:
        """Send command and wait for a JSON report with matching ID."""
        await self.async_start()
        assert self._transport is not None

        key = (host, report_id)
        fut: asyncio.Future[dict[str, Any]] = self._loop.create_future()
        self._waiters[key] = fut

        _LOGGER.debug("UDP send to %s: %s", host, command)
        self._transport.sendto(command.encode("ascii", "ignore"), (host, UDP_PORT))

        try:
            return await asyncio.wait_for(fut, timeout=timeout)
        finally:
            self._waiters.pop(key, None)

    def get_last(self, host: str) -> dict[str, Any] | None:
        return self._last.get(host)
