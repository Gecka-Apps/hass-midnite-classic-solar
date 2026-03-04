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

"""DataUpdateCoordinator for the Midnite Classic Solar integration."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import timedelta

from pymodbus.client import AsyncModbusTcpClient

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.storage import Store

from .const import (
    ADDR_MAX_INPUT_CURRENT,
    ADDR_WRITE,
    BLOCK_BATTERY_PARAMS_ADDR,
    BLOCK_BATTERY_PARAMS_COUNT,
    BLOCK_CHARGE_SETTINGS_ADDR,
    BLOCK_CHARGE_SETTINGS_COUNT,
    BLOCK_FIRMWARE_ADDR,
    BLOCK_FIRMWARE_COUNT,
    BLOCK_MAIN_ADDR,
    BLOCK_MAIN_COUNT,
    BLOCK_NAME_ADDR,
    BLOCK_NAME_COUNT,
    BLOCK_WHIZBANG_ADDR,
    BLOCK_WHIZBANG_COUNT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DEVICE_TYPES,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

ENERGY_SAVE_INTERVAL = 60  # save every ~5 min at 5s polling


class ClassicSolarCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator that polls the Midnite Classic via Modbus TCP."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: AsyncModbusTcpClient,
        unit_id: int,
        device_type: int,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        self._unit_id = unit_id
        self._device_type = device_type
        self._modbus_lock = asyncio.Lock()
        self._last_update: float | None = None
        self._battery_charge_energy: float = 0.0
        self._battery_discharge_energy: float = 0.0
        self._store = Store(hass, 1, f"{DOMAIN}_{unit_id}_energy")
        self._energy_save_counter = 0

    @property
    def unique_id(self) -> str:
        return str(self._unit_id)

    @property
    def device_info(self) -> DeviceInfo:
        model = DEVICE_TYPES.get(self._device_type, f"Classic {self._device_type}")
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=f"Midnite {model}",
            manufacturer="Midnite Solar",
            model=model,
        )

    # ------------------------------------------------------------------
    # Energy persistence
    # ------------------------------------------------------------------

    async def async_load_energy(self) -> None:
        """Restore persisted energy counters from disk."""
        data = await self._store.async_load()
        if data:
            self._battery_charge_energy = data.get("charge", 0.0)
            self._battery_discharge_energy = data.get("discharge", 0.0)

    async def async_save_energy(self) -> None:
        """Persist energy counters to disk."""
        await self._store.async_save({
            "charge": self._battery_charge_energy,
            "discharge": self._battery_discharge_energy,
        })

    # ------------------------------------------------------------------
    # Register decode helpers (no dependency on pymodbus internals)
    # ------------------------------------------------------------------

    @staticmethod
    def _msb(reg: int) -> int:
        """Extract most significant byte from a 16-bit register."""
        return (reg >> 8) & 0xFF

    @staticmethod
    def _lsb(reg: int) -> int:
        """Extract least significant byte from a 16-bit register."""
        return reg & 0xFF

    @staticmethod
    def _int16(reg: int) -> int:
        """Interpret unsigned 16-bit register value as signed int16."""
        return reg - 0x10000 if reg >= 0x8000 else reg

    @staticmethod
    def _uint32_le(regs: list[int], idx: int) -> int:
        """Combine two registers into unsigned 32-bit (Little Endian word order)."""
        return (regs[idx + 1] << 16) | regs[idx]

    @staticmethod
    def _int32_le(regs: list[int], idx: int) -> int:
        """Combine two registers into signed 32-bit (Little Endian word order)."""
        val = (regs[idx + 1] << 16) | regs[idx]
        return val - 0x100000000 if val >= 0x80000000 else val

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    async def _read_block(self, address: int, count: int) -> list[int]:
        """Read a contiguous block of holding registers."""
        result = await self.client.read_holding_registers(
            address, count=count, device_id=DEFAULT_SLAVE_ID
        )
        if result.isError():
            raise UpdateFailed(
                f"Modbus error reading {count} registers at address {address}"
            )
        return result.registers

    async def _async_update_data(self) -> dict:
        """Fetch all data from the Classic."""
        async with self._modbus_lock:
            try:
                data: dict = {}
                await self._decode_main(data)
                await self._decode_charge_settings(data)
                await self._decode_name(data)
                await self._decode_battery_params(data)
                await self._decode_whizbang(data)
                await self._decode_firmware(data)
                await self._decode_max_input_current(data)
            except UpdateFailed:
                raise
            except Exception as exc:
                raise UpdateFailed(
                    f"Error communicating with Classic: {exc}"
                ) from exc

        # Derived values (no I/O, computed outside the lock)
        data["has_whizbang"] = (
            (data.get("aux1and2_function", 0) & 0x3F00) >> 8 == 18
        )
        data["aux1"] = (data.get("info_flags", 0) & 0x00004000) != 0
        data["aux2"] = (data.get("info_flags", 0) & 0x00008000) != 0

        # Computed WhizBang power sensors (for Energy dashboard)
        if data["has_whizbang"]:
            wb_current = data.get("wb_bat_current", 0)
            bat_v = data.get("bat_voltage", 0)
            classic_current = data.get("bat_current", 0)
            data["load_power"] = round(
                (classic_current - wb_current) * bat_v, 1
            )
            data["battery_charge_power"] = round(
                max(0, wb_current) * bat_v, 1
            )
            data["battery_discharge_power"] = round(
                max(0, -wb_current) * bat_v, 1
            )
            # Signed power: positive = discharge, negative = charge (HA convention)
            data["battery_power"] = round(-wb_current * bat_v, 1)

            # Riemann sum integration for energy (kWh)
            now = time.monotonic()
            if self._last_update is not None:
                dt_hours = (now - self._last_update) / 3600.0
                max_dt = self.update_interval.total_seconds() * 3 / 3600.0
                if dt_hours < max_dt:
                    self._battery_charge_energy += (
                        data["battery_charge_power"] * dt_hours / 1000.0
                    )
                    self._battery_discharge_energy += (
                        data["battery_discharge_power"] * dt_hours / 1000.0
                    )
            self._last_update = now
            data["battery_charge_energy"] = round(
                self._battery_charge_energy, 4
            )
            data["battery_discharge_energy"] = round(
                self._battery_discharge_energy, 4
            )

            self._energy_save_counter += 1
            if self._energy_save_counter >= ENERGY_SAVE_INTERVAL:
                self._energy_save_counter = 0
                await self.async_save_energy()

        return data

    # -- Main block (addr 4100, 44 regs -> registers 4101-4144) -----------

    async def _decode_main(self, data: dict) -> None:
        regs = await self._read_block(BLOCK_MAIN_ADDR, BLOCK_MAIN_COUNT)

        data["pcb_revision"] = self._msb(regs[0])              # reg 4101 MSB
        data["device_type"] = self._lsb(regs[0])               # reg 4101 LSB
        data["build_year"] = regs[1]                            # reg 4102
        data["build_month"] = self._msb(regs[2])               # reg 4103 MSB
        data["build_day"] = self._lsb(regs[2])                 # reg 4103 LSB
        data["info_flag_bits_3"] = regs[3]                      # reg 4104
        # regs[4] = reg 4105 reserved
        data["mac_1"] = self._msb(regs[5])                     # reg 4106 MSB
        data["mac_0"] = self._lsb(regs[5])                     # reg 4106 LSB
        data["mac_3"] = self._msb(regs[6])                     # reg 4107 MSB
        data["mac_2"] = self._lsb(regs[6])                     # reg 4107 LSB
        data["mac_5"] = self._msb(regs[7])                     # reg 4108 MSB
        data["mac_4"] = self._lsb(regs[7])                     # reg 4108 LSB
        # regs[8-9] = regs 4109-4110 reserved
        data["unit_id"] = self._int32_le(regs, 10)             # regs 4111-4112
        data["status_roll"] = regs[12]                          # reg 4113
        data["restart_timer_ms"] = regs[13]                     # reg 4114
        data["bat_voltage"] = self._int16(regs[14]) / 10.0     # reg 4115
        data["pv_voltage"] = regs[15] / 10.0                   # reg 4116
        data["bat_current"] = regs[16] / 10.0                  # reg 4117
        data["energy_today"] = regs[17] / 10.0                 # reg 4118
        data["power"] = regs[18]                                # reg 4119
        data["charge_stage"] = self._msb(regs[19])             # reg 4120 MSB
        data["state"] = self._lsb(regs[19])                    # reg 4120 LSB
        data["pv_current"] = regs[20] / 10.0                   # reg 4121
        data["last_voc"] = regs[21] / 10.0                     # reg 4122
        data["highest_vin_log"] = regs[22]                      # reg 4123
        data["match_point_shadow"] = regs[23]                   # reg 4124
        data["amp_hours_today"] = regs[24]                      # reg 4125
        data["lifetime_energy"] = self._uint32_le(regs, 25) / 10.0  # regs 4126-4127
        data["lifetime_amp_hours"] = self._uint32_le(regs, 27)      # regs 4128-4129
        data["info_flags"] = self._int32_le(regs, 29)          # regs 4130-4131
        data["bat_temperature"] = self._int16(regs[31]) / 10.0  # reg 4132
        data["fet_temperature"] = self._int16(regs[32]) / 10.0  # reg 4133
        data["pcb_temperature"] = self._int16(regs[33]) / 10.0  # reg 4134
        # regs[34-36] = regs 4135-4137
        data["float_time_today"] = regs[37]                     # reg 4138
        data["absorb_time"] = regs[38]                          # reg 4139
        # regs[39-40] = regs 4140-4141
        data["reason_for_reset"] = regs[41]                     # reg 4142
        data["equalize_time"] = regs[42]                        # reg 4143

    # -- Charge settings block (addr 4147, 18 regs -> registers 4148-4165) -

    async def _decode_charge_settings(self, data: dict) -> None:
        regs = await self._read_block(
            BLOCK_CHARGE_SETTINGS_ADDR, BLOCK_CHARGE_SETTINGS_COUNT
        )

        data["bat_current_limit"] = regs[0] / 10.0             # reg 4148
        data["absorb_voltage"] = regs[1] / 10.0                # reg 4149
        data["float_voltage"] = regs[2] / 10.0                 # reg 4150
        data["equalize_voltage"] = regs[3] / 10.0              # reg 4151
        # regs[4] = reg 4152 (sliding limit)
        data["min_absorb_time"] = regs[5]                       # reg 4153
        data["absorb_time_setting"] = regs[6]                   # reg 4154
        data["max_temp_comp_voltage"] = regs[7] / 10.0          # reg 4155
        data["min_temp_comp_voltage"] = regs[8] / 10.0          # reg 4156
        data["temp_comp_value"] = regs[9] / 10.0                # reg 4157
        # regs[10-11] = regs 4158-4159
        # regs[12-13] = regs 4160-4161 (Force Flag Bits, 32-bit)
        # regs[12-13] are Force Flag Bits (reg 4160-4161) — write-only per spec
        data["equalize_time_setting"] = regs[14]                # reg 4162
        data["equalize_interval_days"] = regs[15]               # reg 4163
        data["mppt_mode"] = regs[16]                            # reg 4164
        data["aux1and2_function"] = self._int16(regs[17])       # reg 4165

    # -- Device name (addr 4209, 4 regs -> registers 4210-4213) -----------

    async def _decode_name(self, data: dict) -> None:
        regs = await self._read_block(BLOCK_NAME_ADDR, BLOCK_NAME_COUNT)

        name_bytes: list[int] = []
        for reg in regs:
            name_bytes.extend([self._lsb(reg), self._msb(reg)])
        data["device_name"] = "".join(
            chr(b) for b in name_bytes if b != 0
        ).strip()

    # -- Battery params (addr 4243, 32 regs -> registers 4244-4275) -------

    async def _decode_battery_params(self, data: dict) -> None:
        regs = await self._read_block(
            BLOCK_BATTERY_PARAMS_ADDR, BLOCK_BATTERY_PARAMS_COUNT
        )

        data["vbatt_reg_setpoint_temp_comp"] = self._int16(regs[0]) / 10.0  # reg 4244
        data["nominal_battery_voltage"] = regs[1]               # reg 4245
        data["ending_amps"] = self._int16(regs[2]) / 10.0       # reg 4246
        # regs[3-4] = regs 4247-4248
        data["rebulk_volts"] = self._int16(regs[5]) / 10.0    # reg 4249
        # regs[6-30] = regs 4250-4274
        data["reason_for_resting"] = regs[31]                   # reg 4275

    # -- Whizbang Jr (addr 4360, 22 regs -> registers 4361-4382) ----------

    async def _decode_whizbang(self, data: dict) -> None:
        regs = await self._read_block(BLOCK_WHIZBANG_ADDR, BLOCK_WHIZBANG_COUNT)

        # regs[0-3] = regs 4361-4364 (skipped)
        data["positive_amp_hours"] = self._uint32_le(regs, 4)   # regs 4365-4366
        data["negative_amp_hours"] = self._int32_le(regs, 6)    # regs 4367-4368
        data["net_amp_hours"] = self._int32_le(regs, 8)          # regs 4369-4370
        data["wb_bat_current"] = self._int16(regs[10]) / 10.0   # reg 4371
        # reg 4372: MSB = CRC (ignored), LSB = temperature (unsigned - 50)
        data["shunt_temperature"] = self._lsb(regs[11]) - 50.0  # reg 4372 LSB
        data["soc"] = regs[12]                                   # reg 4373
        # regs[13-15] = regs 4374-4376
        data["remaining_amp_hours"] = regs[16]                   # reg 4377
        # regs[17-19] = regs 4378-4380
        data["total_amp_hours"] = regs[20]                       # reg 4381

    # -- Firmware versions (addr 16386, 4 regs -> registers 16387-16390) --

    async def _decode_firmware(self, data: dict) -> None:
        regs = await self._read_block(BLOCK_FIRMWARE_ADDR, BLOCK_FIRMWARE_COUNT)

        data["app_revision"] = self._uint32_le(regs, 0)        # regs 16387-16388
        data["net_revision"] = self._uint32_le(regs, 2)        # regs 16389-16390

    # -- Max input current (single register at addr 4198 -> register 4199) -

    async def _decode_max_input_current(self, data: dict) -> None:
        regs = await self._read_block(ADDR_MAX_INPUT_CURRENT, 1)
        data["max_input_current"] = regs[0] / 10.0

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------

    async def async_write_register(self, address: int, value: int) -> None:
        """Write a single register via Modbus TCP."""
        async with self._modbus_lock:
            result = await self.client.write_register(
                address, value, device_id=DEFAULT_SLAVE_ID
            )
            if result.isError():
                raise HomeAssistantError(
                    f"Failed to write value {value} to register at address {address}"
                )

        # Refresh data after successful write
        await self.async_request_refresh()
