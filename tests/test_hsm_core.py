import tempfile
import unittest
from pathlib import Path

from virtual_hsm import auth
from virtual_hsm import key_manager
from virtual_hsm.hsm_core import HSMCore


class HSMCoreSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self.temp_dir_obj.name)

        self.orig_auth_dir = auth.AUTH_DIR
        self.orig_auth_db_path = auth.AUTH_DB_PATH
        self.orig_db_dir = key_manager.DB_DIR
        self.orig_db_path = key_manager.DB_PATH

        auth.AUTH_DIR = self.temp_dir / "storage"
        auth.AUTH_DB_PATH = auth.AUTH_DIR / "auth.json"
        key_manager.DB_DIR = self.temp_dir / "storage"
        key_manager.DB_PATH = key_manager.DB_DIR / "keys.db"

        auth.set_password("admin123")
        self.hsm = HSMCore()

    def tearDown(self):
        auth.AUTH_DIR = self.orig_auth_dir
        auth.AUTH_DB_PATH = self.orig_auth_db_path
        key_manager.DB_DIR = self.orig_db_dir
        key_manager.DB_PATH = self.orig_db_path
        self.temp_dir_obj.cleanup()

    def test_authentication_required_for_operations(self):
        with self.assertRaises(PermissionError):
            self.hsm.generate_key("AES")
        with self.assertRaises(PermissionError):
            self.hsm.list_keys()

    def test_aes_roundtrip_after_login(self):
        self.assertTrue(self.hsm.login("admin123"))
        key_id = self.hsm.generate_key("AES")
        ciphertext = self.hsm.encrypt(key_id, "hello-hsm")
        plaintext = self.hsm.decrypt(key_id, ciphertext)
        self.assertEqual(plaintext, "hello-hsm")

    def test_rsa_sign_and_verify_after_login(self):
        self.assertTrue(self.hsm.login("admin123"))
        key_id = self.hsm.generate_key("RSA")
        signature = self.hsm.sign(key_id, "message")
        self.assertTrue(self.hsm.verify(key_id, "message", signature))
        self.assertFalse(self.hsm.verify(key_id, "tampered", signature))

    def test_password_rotation_requires_reauth(self):
        self.assertTrue(self.hsm.login("admin123"))
        self.assertTrue(self.hsm.rotate_password("admin123", "newpass123"))

        with self.assertRaises(PermissionError):
            self.hsm.generate_key("AES")

        self.assertTrue(self.hsm.login("newpass123"))
        key_id = self.hsm.generate_key("AES")
        self.assertTrue(key_id.startswith("aes-"))


if __name__ == "__main__":
    unittest.main()
