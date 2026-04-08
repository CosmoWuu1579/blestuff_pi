"""
Raspberry Pi BLE GATT server — sends JSON data to the BLE Scanner app.
Run with:  sudo python3 ble_server.py
"""


# First run
# sudo apt update
# sudo apt install -y python3-pip bluetooth bluez libglib2.0-dev
# sudo pip3 install bless

# Then run
# sudo systemctl enable bluetooth
# sudo systemctl start bluetooth
# sudo hciconfig hci0 up       # brings the BT adapter up
# hciconfig                    # should show hci0 with BD Addres

# Run code via sudo python3 ble_server.py
import asyncio
import json
import logging
import os
import sys
import threading
from typing import Any, Dict, Optional, Union

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "src", "Raspberry_Pi_0_W_scripts"))
try:
    from BLE_R_Pi_0_App import send_file
except Exception as e:
    logging.warning(f"Could not import send_file: {e}")
    def send_file(_): pass

from bless import (
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)

# ── Must match App.tsx exactly ────────────────────────────────────────────────
SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
CHAR_UUID    = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

# ── How often to send data (seconds) ─────────────────────────────────────────
SEND_INTERVAL = 2.0

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Triggered when the phone reads or writes the characteristic ───────────────
def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    return characteristic.value

def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
    characteristic.value = value


FILENAME = "data/vna_data_2025-09-02_15-36-47.json"

def collect_data() -> dict:
    send_file(FILENAME)
    with open(FILENAME, "rb") as f:
        return json.loads(f.read())


async def run():
    # ── Create the GATT server ────────────────────────────────────────────────
    trigger = threading.Event()
    server = BlessServer(name="RaspberryPi", loop=asyncio.get_event_loop())
    server.read_request_func  = read_request
    server.write_request_func = write_request

    # Register the NUS service
    await server.add_new_service(SERVICE_UUID)

    # Register the notify characteristic inside that service
    char_flags = (
        GATTCharacteristicProperties.read   |
        GATTCharacteristicProperties.notify
    )
    permissions = GATTAttributePermissions.readable
    await server.add_new_characteristic(
        SERVICE_UUID, CHAR_UUID, char_flags, None, permissions
    )

    await server.start()
    logger.info("BLE server started — advertising as 'RaspberryPi'")
    logger.info("Waiting for phone to connect and subscribe...")

    # ── Send loop ─────────────────────────────────────────────────────────────
    try:
        while True:
            await asyncio.sleep(SEND_INTERVAL)

            data  = collect_data()
            payload = json.dumps(data)              # dict → JSON string
            raw     = payload.encode("utf-8")       # string → bytes

            logger.info(f"Sending: {payload}")

            # Write the bytes to the characteristic and notify all subscribers
            server.get_characteristic(CHAR_UUID).value = bytearray(raw)
            server.update_value(SERVICE_UUID, CHAR_UUID)

    except KeyboardInterrupt:
        logger.info("Stopping server...")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(run())