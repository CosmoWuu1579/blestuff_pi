# Longhorn Life Sciences - VNA Telemetry System

A Python-based telemetry system that performs calibrated frequency sweep measurements using a **miniVNA Tiny** vector network analyzer connected to a **Raspberry Pi Zero W**, and transmits results over Bluetooth.

---

## System Architecture

```
┌──────────────────┐         Bluetooth (RFCOMM)        ┌──────────────────┐
│   Mobile App /   │◄────────────────────────────────►  │  Raspberry Pi 0W │
│   Host Client    │   Port 4, bidirectional JSON/bin   │                  │
└──────────────────┘                                    │  BLE_R_Pi_0_App  │
                                                        │  miniVNAcontroller│
                                                        └────────┬─────────┘
                                                                 │ USB Serial
                                                                 │ 921600 baud
                                                        ┌────────▼─────────┐
                                                        │  miniVNA Tiny    │
                                                        │  (VNA Hardware)  │
                                                        └──────────────────┘
```

**The mobile app replaces the current PC host client** (`src/PC_scripts/BLE_PC_App.py`). The RPi acts as the Bluetooth client that connects to the host. The mobile app must act as a **Bluetooth RFCOMM server** on port 4.

---

## Bluetooth Integration Guide (Mobile App)

This is the primary integration surface for the mobile app.

### Protocol

- **Transport:** Bluetooth Classic RFCOMM (not BLE/GATT)
- **Port:** 4
- **Roles:** The RPi **initiates** the connection to the mobile device's MAC address. The mobile app must be listening as a server.
- **Current hardcoded MAC:** `FC:01:7C:92:05:6C` (must be updated to the mobile device's MAC in `miniVNAcontroller.py` and `BLE_R_Pi_0_App.py`)

### Communication Flow

#### 1. Mobile App sends a scan command (JSON)

```json
{
    "cmd": "scan",
    "start_freq": 1000000.0,
    "stop_freq": 1000000000.0,
    "num_steps": 202
}
```

| Field        | Type  | Description                              | Typical Range          |
|------------- |-------|------------------------------------------|------------------------|
| `cmd`        | str   | Command type. Currently only `"scan"`    | `"scan"`               |
| `start_freq` | float | Start frequency in Hz                    | 1,000,000 (1 MHz)     |
| `stop_freq`  | float | Stop frequency in Hz                     | 1,000,000,000 (1 GHz) |
| `num_steps`  | int   | Number of frequency points in the sweep  | 50 - 500 (202 typical) |

#### 2. RPi performs the measurement and returns data (JSON)

```json
{
    "frequencies": [1000000.0, 6020100.0, ..., 999999900.0],
    "RL": [0.0, -0.003, ..., -0.651],
    "RLPHASE": [148.95, 159.43, ..., 63.22]
}
```

| Field         | Type         | Unit    | Description                                                        |
|-------------- |--------------|---------|--------------------------------------------------------------------|
| `frequencies` | float[]      | Hz      | Linear sweep of frequency points from `start_freq` to `stop_freq` |
| `RL`          | float[]      | dB      | Return Loss. `20*log10(|Gamma|)`. Values are <= 0; more negative = better match. |
| `RLPHASE`     | float[]      | degrees | Reflection phase angle. Range: [-180, 180].                        |

All three arrays have the same length (equal to `num_steps`), and indices correspond to the same frequency point.

#### 3. Data transfer details

- The RPi streams the JSON file to the connected client in **1024-byte chunks**.
- End of transmission is signaled by the RPi closing the socket.
- If Bluetooth is unavailable, the RPi saves data locally to `/home/pi/vna_data_YYYY-MM-DD_HH-MM-SS.json`.

---

## Interpreting the Measurement Data

The system measures the **S11 reflection coefficient** of an antenna or RF device.

| Metric       | What It Means                                                                                      |
|------------- |----------------------------------------------------------------------------------------------------|
| **RL (dB)**  | How much signal is reflected back. 0 dB = total reflection (bad). -10 dB = good. -20 dB = excellent match. |
| **RLPHASE**  | Phase angle of the reflected signal. Used for impedance calculations.                              |

**Derived values** the mobile app can compute from RL and RLPHASE:

```
|Gamma| = 10^(RL / 20)                            # Reflection coefficient magnitude
SWR     = (1 + |Gamma|) / (1 - |Gamma|)           # Standing Wave Ratio (1.0 = perfect)
Z       = 50 * (1 + Gamma) / (1 - Gamma)          # Complex impedance (Ohms)
  where Gamma = |Gamma| * e^(j * RLPHASE * pi/180)
```

---

## Repository Structure

```
telemetry/
├── miniVNAcontroller.py                          # Main orchestrator (start here)
├── README.md
├── src/
│   ├── Raspberry_Pi_0_W_scripts/
│   │   ├── miniVNA_Tiny_Calibration_R_Pi_0.py    # Core VNA driver (1884 lines)
│   │   ├── BLE_R_Pi_0_App.py                     # RPi Bluetooth client
│   │   ├── REFL_miniVNATiny.cal                  # Calibration file (Java serialized)
│   │   ├── test_calibration_reader.py            # Calibration diagnostics
│   │   └── test_javaobj.py                       # Java deserialization test
│   ├── PC_scripts/
│   │   └── BLE_PC_App.py                         # PC Bluetooth server (reference for mobile app)
│   ├── 5000_1ovrscn/
│   │   └── REFL_miniVNATiny.cal                  # 5000-point calibration (1 overscan)
│   └── 7000_3ovrscn/
│       └── REFL_miniVNATiny.cal                  # 7000-point calibration (3 overscans, recommended)
├── data/                                         # Sample measurement outputs
│   ├── vna_data_2025-09-02_15-36-47.json
│   └── received_data_2025-09-02_15-36-04.json
├── examples/
│   └── test_run.py
└── ARCHIVE/                                      # Previous versions and venv
```

### Key Files

| File | Purpose |
|------|---------|
| `miniVNAcontroller.py` | High-level API: `sweep_and_send()`, `sweep_to_json()`, `send_json()` |
| `src/.../miniVNA_Tiny_Calibration_R_Pi_0.py` | Low-level VNA control: serial communication, calibration math, frequency sweep |
| `src/PC_scripts/BLE_PC_App.py` | **Reference implementation** for the Bluetooth server the mobile app needs to replicate |
| `src/.../BLE_R_Pi_0_App.py` | RPi-side Bluetooth client that connects and sends data |

---

## MiniVNAController API

The `miniVNAcontroller.py` orchestrator exposes these methods:

```python
controller = MiniVNAController(
    bt_mac="FC:01:7C:92:05:6C",                   # Target device MAC
    bt_port=4,                                      # RFCOMM port
    calibration_file="./REFL_miniVNATiny.cal",      # Path to .cal file
    serial_port="/dev/ttyUSB0",                     # VNA serial port
    baud_rate=921600                                 # Serial baud rate
)

controller.load_calibration()                       # Load .cal file
controller.sweep_to_json(start, stop, steps, path)  # Run sweep, save JSON
controller.send_json(json_path)                      # Send JSON over Bluetooth
controller.sweep_and_send(start, stop, steps)        # Combined workflow
```

---

## RPi Setup & Dependencies

### Python Requirements

```
pyserial
matplotlib
numpy
javaobj-py3>=0.4.4
```

### System Requirements

- Python 3.9+
- Bluetooth Classic support (BlueZ on Linux)
- USB serial driver for miniVNA Tiny
- Serial port permissions: `sudo chmod 666 /dev/ttyUSB0`

### Running on the RPi

```bash
# From the telemetry/ directory
python miniVNAcontroller.py
```

---

## Reference: PC Bluetooth Server (src/PC_scripts/BLE_PC_App.py)

This is the existing host implementation that the mobile app replaces. Key behavior to replicate:

1. **Listen** on RFCOMM port 4
2. **Accept** incoming connection from RPi
3. **Send** a scan command JSON (see format above)
4. **Receive** measurement data in 1024-byte chunks until the connection closes
5. **Parse** the received bytes as UTF-8 JSON
6. **Display/store** the results

---

## Known Issues & Limitations

| Issue | Impact | Notes |
|-------|--------|-------|
| Calibration file parsing | Calibration falls back to default values | `.cal` files use Java serialization; `javaobj-py3` can't fully parse them. Measurements are real but correction is approximate. |
| Hardcoded Bluetooth MAC | Must manually update for each new host device | Change in `miniVNAcontroller.py` and `BLE_R_Pi_0_App.py` |
| Hardcoded frequency overrides | Sweep range may be overridden to 1-1000 MHz internally | Check lines ~996-997 in `miniVNA_Tiny_Calibration_R_Pi_0.py` |
| Plotting is Windows-only | `matplotlib` rendering gated on `platform == "Windows"` | Not relevant for mobile, but note if debugging on RPi |

---

## Sample Data

See `data/vna_data_2025-09-02_15-36-47.json` for a complete 202-point measurement example. This file can be used for mobile app development and testing without needing the physical hardware.
