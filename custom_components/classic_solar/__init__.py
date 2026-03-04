# Copyright (C) 2026 Gecka <https://gecka.nc>
# Author: Laurent Dinclaux <laurent@gecka.nc>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""The Midnite Classic Solar integration."""

from __future__ import annotations

import asyncio
import logging

from pymodbus.client import AsyncModbusTcpClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import ClassicSolarCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.BUTTON, Platform.NUMBER, Platform.SELECT, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Midnite Classic Solar from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    client = AsyncModbusTcpClient(
        host=host,
        port=port,
        timeout=5,
        retries=3,
        reconnect_delay=5,
        reconnect_delay_max=30,
    )

    # The Classic only accepts one Modbus TCP connection at a time.
    # After a reload (e.g. reconfigure), the device may need a moment
    # to release the previous TCP socket before accepting a new one.
    await asyncio.sleep(2)
    for attempt in range(3):
        await client.connect()
        if client.connected:
            break
        _LOGGER.debug(
            "Connection attempt %d failed, retrying in 4s", attempt + 1
        )
        await asyncio.sleep(4)

    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = ClassicSolarCoordinator(
        hass,
        client=client,
        unit_id=entry.data["unit_id"],
        device_type=entry.data["device_type"],
        scan_interval=scan_interval,
    )

    await coordinator.async_load_energy()

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        client.close()
        raise

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: ClassicSolarCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
    else:
        coordinator = hass.data[DOMAIN].get(entry.entry_id)
    if coordinator is not None:
        await coordinator.async_save_energy()
        coordinator.client.close()
    return unload_ok
