"""
Virtual HSM — Crypto Service
Performs cryptographic operations using keys stored inside the HSM.
Keys are accessed via key_manager and NEVER exposed externally.
"""

import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

from virtual_hsm import key_manager


# ──────────────────── AES Encryption / Decryption ────────────────────

def encrypt(key_id: str, plaintext: str) -> str:
    """
    Encrypt plaintext using AES-256-GCM.
    Returns a base64-encoded string (nonce + ciphertext).
    """
    record = key_manager.get_key(key_id)
    if record is None:
        raise ValueError(f"Key '{key_id}' not found in HSM.")
    
    key_type, key_bytes = record
    if key_type != "AES-256":
        raise TypeError(f"Key '{key_id}' is {key_type}, expected AES-256 for encryption.")

    import os
    nonce = os.urandom(12)  # 96-bit nonce for GCM
    aesgcm = AESGCM(key_bytes)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)

    # Pack nonce + ciphertext and base64-encode for transport
    return base64.b64encode(nonce + ciphertext).decode()


def decrypt(key_id: str, token: str) -> str:
    """
    Decrypt a base64-encoded AES-256-GCM token.
    Returns the plaintext string.
    """
    record = key_manager.get_key(key_id)
    if record is None:
        raise ValueError(f"Key '{key_id}' not found in HSM.")
    
    key_type, key_bytes = record
    if key_type != "AES-256":
        raise TypeError(f"Key '{key_id}' is {key_type}, expected AES-256 for decryption.")

    raw = base64.b64decode(token)
    nonce, ciphertext = raw[:12], raw[12:]
    aesgcm = AESGCM(key_bytes)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()


# ──────────────────── RSA Signing / Verification ────────────────────

def _load_rsa_private_key(pem_bytes: bytes):
    """Load an RSA private key from PEM bytes."""
    return serialization.load_pem_private_key(pem_bytes, password=None)


def sign(key_id: str, data: str) -> str:
    """
    Sign data using RSA-PSS with SHA-256.
    Returns a base64-encoded signature.
    """
    record = key_manager.get_key(key_id)
    if record is None:
        raise ValueError(f"Key '{key_id}' not found in HSM.")
    
    key_type, key_bytes = record
    if key_type != "RSA-2048":
        raise TypeError(f"Key '{key_id}' is {key_type}, expected RSA-2048 for signing.")

    private_key = _load_rsa_private_key(key_bytes)
    signature = private_key.sign(
        data.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode()


def verify(key_id: str, data: str, signature_b64: str) -> bool:
    """
    Verify an RSA-PSS signature.
    Returns True if valid, False otherwise.
    """
    record = key_manager.get_key(key_id)
    if record is None:
        raise ValueError(f"Key '{key_id}' not found in HSM.")
    
    key_type, key_bytes = record
    if key_type != "RSA-2048":
        raise TypeError(f"Key '{key_id}' is {key_type}, expected RSA-2048 for verification.")

    private_key = _load_rsa_private_key(key_bytes)
    public_key = private_key.public_key()
    signature = base64.b64decode(signature_b64)

    try:
        public_key.verify(
            signature,
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False
