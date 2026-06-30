from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt(packet, key):
    nonce = os.urandom(12)
    aes = AESGCM(key)
    cipher_packet = aes.encrypt(nonce, packet, None)
    return nonce, cipher_packet


def decrypt(nonce, cipher_packet, key):
    aes = AESGCM(key)
    return aes.decrypt(nonce, cipher_packet, None)

def generate_key():
    return AESGCM.generate_key(bit_length=256)

def save_key(key, filename):
    with open(filename, "wb") as f:
        f.write(key)
    print("save key!")

def load_key(filename):
    with open(filename, "rb") as f:
        return f.read()