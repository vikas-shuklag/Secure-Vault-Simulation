import hashlib
import os

TRUST_FILE = "keys/root_hash.txt"

def generate_root_hash(data):
    root_hash = hashlib.sha256(data).hexdigest()

    with open(TRUST_FILE, "w") as f:
        f.write(root_hash)

def verify_root(data):
    if not os.path.exists(TRUST_FILE):
        generate_root_hash(data)
        return True

    with open(TRUST_FILE, "r") as f:
        stored_hash = f.read()

    current_hash = hashlib.sha256(data).hexdigest()

    return stored_hash == current_hash