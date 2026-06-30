import os
import argparse

import struct
import fcntl

import socket
import time

import select

from protocol import *
from handlers import handle_data, handle_public_key, send_data, send_keep_alive
from config import KEEP_ALIVE_INTERVAL, REKEY_INTERVAL
from crypto import generate_key
from key_exchange import encrypt_key


from session import Session

TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000

fd = os.open("/dev/net/tun", os.O_RDWR)
ifreq = struct.pack("16sH", b"tun0", IFF_TUN | IFF_NO_PI)
fcntl.ioctl(fd, TUNSETIFF, ifreq)

os.system("ip addr replace 10.0.0.1/24 dev tun0")
os.system("ip link set tun0 up")

parser = argparse.ArgumentParser(description="Mini VPN Client")

parser.add_argument(
    "--server",
    required=True,
    help="VPN Server IP"
)

parser.add_argument(
    "--port",
    type=int,
    default=5000,
    help="VPN Server Port"
)

args = parser.parse_args()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (args.server, args.port)

session = Session()


initialize_packet = build_packet(KEY_REQUEST, b"")
server_socket.sendto(initialize_packet, server_address)
print("[CLIENT] Send KEY_REQUEST")

try:
    while True:
        now = time.time()
        if now - session.last_rekey >= REKEY_INTERVAL:
            print("[CLIENT] Rekey Start")
            new_key = generate_key()
            encrypted_key = encrypt_key(
                session.server_public_key,
                new_key
            )
            send_packet = build_packet(AES_KEY, encrypted_key)
            server_socket.sendto(send_packet, server_address)
            session.session_key = new_key
            session.last_rekey = now
            print("[CLIENT] Rekey Sent")
        if now - session.last_keepalive >= KEEP_ALIVE_INTERVAL:
            if session.session_key is not None:
                send_keep_alive(server_socket, server_address)
                print("[CLIENT] KEEP_ALIVE")
                session.last_keepalive = now
        readable, _, _ = select.select([fd, server_socket], [], [], 1)
        for r in readable:
            if r == fd:
                if session.session_key is None:
                    continue
                packet = os.read(fd, 2048)
                send_data(server_socket, server_address, packet, session.session_key)
            elif r == server_socket:
                packet, addr = server_socket.recvfrom(2048)

                version, packet_type, payload = parse_packet(packet)

                if packet_type == PUBLIC_KEY:
                    handle_public_key(
                        session,
                        server_socket,
                        server_address,
                        payload
                    )

                elif packet_type == DATA:
                    if session.session_key is None:
                        continue
                    plain_packet = handle_data(payload, session.session_key)
                    if plain_packet:
                        os.write(fd, plain_packet)

                else:
                    print(f"Unknown packet type : {packet_type}")
except KeyboardInterrupt:
    print("Exit")
finally:
    os.system("ip link delete tun0")