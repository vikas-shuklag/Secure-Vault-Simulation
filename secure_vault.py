import os
from crypto_engine import encrypt_data, decrypt_data

VAULT_PATH = "storage/vault.enc"

def store_secret(secret):

    encrypted = encrypt_data(secret.encode())

    with open(VAULT_PATH, "wb") as f:
        f.write(encrypted)

    print("Secret stored securely")


def retrieve_secret():

    if not os.path.exists(VAULT_PATH):
        print("Vault empty")
        return

    with open(VAULT_PATH, "rb") as f:
        encrypted = f.read()

    decrypted = decrypt_data(encrypted)

    print("Stored Secret:", decrypted.decode())