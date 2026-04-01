import socket

# server_address = "A0:51:0B:AB:7C:D1"  # ARCH PC Bluetooth MAC address
server_address = "FC:01:7C:92:05:6C"  # JOEY PC Bluetooth MAC address
port = 4


def send_file(filename):
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    sock.connect((server_address, port))

    with open(filename, "rb") as f:
        data = f.read(1024)
        while data:
            sock.sendall(data)
            data = f.read(1024)

    print("File sent successfully")
    sock.close()
    print("Socket closed on client side")


if __name__ == "__main__":
    send_file("vna_data_2025-07-07_00-56-41.json")
