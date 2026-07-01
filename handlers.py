import time

from crypto import *
from protocol import *
from key_exchange import *

def handle_key_request(server_socket, client_address, public_key):
    pem = public_key_to_bytes(public_key)
    send_packet = build_packet(PUBLIC_KEY, pem)
    server_socket.sendto(send_packet, client_address)
    print("[SERVER] PUBLIC_KEY Sent")

def handle_public_key(session, server_socket, server_address, payload):
    print("[CLIENT] PUBLIC_KEY Received")

    server_public_key = load_public_key_from_bytes(payload)
    session_key = generate_key()

    session.server_public_key = server_public_key
    session.session_key = session_key

    encrypted_key = encrypt_key(server_public_key, session_key)

    send_packet = build_packet(AES_KEY, encrypted_key)

    server_socket.sendto(send_packet, server_address)

    print("[CLIENT] AES_KEY Sent")

    session.last_rekey = time.time()

def handle_aes_key(private_key, payload):
    session_key = decrypt_key(private_key, payload)

    print("[SERVER] AES_KEY Received")

    return session_key

def handle_data(packet, session_key):
    nonce = packet[:12]
    cipher_packet = packet[12:]
    try:
        return decrypt(nonce, cipher_packet, session_key)
    except Exception:
        return None

def send_data(server_socket, address, packet, session_key):
    try:
        nonce, cipher_packet = encrypt(packet, session_key)
        vpn_payload = nonce + cipher_packet
        send_packet = build_packet(DATA, vpn_payload)
        server_socket.sendto(send_packet, address)
    except Exception as e:
        print(e)
def send_keep_alive(server_socket, address):
    packet = build_packet(KEEP_ALIVE, b"")
    server_socket.sendto(packet, address)