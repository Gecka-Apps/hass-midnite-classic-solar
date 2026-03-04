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

"""Config flow for the Midnite Classic Solar integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pymodbus.client import AsyncModbusTcpClient

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DEVICE_TYPES,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(
            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
        ): vol.All(int, vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
    }
)


async def _test_connection(
    host: str, port: int
) -> tuple[dict[str, Any] | None, str | None]:
    """Validate Modbus connection and identify the Classic."""
    client = AsyncModbusTcpClient(host=host, port=port, timeout=5)
    try:
        await client.connect()
        if not client.connected:
            return None, "cannot_connect"

        # Read first 12 registers to get device type + unit ID
        result = await client.read_holding_registers(
            4100, count=12, device_id=DEFAULT_SLAVE_ID
        )
        if result.isError():
            return None, "cannot_connect"

        regs = result.registers
        device_type = regs[0] & 0xFF               # reg 4101 LSB
        # regs[1-9] = regs 4102-4110 (skipped)
        unit_id = (regs[11] << 16) | regs[10]      # regs 4111-4112 (LE word order)
        if unit_id >= 0x80000000:                   # signed 32-bit
            unit_id -= 0x100000000

        if device_type not in DEVICE_TYPES:
            return None, "invalid_device"

        return {
            "device_type": device_type,
            "unit_id": unit_id,
        }, None
    except Exception:
        _LOGGER.exception("Error testing connection to Classic at %s:%s", host, port)
        return None, "cannot_connect"
    finally:
        client.close()


class ClassicSolarConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Midnite Classic Solar."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            info, error = await _test_connection(
                user_input[CONF_HOST], user_input[CONF_PORT]
            )
            if error:
                errors["base"] = error
            else:
                await self.async_set_unique_id(str(info["unit_id"]))
                self._abort_if_unique_id_configured()

                model = DEVICE_TYPES.get(
                    info["device_type"], f"Classic {info['device_type']}"
                )
                return self.async_create_entry(
                    title=f"Midnite {model}",
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PORT: user_input[CONF_PORT],
                        CONF_SCAN_INTERVAL: user_input.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                        "unit_id": info["unit_id"],
                        "device_type": info["device_type"],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            # Skip connection test — the Classic only accepts one Modbus TCP
            # connection at a time and the coordinator already holds one.
            # The reload triggered by async_update_reload_and_abort will
            # validate the new connection parameters.
            return self.async_update_reload_and_abort(
                entry,
                data={**entry.data, **user_input},
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST, default=entry.data.get(CONF_HOST)
                    ): str,
                    vol.Required(
                        CONF_PORT, default=entry.data.get(CONF_PORT, DEFAULT_PORT)
                    ): int,
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=entry.data.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(
                        int,
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    ),
                }
            ),
            errors=errors,
        )
