"""
Virtual HSM — HSM Core
Central controller that orchestrates authentication, policy checks,
key management, and cryptographic operations.

Keys NEVER leave this boundary.
"""

from virtual_hsm import key_manager
from virtual_hsm import crypto_service
from virtual_hsm import policy_engine
from virtual_hsm import auth


class HSMCore:
    """Virtual Hardware Security Module — core controller."""

    def __init__(self):
        self.authenticated = False

    def login(self, password: str) -> bool:
        """Authenticate a session before allowing HSM operations."""
        self.authenticated = auth.verify_password(password)
        return self.authenticated

    def logout(self):
        """Clear the current session authentication state."""
        self.authenticated = False

    def _require_authentication(self):
        if not self.authenticated:
            raise PermissionError("Authentication required before HSM operations.")

    # ─── Key Operations ──────────────────────────────────────────

    def generate_key(self, key_type: str) -> str:
        """
        Generate a new cryptographic key inside the HSM.
        Returns key_id only — key material stays internal.
        """
        self._require_authentication()
        policy_engine.check_policy("generate_key")

        if key_type.upper() == "AES":
            key_id = key_manager.generate_aes_key()
        elif key_type.upper() == "RSA":
            key_id = key_manager.generate_rsa_key()
        else:
            raise ValueError(f"Unsupported key type: {key_type}")

        return key_id

    # ─── Encryption / Decryption ─────────────────────────────────

    def encrypt(self, key_id: str, plaintext: str) -> str:
        """Encrypt data using a key stored in the HSM."""
        self._require_authentication()
        policy_engine.check_policy("encrypt")
        return crypto_service.encrypt(key_id, plaintext)

    def decrypt(self, key_id: str, token: str) -> str:
        """Decrypt data using a key stored in the HSM."""
        self._require_authentication()
        policy_engine.check_policy("decrypt")
        return crypto_service.decrypt(key_id, token)

    # ─── Signing / Verification ──────────────────────────────────

    def sign(self, key_id: str, data: str) -> str:
        """Sign data using a key stored in the HSM."""
        self._require_authentication()
        policy_engine.check_policy("sign")
        return crypto_service.sign(key_id, data)

    def verify(self, key_id: str, data: str, signature: str) -> bool:
        """Verify a signature using a key stored in the HSM."""
        self._require_authentication()
        policy_engine.check_policy("verify")
        return crypto_service.verify(key_id, data, signature)

    # ─── Key Listing ─────────────────────────────────────────────

    def list_keys(self) -> list:
        """List all key IDs and types (no key material)."""
        self._require_authentication()
        policy_engine.check_policy("list_keys")
        return key_manager.list_keys()

    def rotate_password(self, old_password: str, new_password: str) -> bool:
        """Rotate the HSM admin password for future logins."""
        self._require_authentication()
        policy_engine.check_policy("rotate_password")
        changed = auth.change_password(old_password, new_password)
        if changed:
            # Require a fresh login after credential rotation.
            self.authenticated = False
        return changed
