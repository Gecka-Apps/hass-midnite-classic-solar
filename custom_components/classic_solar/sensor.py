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

"""Sensor platform for the Midnite Classic Solar integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CHARGE_STAGES, CLASSIC_STATES, DOMAIN, REASONS_FOR_RESTING
from .coordinator import ClassicSolarCoordinator


@dataclass(frozen=True, kw_only=True)
class ClassicSolarSensorDescription(SensorEntityDescription):
    """Describe a Classic Solar sensor."""

    # Optional callable to transform the raw coordinator value
    value_fn: Any = None


SENSOR_DESCRIPTIONS: list[ClassicSolarSensorDescription] = [
    # -- Electrical measurements --
    ClassicSolarSensorDescription(
        key="bat_voltage",
        translation_key="bat_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
    ),
    ClassicSolarSensorDescription(
        key="pv_voltage",
        translation_key="pv_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
    ),
    ClassicSolarSensorDescription(
        key="bat_current",
        translation_key="bat_current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
    ),
    ClassicSolarSensorDescription(
        key="pv_current",
        translation_key="pv_current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
    ),
    ClassicSolarSensorDescription(
        key="power",
        translation_key="power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    ClassicSolarSensorDescription(
        key="last_voc",
        translation_key="last_voc",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
    ),
    # -- Energy --
    ClassicSolarSensorDescription(
        key="energy_today",
        translation_key="energy_today",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=1,
    ),
    ClassicSolarSensorDescription(
        key="amp_hours_today",
        translation_key="amp_hours_today",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="Ah",
        icon="mdi:current-dc",
    ),
    ClassicSolarSensorDescription(
        key="lifetime_energy",
        translation_key="lifetime_energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=1,
    ),
    # -- Charge state --
    ClassicSolarSensorDescription(
        key="charge_stage",
        translation_key="charge_stage",
        value_fn=lambda v: CHARGE_STAGES.get(v, f"Unknown ({v})"),
        icon="mdi:battery-charging",
    ),
    ClassicSolarSensorDescription(
        key="charge_stage",
        translation_key="charge_stage_code",
        icon="mdi:battery-charging",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarSensorDescription(
        key="reason_for_resting",
        translation_key="reason_for_resting",
        value_fn=lambda v: REASONS_FOR_RESTING.get(v, f"Unknown ({v})"),
        icon="mdi:sleep",
    ),
    ClassicSolarSensorDescription(
        key="reason_for_resting",
        translation_key="reason_for_resting_code",
        icon="mdi:sleep",
        entity_registry_enabled_default=False,
    ),
    # -- Temperatures --
    ClassicSolarSensorDescription(
        key="bat_temperature",
        translation_key="bat_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
    ),
    ClassicSolarSensorDescription(
        key="fet_temperature",
        translation_key="fet_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
    ),
    ClassicSolarSensorDescription(
        key="pcb_temperature",
        translation_key="pcb_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
    ),
    # -- Timers --
    ClassicSolarSensorDescription(
        key="float_time_today",
        translation_key="float_time_today",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        icon="mdi:timer-outline",
    ),
    ClassicSolarSensorDescription(
        key="absorb_time",
        translation_key="absorb_time",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        icon="mdi:timer-outline",
    ),
    # -- Whizbang Jr --
    ClassicSolarSensorDescription(
        key="wb_bat_current",
        translation_key="wb_bat_current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    ClassicSolarSensorDescription(
        key="soc",
        translation_key="soc",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        entity_registry_enabled_default=False,
    ),
    ClassicSolarSensorDescription(
        key="remaining_amp_hours",
        translation_key="remaining_amp_hours",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="Ah",
        icon="mdi:battery-outline",
        entity_registry_enabled_default=False,
    ),
    # -- Additional measurements --
    ClassicSolarSensorDescription(
        key="vbatt_reg_setpoint_temp_comp",
        translation_key="vbatt_reg_setpoint_temp_comp",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    ClassicSolarSensorDescription(
        key="state",
        translation_key="state",
        icon="mdi:state-machine",
        value_fn=lambda v: CLASSIC_STATES.get(v, f"Unknown ({v})"),
        entity_registry_enabled_default=False,
    ),
    # -- Whizbang Jr additional --
    ClassicSolarSensorDescription(
        key="shunt_temperature",
        translation_key="shunt_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
    ),
    ClassicSolarSensorDescription(
        key="total_amp_hours",
        translation_key="total_amp_hours",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="Ah",
        icon="mdi:battery-outline",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarSensorDescription(
        key="positive_amp_hours",
        translation_key="positive_amp_hours",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="Ah",
        icon="mdi:battery-plus-outline",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarSensorDescription(
        key="negative_amp_hours",
        translation_key="negative_amp_hours",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="Ah",
        icon="mdi:battery-minus-outline",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarSensorDescription(
        key="net_amp_hours",
        translation_key="net_amp_hours",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="Ah",
        icon="mdi:battery-sync-outline",
        entity_registry_enabled_default=False,
    ),
    # -- Computed power sensors (require Whizbang Jr) --
    ClassicSolarSensorDescription(
        key="load_power",
        translation_key="load_power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
        icon="mdi:home-lightning-bolt",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarSensorDescription(
        key="battery_charge_power",
        translation_key="battery_charge_power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
        icon="mdi:battery-charging",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarSensorDescription(
        key="battery_discharge_power",
        translation_key="battery_discharge_power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
        icon="mdi:battery-arrow-down",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarSensorDescription(
        key="battery_power",
        translation_key="battery_power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
        icon="mdi:battery-sync",
        entity_registry_enabled_default=False,
    ),
    # -- Computed energy sensors (require Whizbang Jr) --
    ClassicSolarSensorDescription(
        key="battery_charge_energy",
        translation_key="battery_charge_energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        icon="mdi:battery-charging",
        entity_registry_enabled_default=False,
    ),
    ClassicSolarSensorDescription(
        key="battery_discharge_energy",
        translation_key="battery_discharge_energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        icon="mdi:battery-arrow-down",
        entity_registry_enabled_default=False,
    ),
    # -- Diagnostics --
    ClassicSolarSensorDescription(
        key="info_flags",
        translation_key="info_flags",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:flag-outline",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ClassicSolarCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ClassicSolarSensor(coordinator, desc) for desc in SENSOR_DESCRIPTIONS
    )


class ClassicSolarSensor(CoordinatorEntity[ClassicSolarCoordinator], SensorEntity):
    """Representation of a Classic Solar sensor."""

    entity_description: ClassicSolarSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ClassicSolarCoordinator,
        description: ClassicSolarSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id}_{description.translation_key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(self.entity_description.key)
        if raw is None:
            return None
        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(raw)
        return raw
