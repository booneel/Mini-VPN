from pathlib import Path

KEY_DIR = Path("keys")

PRIVATE_KEY_FILE = KEY_DIR / "server_private.pem"
PUBLIC_KEY_FILE = KEY_DIR / "server_public.pem"

KEEP_ALIVE_INTERVAL = 10
TIMEOUT = 10

REKEY_INTERVAL = 10

SERVER_PORT = 5000
