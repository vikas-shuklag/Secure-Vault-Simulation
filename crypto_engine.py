from cryptography.fernet import Fernet
import os

KEY_PATH = "keys/master.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_PATH, "wb") as f:
        f.write(key)
    return key

def load_key():
    if not os.path.exists(KEY_PATH):
        return generate_key()

    with open(KEY_PATH, "rb") as f:
        return f.read()

def encrypt_data(data: bytes):
    key = load_key()
    cipher = Fernet(key)
    return cipher.encrypt(data)

def decrypt_data(data: bytes):
    key = load_key()
    cipher = Fernet(key)
    return cipher.decrypt(data)