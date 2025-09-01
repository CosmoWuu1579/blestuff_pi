import numpy as np
import json
import socket
from matplotlib import pyplot as plt
local_bt_addr = "00:1A:7D:DA:71:13"  # Your PC's Bluetooth MAC address
port = 4

server_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
server_sock.bind((local_bt_addr, port))
server_sock.listen(1)

print("Waiting for connection...")
client_sock, client_info = server_sock.accept()
print(f"Accepted connection from {client_info}")

client_sock.settimeout(10)  # 10 seconds timeout

output_filename = "received_data.json"
with open(output_filename, "wb") as f:
    try:
        while True:
            data = client_sock.recv(1024)
            if not data:
                print("No more data received, closing connection")
                break
            print(f"Received {len(data)} bytes")
            f.write(data)
    except socket.timeout:
        print("Socket timed out, assuming end of file")
    except OSError:
        pass

print(f"File received and saved as {output_filename}")

client_sock.close()
server_sock.close()

with open('received_data.json', 'r') as jsonFile:
    data = json.load(jsonFile)

fig,ax = plt.subplots(2, 1, figsize=(10, 6),num = 1)
ax[0].plot(np.array(data['frequencies'])*1e-6, data['RL'])
ax[0].set_xlabel('Frequency (MHz)')
ax[0].set_ylabel('Reflection Coefficient (dB)')
ax[0].grid(True, which='both', linestyle='--', linewidth=0.5)

ax[1].plot(np.array(data['frequencies'])*1e-6, data['RLPHASE'])
ax[1].set_xlabel('Frequency (MHz)')
ax[1].set_ylabel('S11 Phase (deg)')
ax[1].grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.show()
