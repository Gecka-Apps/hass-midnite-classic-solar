# Midnite Classic Solar

[![Release](https://img.shields.io/github/v/release/Gecka-Apps/hass-midnite-classic-solar)](https://github.com/Gecka-Apps/hass-midnite-classic-solar/releases)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![HA: 2024.1+](https://img.shields.io/badge/HA-2024.1%2B-41BDF5)](https://www.home-assistant.io/)

Home Assistant integration for Midnite Classic 150/200/250 solar charge controllers via Modbus TCP.

## Features

- **Real-time monitoring** — battery voltage, PV voltage, currents, power, temperatures, charge stage
- **Energy tracking** — daily kWh, daily Ah, lifetime energy
- **Charge settings** — absorb/float/equalize voltages, current limits, timing parameters
- **MPPT control** — select MPPT mode (Solar, Dynamic, Wind Track, etc.)
- **Force charge** — force bulk, float, or equalize stage
- **WhizBang Jr support** — SOC, net/positive/negative Ah, load power, battery charge/discharge power and energy
- **Diagnostics** — FET/PCB/shunt temperatures, charge stage codes, resting reasons, info flags
- **Action buttons** — reset faults, force MPPT sweep, reset WhizBang Jr SOC to 100%
- **Reconfigure flow** — change host, port, or polling interval without removing the device
- **Translations** — English, French

## Entities

- **sensor** — battery voltage, PV voltage, battery current, PV current, power, last VOC, energy today, amp hours today, lifetime energy, charge stage, reason for resting, temperatures (battery, FET, PCB, shunt), float time today, absorb time, WhizBang battery current, SOC, remaining/total/positive/negative/net amp hours, load power, battery charge/discharge power/energy, classic state, info flags
- **number** — absorb voltage, float voltage, equalize voltage, absorb/equalize time, equalize interval, battery current limit, max input current, ending amps, re-bulk voltage, nominal battery voltage, min absorb time, temp comp voltage min/max, temp comp value
- **select** — MPPT mode, force charge stage
- **button** — reset faults, force MPPT sweep, reset SOC to 100%

## Requirements

- Home Assistant 2024.1 or later
- Midnite Classic 150, 200, 250 or 250 KS with Modbus TCP enabled
- Network access to the Classic (default port 502)

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations** > **Custom repositories**
3. Add `https://github.com/Gecka-Apps/hass-midnite-classic-solar` as an **Integration**
4. Install **Midnite Classic Solar**
5. Restart Home Assistant

### Manual

1. Copy `custom_components/classic_solar/` into your Home Assistant `custom_components/` directory
2. Restart Home Assistant

### Configuration

1. Go to **Settings** > **Devices & services** > **Add integration**
2. Search for **Midnite Classic Solar**
3. Enter the host IP, port (default 502), and polling interval (default 5s)

> **Note:** The Classic accepts only one Modbus TCP connection at a time. Close any other Modbus client (Local app, other HA instance) before adding the integration.

## License

[GNU Affero General Public License v3.0](LICENSE)

## Authors

**Laurent Dinclaux** <laurent@gecka.nc> — [Gecka](https://gecka.nc)

---
Built with 🥥 and ☕ by [Gecka](https://gecka.nc) — Kanaky-New Caledonia 🇳🇨
