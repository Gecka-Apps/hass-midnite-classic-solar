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

"""Constants for the Midnite Classic Solar integration."""

DOMAIN = "classic_solar"
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 10
DEFAULT_SCAN_INTERVAL = 5  # seconds
MIN_SCAN_INTERVAL = 3
MAX_SCAN_INTERVAL = 30

CONF_SCAN_INTERVAL = "scan_interval"

# ---------------------------------------------------------------------------
# Modbus block addresses (pymodbus 0-based addresses; register = address + 1)
# ---------------------------------------------------------------------------
BLOCK_MAIN_ADDR = 4100
BLOCK_MAIN_COUNT = 44  # registers 4101-4144

BLOCK_CHARGE_SETTINGS_ADDR = 4147
BLOCK_CHARGE_SETTINGS_COUNT = 18  # registers 4148-4165

BLOCK_NAME_ADDR = 4209
BLOCK_NAME_COUNT = 4  # registers 4210-4213

BLOCK_BATTERY_PARAMS_ADDR = 4243
BLOCK_BATTERY_PARAMS_COUNT = 32  # registers 4244-4275

BLOCK_WHIZBANG_ADDR = 4360
BLOCK_WHIZBANG_COUNT = 22  # registers 4361-4382

BLOCK_FIRMWARE_ADDR = 16386
BLOCK_FIRMWARE_COUNT = 4  # registers 16387-16390

# Single register for MaxInputCurrent (register 4199)
ADDR_MAX_INPUT_CURRENT = 4198

# ---------------------------------------------------------------------------
# Force Flag Bits: write-only trigger register 4160 (low word) / 4161 (high word)
# ---------------------------------------------------------------------------
ADDR_FORCE_FLAGS_LOW = 4159   # register 4160
ADDR_FORCE_FLAGS_HIGH = 4160  # register 4161

# ForceEEpromUpdateWriteF: saves every EEPROM-backed register to internal EEPROM
FORCE_EEPROM_UPDATE = 0x0004

# ---------------------------------------------------------------------------
# Writable register addresses (used with write_register)
# ---------------------------------------------------------------------------
ADDR_WRITE = {
    "bat_current_limit": 4147,       # reg 4148 - Battery output Current Limit
    "absorb_voltage": 4148,          # reg 4149 - Absorb Set Point Voltage
    "float_voltage": 4149,           # reg 4150 - Float Voltage Set Point
    "equalize_voltage": 4150,        # reg 4151 - Equalize Voltage Set Point
    "absorb_time_setting": 4153,     # reg 4154 - Absorb Time
    "equalize_time_setting": 4161,   # reg 4162 - Equalize Time
    "equalize_interval_days": 4162,  # reg 4163 - Equalize Interval Days
    "mppt_mode": 4163,               # reg 4164 - MPPT Mode
    "max_input_current": 4198,       # reg 4199 - MaxInputCurrent
    "ending_amps": 4245,             # reg 4246 - Ending Amps
    "rebulk_volts": 4248,            # reg 4249 - Re-bulk Voltage
    "nominal_battery_voltage": 4244, # reg 4245 - Nominal Battery Voltage
    "min_absorb_time": 4152,         # reg 4153 - Minimum Absorb Time
    "max_temp_comp_voltage": 4154,   # reg 4155 - Max Temp Comp Voltage
    "min_temp_comp_voltage": 4155,   # reg 4156 - Min Temp Comp Voltage
    "temp_comp_value": 4156,         # reg 4157 - Temp Comp Value
    "force_charge_stage": 4159,      # reg 4160 - Force Charge Stage
}

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
CHARGE_STAGES = {
    0: "Resting",
    3: "Absorb",
    4: "Bulk MPPT",
    5: "Float",
    6: "Float MPPT",
    7: "Equalize",
    10: "HyperVOC",
    18: "Equalize MPPT",
}

MPPT_MODES = {
    0x0001: "PV Uset",
    0x0003: "Dynamic",
    0x0005: "Wind Track",
    0x0009: "Legacy P&O",
    0x000B: "Solar",
    0x000D: "Hydro",
}
MPPT_MODES_REVERSE = {v: k for k, v in MPPT_MODES.items()}

FORCE_CHARGE_STAGES = {
    0x00: "Normal",
    0x40: "Force Bulk",
    0x20: "Force Float",
    0x80: "Force Equalize",
}
FORCE_CHARGE_STAGES_REVERSE = {v: k for k, v in FORCE_CHARGE_STAGES.items()}

CLASSIC_STATES = {
    0: "Resting",
    1: "Waking",
    2: "Waking",
    3: "Active",
    4: "Active",
    6: "Active",
}

REASONS_FOR_RESTING = {
    1: "Anti-Click",
    2: "Insane Ibatt",
    3: "Negative Current",
    4: "PV Below Battery V",
    5: "Low Power",
    6: "FET Temperature",
    7: "Ground Fault",
    8: "Arc Fault",
    9: "Backfeed",
    10: "Battery Below 8V",
    11: "PV Rising Slow",
    12: "Voc Drop",
    13: "Voc Rise",
    14: "PV Rising Slow",
    15: "Voc Drop",
    16: "MPPT Off",
    17: "PV Over Voltage 150",
    18: "PV Over Voltage 200",
    19: "PV Over Voltage 250",
    22: "Avg Battery V High",
    25: "Battery Overshoot",
    26: "Mode Changed",
    27: "Bridge Center Fault",
    28: "Relay Not Engaged",
    29: "Wind Graph Illegal",
    30: "Peak Amps Over Limit",
    31: "Peak Neg Current 250",
    32: "Aux2 Commanded Off",
    33: "OCP Non-Solar",
    34: "Peak Neg Current 150/200",
    35: "Low Battery Disconnect",
}

DEVICE_TYPES = {
    150: "Classic 150",
    200: "Classic 200",
    250: "Classic 250",
    251: "Classic 250 KS",
}
