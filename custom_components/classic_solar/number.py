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

"""Number platform for the Midnite Classic Solar integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ADDR_WRITE, DOMAIN
from .coordinator import ClassicSolarCoordinator


@dataclass(frozen=True, kw_only=True)
class ClassicSolarNumberDescription(NumberEntityDescription):
    """Describe a Classic Solar writable number."""

    register_address: int
    write_scale: float = 1.0  # native value * write_scale = register value


NUMBER_DESCRIPTIONS: list[ClassicSolarNumberDescription] = [
    ClassicSolarNumberDescription(
        key="absorb_voltage",
        translation_key="absorb_voltage",
        register_address=ADDR_WRITE["absorb_voltage"],
        write_scale=10.0,
        device_class=NumberDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        native_min_value=10.0,
        native_max_value=68.0,
        native_step=0.1,
        mode=NumberMode.BOX,
        icon="mdi:sine-wave",
    ),
    ClassicSolarNumberDescription(
        key="float_voltage",
        translation_key="float_voltage",
        register_address=ADDR_WRITE["float_voltage"],
        write_scale=10.0,
        device_class=NumberDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        native_min_value=10.0,
        native_max_value=68.0,
        native_step=0.1,
        mode=NumberMode.BOX,
        icon="mdi:sine-wave",
    ),
    ClassicSolarNumberDescription(
        key="equalize_voltage",
        translation_key="equalize_voltage",
        register_address=ADDR_WRITE["equalize_voltage"],
        write_scale=10.0,
        device_class=NumberDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        native_min_value=10.0,
        native_max_value=68.0,
        native_step=0.1,
        mode=NumberMode.BOX,
        icon="mdi:sine-wave",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarNumberDescription(
        key="absorb_time_setting",
        translation_key="absorb_time_setting",
        register_address=ADDR_WRITE["absorb_time_setting"],
        write_scale=1.0,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        native_min_value=0,
        native_max_value=65535,
        native_step=1,
        mode=NumberMode.BOX,
        icon="mdi:timer-cog-outline",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarNumberDescription(
        key="equalize_time_setting",
        translation_key="equalize_time_setting",
        register_address=ADDR_WRITE["equalize_time_setting"],
        write_scale=1.0,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        native_min_value=0,
        native_max_value=65535,
        native_step=1,
        mode=NumberMode.BOX,
        icon="mdi:timer-cog-outline",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarNumberDescription(
        key="equalize_interval_days",
        translation_key="equalize_interval_days",
        register_address=ADDR_WRITE["equalize_interval_days"],
        write_scale=1.0,
        native_unit_of_measurement="d",
        native_min_value=0,
        native_max_value=365,
        native_step=1,
        mode=NumberMode.BOX,
        icon="mdi:calendar-refresh-outline",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarNumberDescription(
        key="bat_current_limit",
        translation_key="bat_current_limit",
        register_address=ADDR_WRITE["bat_current_limit"],
        write_scale=10.0,
        device_class=NumberDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        native_min_value=0,
        native_max_value=99.0,
        native_step=0.1,
        mode=NumberMode.BOX,
        icon="mdi:current-dc",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarNumberDescription(
        key="max_input_current",
        translation_key="max_input_current",
        register_address=ADDR_WRITE["max_input_current"],
        write_scale=10.0,
        device_class=NumberDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        native_min_value=0,
        native_max_value=99.0,
        native_step=0.1,
        mode=NumberMode.BOX,
        icon="mdi:current-dc",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarNumberDescription(
        key="ending_amps",
        translation_key="ending_amps",
        register_address=ADDR_WRITE["ending_amps"],
        write_scale=10.0,
        device_class=NumberDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        native_min_value=0,
        native_max_value=99.0,
        native_step=0.1,
        mode=NumberMode.BOX,
        icon="mdi:current-dc",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarNumberDescription(
        key="rebulk_volts",
        translation_key="rebulk_volts",
        register_address=ADDR_WRITE["rebulk_volts"],
        write_scale=10.0,
        device_class=NumberDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        native_min_value=10.0,
        native_max_value=68.0,
        native_step=0.1,
        mode=NumberMode.BOX,
        icon="mdi:sine-wave",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarNumberDescription(
        key="nominal_battery_voltage",
        translation_key="nominal_battery_voltage",
        register_address=ADDR_WRITE["nominal_battery_voltage"],
        write_scale=1.0,
        device_class=NumberDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        native_min_value=12,
        native_max_value=120,
        native_step=12,
        mode=NumberMode.BOX,
        icon="mdi:battery-outline",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarNumberDescription(
        key="min_absorb_time",
        translation_key="min_absorb_time",
        register_address=ADDR_WRITE["min_absorb_time"],
        write_scale=1.0,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        native_min_value=0,
        native_max_value=65535,
        native_step=1,
        mode=NumberMode.BOX,
        icon="mdi:timer-cog-outline",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarNumberDescription(
        key="max_temp_comp_voltage",
        translation_key="max_temp_comp_voltage",
        register_address=ADDR_WRITE["max_temp_comp_voltage"],
        write_scale=10.0,
        device_class=NumberDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        native_min_value=10.0,
        native_max_value=68.0,
        native_step=0.1,
        mode=NumberMode.BOX,
        icon="mdi:thermometer",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarNumberDescription(
        key="min_temp_comp_voltage",
        translation_key="min_temp_comp_voltage",
        register_address=ADDR_WRITE["min_temp_comp_voltage"],
        write_scale=10.0,
        device_class=NumberDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        native_min_value=10.0,
        native_max_value=68.0,
        native_step=0.1,
        mode=NumberMode.BOX,
        icon="mdi:thermometer",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarNumberDescription(
        key="temp_comp_value",
        translation_key="temp_comp_value",
        register_address=ADDR_WRITE["temp_comp_value"],
        write_scale=10.0,
        native_unit_of_measurement="mV/°C/2V",
        native_min_value=0,
        native_max_value=10.0,
        native_step=0.5,
        mode=NumberMode.BOX,
        icon="mdi:thermometer",
        entity_registry_enabled_default=False,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ClassicSolarCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ClassicSolarNumber(coordinator, desc) for desc in NUMBER_DESCRIPTIONS
    )


class ClassicSolarNumber(CoordinatorEntity[ClassicSolarCoordinator], NumberEntity):
    """Representation of a Classic Solar writable number."""

    entity_description: ClassicSolarNumberDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ClassicSolarCoordinator,
        description: ClassicSolarNumberDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.key)

    async def async_set_native_value(self, value: float) -> None:
        register_value = int(value * self.entity_description.write_scale)
        await self.coordinator.async_write_register(
            self.entity_description.register_address,
            register_value,
        )
