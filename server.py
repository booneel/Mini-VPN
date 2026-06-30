import os
import struct
import fcntl

import socket
import select
from protocol import *
from config import TIMEOUT, SERVER_PORT

from key_exchange import initialize_server_keys
from handlers import handle_key_request, handle_data, handle_aes_key, send_data

from session import Session
import time


TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000

fd = os.open("/dev/net/tun", os.O_RDWR)
ifreq = struct.pack("16sH", b"tun0", IFF_TUN | IFF_NO_PI)
fcntl.ioctl(fd, TUNSETIFF, ifreq)

os.system("ip addr replace 10.0.0.2/24 dev tun0")
os.system("ip link set tun0 up")

session = Session()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', SERVER_PORT))


private_key, public_key = initialize_server_keys()
print("[SERVER] VPN_SERVER Started")
try:
    while True:
        if session.session_key is not None:
            if time.time() - session.last_seen > TIMEOUT:
                print(f"[TIMEOUT] {session.client_address}")
                session.session_key = None
                session.client_address = None
        readable, _, _ = select.select([fd, server_socket], [], [], 1)
        for r in readable:
            if r == fd:
                if session.session_key is None:
                    continue
                packet = os.read(fd, 2048)
                if session.client_address:
                    send_data(server_socket, session.client_address, packet, session.session_key)
            elif r == server_socket:
                packet, addr = server_socket.recvfrom(2048)
                version, packet_type, payload = parse_packet(packet)

                session.client_address = addr
                session.last_seen = time.time()

                if packet_type == KEY_REQUEST:
                    print("[SERVER] Packet Received")
                    handle_key_request(server_socket, addr, public_key)
                    continue
                elif packet_type == DATA:
                    if session.session_key is None:
                        continue
                    plain_packet = handle_data(payload, session.session_key)
                    if plain_packet:
                        os.write(fd, plain_packet)
                elif packet_type == AES_KEY:
                    session.session_key = handle_aes_key(private_key, payload)
                    continue
                elif packet_type == KEEP_ALIVE:
                    print("[SERVER] KEEP_ALIVE")
                    continue
                else:
                    print(f"Unknown packet type : {packet_type}")
except KeyboardInterrupt:
    print("Exit")
finally:
    os.system("ip link delete tun0")