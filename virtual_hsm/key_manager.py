"""
Virtual HSM — Key Manager
Generates, stores, and retrieves cryptographic keys.
Keys NEVER leave this module — only internal access is permitted.
"""

import os
import uuid
import sqlite3
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Database path relative to this file
DB_DIR = Path(__file__).parent / "storage"
DB_PATH = DB_DIR / "keys.db"


def _get_connection() -> sqlite3.Connection:
    """Get a connection to the key store database."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            id   TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            key  BLOB NOT NULL
        )
    """)
    conn.commit()
    return conn


def generate_aes_key() -> str:
    """
    Generate a 256-bit AES key and store it in the HSM.
    Returns the key_id (the key material is NEVER exposed).
    """
    key_id = f"aes-{uuid.uuid4().hex[:12]}"
    key_bytes = os.urandom(32)  # 256-bit

    conn = _get_connection()
    conn.execute("INSERT INTO keys (id, type, key) VALUES (?, ?, ?)",
                 (key_id, "AES-256", key_bytes))
    conn.commit()
    conn.close()
    return key_id


def generate_rsa_key() -> str:
    """
    Generate a 2048-bit RSA key pair and store the private key in the HSM.
    Returns the key_id (the key material is NEVER exposed).
    """
    key_id = f"rsa-{uuid.uuid4().hex[:12]}"
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    pem_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    conn = _get_connection()
    conn.execute("INSERT INTO keys (id, type, key) VALUES (?, ?, ?)",
                 (key_id, "RSA-2048", pem_bytes))
    conn.commit()
    conn.close()
    return key_id


def get_key(key_id: str):
    """
    Retrieve key material by key_id.
    ⚠ INTERNAL USE ONLY — must never be called from the CLI layer.
    Returns (type, key_bytes) or None.
    """
    conn = _get_connection()
    row = conn.execute("SELECT type, key FROM keys WHERE id = ?",
                       (key_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return row  # (type_str, key_bytes)


def list_keys() -> list:
    """
    List all key IDs and their types stored in the HSM.
    Key material is NOT included.
    """
    conn = _get_connection()
    rows = conn.execute("SELECT id, type FROM keys").fetchall()
    conn.close()
    return rows

def store_ca_key(pem_bytes: bytes) -> str:
    """Store the root CA private key."""
    conn = _get_connection()
    # Check if exists to replace or insert
    exists = conn.execute("SELECT id FROM keys WHERE id = 'ca-root'").fetchone()
    if exists:
        conn.execute("UPDATE keys SET type = ?, key = ? WHERE id = ?",
                     ("RSA-CA", pem_bytes, "ca-root"))
    else:
        conn.execute("INSERT INTO keys (id, type, key) VALUES (?, ?, ?)",
                     ("ca-root", "RSA-CA", pem_bytes))
    conn.commit()
    conn.close()
    return "ca-root"

def load_ca_key() -> bytes:
    """Retrieve the CA private key bytes."""
    record = get_key("ca-root")
    if not record:
        raise ValueError("CA Root key not found in HSM.")
    _, key_bytes = record
    return key_bytes

