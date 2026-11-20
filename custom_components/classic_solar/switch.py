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

"""Switch platform for the Midnite Classic Solar integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ADDR_WRITE, DOMAIN
from .coordinator import ClassicSolarCoordinator

# Bit 0 of the MPPT Mode register (4164) turns the charger on and off.
MPPT_ENABLED = 0x0001


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ClassicSolarCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ClassicSolarChargingSwitch(coordinator)])


class ClassicSolarChargingSwitch(
    CoordinatorEntity[ClassicSolarCoordinator], SwitchEntity
):
    """Switch that stops and resumes charging.

    Off clears the enable bit of the MPPT Mode register and leaves the mode
    itself in place: the Classic goes to Resting and stays powered, so it
    keeps its counters and its state of charge. The write stays out of the
    EEPROM, and a Classic that restarts comes back in the state it last
    stored.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "charging"
    _attr_icon = "mdi:solar-power"

    def __init__(self, coordinator: ClassicSolarCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_charging"
        self._attr_device_info = coordinator.device_info

    @property
    def _mode(self) -> int | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("mppt_mode")

    @property
    def is_on(self) -> bool | None:
        mode = self._mode
        return None if mode is None else bool(mode & MPPT_ENABLED)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._write(enabled=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._write(enabled=False)

    async def _write(self, enabled: bool) -> None:
        mode = self._mode
        if mode is None:
            raise HomeAssistantError(
                "The MPPT mode of the Classic has not been read yet"
            )
        value = mode | MPPT_ENABLED if enabled else mode & ~MPPT_ENABLED
        await self.coordinator.async_write_register(
            ADDR_WRITE["mppt_mode"], value, commit_eeprom=False
        )
