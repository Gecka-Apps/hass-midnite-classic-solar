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

"""Select platform for the Midnite Classic Solar integration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ADDR_WRITE,
    DOMAIN,
    FORCE_CHARGE_STAGES,
    FORCE_CHARGE_STAGES_REVERSE,
    MPPT_MODES,
    MPPT_MODES_REVERSE,
)
from .coordinator import ClassicSolarCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ClassicSolarCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ClassicSolarMPPTSelect(coordinator),
        ClassicSolarForceChargeSelect(coordinator),
    ])


class ClassicSolarMPPTSelect(
    CoordinatorEntity[ClassicSolarCoordinator], SelectEntity
):
    """Select entity for the Classic MPPT mode."""

    _attr_has_entity_name = True
    _attr_translation_key = "mppt_mode"
    _attr_icon = "mdi:solar-power-variant"
    _attr_options = list(MPPT_MODES.values())
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: ClassicSolarCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_mppt_mode"
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str | None:
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get("mppt_mode")
        if raw is None:
            return None
        return MPPT_MODES.get(raw)

    async def async_select_option(self, option: str) -> None:
        value = MPPT_MODES_REVERSE.get(option)
        if value is None:
            return
        await self.coordinator.async_write_register(
            ADDR_WRITE["mppt_mode"], value
        )


class ClassicSolarForceChargeSelect(
    CoordinatorEntity[ClassicSolarCoordinator], SelectEntity
):
    """Select entity for the Classic Force Charge Stage.

    Register 4160 (Force Flag Bits) is write-only per the Modbus spec,
    so current_option is tracked locally and resets to "Normal" on restart.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "force_charge_stage"
    _attr_icon = "mdi:battery-charging"
    _attr_options = list(FORCE_CHARGE_STAGES.values())
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: ClassicSolarCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_force_charge_stage"
        self._attr_device_info = coordinator.device_info
        self._current_option = "Normal"

    @property
    def current_option(self) -> str:
        return self._current_option

    async def async_select_option(self, option: str) -> None:
        value = FORCE_CHARGE_STAGES_REVERSE.get(option)
        if value is None:
            return
        await self.coordinator.async_write_register(
            ADDR_WRITE["force_charge_stage"], value
        )
        self._current_option = option
        self.async_write_ha_state()
