"""Virtual HSM authentication service using salted PBKDF2 hashes."""

import base64
import getpass
import hashlib
import hmac
import json
import os
from pathlib import Path


AUTH_DIR = Path(__file__).parent / "storage"
AUTH_DB_PATH = AUTH_DIR / "auth.json"
PBKDF2_ITERATIONS = 240000
SALT_BYTES = 16
DEFAULT_BOOTSTRAP_PASSWORD = "admin123"


def _pbkdf2(password: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)


def _bootstrap_if_missing() -> None:
    """Create an initial credential file if it does not exist yet."""
    if AUTH_DB_PATH.exists():
        return

    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    initial_password = os.getenv("VIRTUAL_HSM_DEFAULT_PASSWORD", DEFAULT_BOOTSTRAP_PASSWORD)
    salt = os.urandom(SALT_BYTES)
    password_hash = _pbkdf2(initial_password, salt, PBKDF2_ITERATIONS)

    record = {
        "scheme": "PBKDF2-HMAC-SHA256",
        "iterations": PBKDF2_ITERATIONS,
        "salt": base64.b64encode(salt).decode("ascii"),
        "password_hash": base64.b64encode(password_hash).decode("ascii"),
    }
    AUTH_DB_PATH.write_text(json.dumps(record, indent=2), encoding="utf-8")


def _read_record() -> dict:
    _bootstrap_if_missing()
    record = json.loads(AUTH_DB_PATH.read_text(encoding="utf-8"))
    required = {"iterations", "salt", "password_hash"}
    if not required.issubset(record):
        raise ValueError("Invalid credential store format.")
    return record


def verify_password(password: str) -> bool:
    """Validate a password against the persisted salted PBKDF2 hash."""
    record = _read_record()
    iterations = int(record["iterations"])
    salt = base64.b64decode(record["salt"])
    stored_hash = base64.b64decode(record["password_hash"])
    candidate_hash = _pbkdf2(password, salt, iterations)
    return hmac.compare_digest(candidate_hash, stored_hash)


def authenticate(max_attempts: int = 3) -> bool:
    """Prompt in terminal and validate credentials."""
    print("\nVirtual HSM Authentication")
    for attempt in range(1, max_attempts + 1):
        password = getpass.getpass(f"Enter HSM password (attempt {attempt}/{max_attempts}): ")
        if verify_password(password):
            print("Authentication successful.\n")
            return True
        print("Invalid password.")
    print("Maximum attempts exceeded. Access denied.\n")
    return False


def set_password(new_password: str) -> None:
    """Persist a new salted PBKDF2 credential."""
    if not new_password:
        raise ValueError("Password cannot be empty.")

    salt = os.urandom(SALT_BYTES)
    password_hash = _pbkdf2(new_password, salt, PBKDF2_ITERATIONS)
    record = {
        "scheme": "PBKDF2-HMAC-SHA256",
        "iterations": PBKDF2_ITERATIONS,
        "salt": base64.b64encode(salt).decode("ascii"),
        "password_hash": base64.b64encode(password_hash).decode("ascii"),
    }
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    AUTH_DB_PATH.write_text(json.dumps(record, indent=2), encoding="utf-8")


def change_password(old_password: str, new_password: str) -> bool:
    """Change the HSM password after validating the old password."""
    if not verify_password(old_password):
        return False
    set_password(new_password)
    return True
