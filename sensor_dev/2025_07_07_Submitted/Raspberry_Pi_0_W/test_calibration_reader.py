#!/usr/bin/env python3
"""
Test script to diagnose calibration file reading issues and provide workaround
"""

import struct
import json
from datetime import datetime

def read_calibration_alternative(filename):
    """
    Alternative calibration reader that creates dummy calibration data
    This is a workaround until the javaobj issue is resolved
    """
    print("WARNING: Using alternative calibration reader with default values")
    print("This is a temporary workaround - actual calibration data is not being loaded")
    
    # Create dummy calibration data structure
    cal_data = {
        'version': 5,
        'analyserType': 20,
        'comment': 'Dummy calibration data',
        'startFrequency': type('obj', (object,), {'value': 1000000}),  # 1 MHz
        'stopFrequency': type('obj', (object,), {'value': 3000000000}),  # 3 GHz
        'numberOfSteps': type('obj', (object,), {'value': 1000}),
        'numberOfOverscans': type('obj', (object,), {'value': 1}),
        'scanMode': type('obj', (object,), {'mode': 'Reflection'}),
    }
    
    # Create dummy calibration blocks with temperature data
    for block_name in ['calibrationData4Load', 'calibrationData4Open', 'calibrationData4Short', 'calibrationData4Loop']:
        cal_block = type('CalibrationBlock', (object,), {
            'deviceTemperature': type('obj', (object,), {'value': 49.133}),
            'samples': [type('Sample', (object,), {
                'angle': 0.0,
                'loss': 0.0,
                'frequency': 1000000 + i * 1000
            }) for i in range(1000)]
        })
        cal_data[block_name] = cal_block()
    
    return cal_data

def examine_java_serialization_header(filename):
    """
    Examine the Java serialization file header
    """
    with open(filename, 'rb') as f:
        # Java serialization magic number
        magic = f.read(2)
        if magic == b'\xac\xed':
            print(f"Valid Java serialization file (magic: {magic.hex()})")
            
            # Version
            version = struct.unpack('>H', f.read(2))[0]
            print(f"Serialization version: {version}")
            
            # Read first few bytes to understand structure
            print("\nFirst 100 bytes (hex):")
            f.seek(0)
            data = f.read(100)
            hex_data = ' '.join([f'{b:02x}' for b in data])
            print(hex_data)
            
            # Try to find string patterns
            f.seek(0)
            content = f.read()
            print(f"\nFile size: {len(content)} bytes")
            
            # Look for readable strings
            import re
            strings = re.findall(b'[\x20-\x7e]{4,}', content)
            print("\nReadable strings found:")
            for s in strings[:20]:  # First 20 strings
                print(f"  {s.decode('ascii', errors='ignore')}")
        else:
            print(f"Not a valid Java serialization file (magic: {magic.hex()})")

if __name__ == "__main__":
    print("Calibration File Analysis")
    print("=" * 50)
    
    filename = "./REFL_miniVNATiny.cal"
    
    # Examine the file
    examine_java_serialization_header(filename)
    
    print("\n" + "=" * 50)
    print("Alternative calibration data structure:")
    cal_data = read_calibration_alternative(filename)
    
    # Test the structure
    print(f"\nVersion: {cal_data['version']}")
    print(f"Analyser Type: {cal_data['analyserType']}")
    print(f"Start Frequency: {cal_data['startFrequency'].value}")
    print(f"Stop Frequency: {cal_data['stopFrequency'].value}")
    print(f"Number of Steps: {cal_data['numberOfSteps'].value}")
    
    # Test temperature access
    print(f"\nOpen circuit temperature: {cal_data['calibrationData4Open'].deviceTemperature.value}")
    print(f"Short circuit temperature: {cal_data['calibrationData4Short'].deviceTemperature.value}")
    print(f"Load temperature: {cal_data['calibrationData4Load'].deviceTemperature.value}")