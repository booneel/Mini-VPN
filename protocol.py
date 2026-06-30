VERSION = 1

DATA = 0x01
KEY_REQUEST = 0x02
PUBLIC_KEY = 0x03
AES_KEY = 0x04
KEEP_ALIVE = 0x05

def build_packet(packet_type, payload):
    return bytes([VERSION]) + bytes([packet_type]) + payload

def parse_packet(packet):
    if len(packet) < 2:
        raise ValueError("Invalid packet")
    version = packet[0]
    packet_type = packet[1]
    payload = packet[2:]
    if version != VERSION:
        raise ValueError("Unsupported protocol version")
    return version, packet_type, payload