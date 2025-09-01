# miniVNA Tiny Calibration Script - Project State

## Overview
This project implements a Python interface for the miniVNA Tiny vector network analyzer, including calibration support and Bluetooth data transmission to a host PC.

## Current State (as of 2025-07-09)

### Working Features
- ✅ Serial communication with miniVNA Tiny device
- ✅ Temperature and device status reading
- ✅ VNA frequency sweep measurements (1-100 MHz range)
- ✅ Data processing and calibration calculations
- ✅ JSON data export
- ✅ Bluetooth data transmission with error handling
- ✅ Matplotlib plotting (on Windows systems)

### Recent Fixes Applied

1. **javaobj Compatibility Issue**
   - Problem: Original javaobj 0.1.0 had Python 2/3 compatibility issues
   - Solution: Installed javaobj-py3 (v0.4.4) for better Python 3 support
   - Status: Calibration file reading still falls back to default values due to complex Java serialization format

2. **Data Accumulation Bug**
   - Problem: `self.data_samples` was not cleared between measurements, causing same data regardless of antenna connection
   - Solution: Added `self.data_samples = []` at start of `receive_byte_stream()` method
   - Status: Fixed - each measurement now produces fresh data

3. **Division by Zero Errors**
   - Fixed in SWR calculation when mag = 1.0
   - Fixed in e11 calculation with near-zero denominators
   - Added proper error handling with sensible defaults

4. **Bluetooth Connection Error Handling**
   - Added try-except block with timeout for Bluetooth connections
   - Provides informative messages when host is unavailable
   - Data is still saved locally even if Bluetooth fails

### Known Issues

1. **Calibration File Reading**
   - The Java serialization format in REFL_miniVNATiny.cal is not fully compatible with javaobj-py3
   - Currently using default/dummy calibration values
   - Impact: Measurements are real but calibration correction is approximate

2. **Hardcoded Frequency Range**
   - Lines 996-997 override the requested frequency range to 1-100 MHz
   - This should be removed or made configurable

### Configuration

#### Serial Port
- Port: `/dev/ttyUSB0`
- Baud rate: 921600
- Timeout: 1 second

#### Bluetooth
- Current MAC: `FC:01:7C:92:05:6C` (JOEY PC)
- Port: 4
- Protocol: RFCOMM

#### VNA Settings
- DDS_TICKS_PER_MHZ: 10000000
- Prescaler: 10
- Scan mode: Reflection (command "7")

### Dependencies
- Python 3.9+
- pyserial
- matplotlib
- javaobj-py3
- numpy
- socket (for Bluetooth)

### Usage
```bash
python miniVNA_Tiny_Calibration_R_Pi_0.py
```

### Data Output
The script generates:
1. `vna_data_YYYY-MM-DD_HH-MM-SS.json` - Contains frequencies, reflection loss (RL), and reflection phase (RLPHASE)
2. `REFL_miniVNATiny.png` - Plot of measurements (Windows only)
3. Optional: `debug_output_YYYY-MM-DD_HH-MM-SS.json` - Debug information (currently disabled)

### Future Improvements
1. Implement proper calibration file parser or convert .cal files to a more accessible format
2. Make frequency range configurable via command line arguments
3. Add support for transmission measurements
4. Implement real-time plotting on all platforms
5. Add configuration file for Bluetooth settings
6. Create a more robust calibration data structure

### Testing Notes
To verify the script is measuring real data:
1. Run with antenna connected - note the RL/phase values
2. Disconnect antenna and run again - values should change significantly
3. An open circuit typically shows high reflection loss
4. A matched load (50Ω) shows low reflection loss

### Troubleshooting
- If Bluetooth fails: Check that the server is running on the host PC
- If calibration fails: The script will use default values and continue
- If serial communication fails: Check USB connection and permissions (`sudo chmod 666 /dev/ttyUSB0`)