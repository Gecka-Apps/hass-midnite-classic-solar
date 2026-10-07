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

"""Button platform for the Midnite Classic Solar integration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ADDR_FORCE_FLAGS_HIGH, CLEAR_LOGS_CAT_WBJR_NET_AH, DOMAIN
from .coordinator import ClassicSolarCoordinator

# Remote buttons: register 4221 (addr 4220)
ADDR_REMOTE_BUTTONS = 4220


def _write_trigger(
    address: int, value: int
) -> Callable[[ClassicSolarCoordinator], Awaitable[None]]:
    """Build a press handler that writes a one-shot value to a trigger register."""

    async def press(coordinator: ClassicSolarCoordinator) -> None:
        await coordinator.async_write_register(address, value, commit_eeprom=False)

    return press


async def _reset_soc(coordinator: ClassicSolarCoordinator) -> None:
    """Clear the WhizBang Jr net amp-hours counter (ClearLogsCat category 5)."""
    await coordinator.async_clear_logs(CLEAR_LOGS_CAT_WBJR_NET_AH)


@dataclass(frozen=True, kw_only=True)
class ClassicSolarButtonDescription(ButtonEntityDescription):
    """Describe a Classic Solar button."""

    press_fn: Callable[[ClassicSolarCoordinator], Awaitable[None]]


BUTTON_DESCRIPTIONS: list[ClassicSolarButtonDescription] = [
    ClassicSolarButtonDescription(
        key="reset_faults",
        translation_key="reset_faults",
        # ForceResetFaultsF (high word of 0x00800000)
        press_fn=_write_trigger(ADDR_FORCE_FLAGS_HIGH, 0x0080),
        icon="mdi:alert-remove",
    ),
    ClassicSolarButtonDescription(
        key="force_sweep",
        translation_key="force_sweep",
        # ENTER_key
        press_fn=_write_trigger(ADDR_REMOTE_BUTTONS, 0x0010),
        icon="mdi:refresh",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarButtonDescription(
        key="reset_soc",
        translation_key="reset_soc",
        press_fn=_reset_soc,
        icon="mdi:battery-sync",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ClassicSolarCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ClassicSolarButton(coordinator, desc) for desc in BUTTON_DESCRIPTIONS
    )


class ClassicSolarButton(
    CoordinatorEntity[ClassicSolarCoordinator], ButtonEntity
):
    """Representation of a Classic Solar button."""

    entity_description: ClassicSolarButtonDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ClassicSolarCoordinator,
        description: ClassicSolarButtonDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    async def async_press(self) -> None:
        await self.entity_description.press_fn(self.coordinator)
