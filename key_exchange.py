from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from config import *

def initialize_server_keys():
    KEY_DIR.mkdir(exist_ok=True. parents=True)
    if not PRIVATE_KEY_FILE.exists() or not PUBLIC_KEY_FILE.exists():
        private_key, public_key = generate_keypair()
        save_private_key(private_key)
        save_public_key(public_key)
    private_key = load_private_key()
    public_key = load_public_key()
    return private_key, public_key

def generate_keypair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key

def save_private_key(private_key):
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with PRIVATE_KEY_FILE.open("wb") as key_file:
        key_file.write(pem)

def save_public_key(public_key):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with PUBLIC_KEY_FILE.open("wb") as key_file:
        key_file.write(pem)

def load_private_key():
    with PRIVATE_KEY_FILE.open("rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )
    return private_key

def load_public_key():
    with PUBLIC_KEY_FILE.open("rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
        )
    return public_key

def public_key_to_bytes(public_key):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem

def load_public_key_from_bytes(data):
    public_key = serialization.load_pem_public_key(
        data
    )
    return public_key

def encrypt_key(public_key, aes_key):
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_key

def decrypt_key(private_key, encrypted_key):
    decrypted_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_key