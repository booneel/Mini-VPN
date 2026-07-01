import time


class Session:
    def __init__(self):
        self.client_address = None
        self.session_key = None
        self.last_seen = time.time()
        self.last_keepalive = time.time()
        self.last_rekey = time.time()
        self.server_public_key = None