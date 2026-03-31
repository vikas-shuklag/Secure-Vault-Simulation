"""
Virtual HSM — Crypto Service
Performs cryptographic operations using keys stored inside the HSM.
Keys are accessed via key_manager and NEVER exposed externally.
"""

import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
import datetime
import ipaddress

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


# ──────────────────── X.509 Certificate Issuance ────────────────────

def issue_certificate(
    ca_private_key,        # CA key from your key_manager
    ca_cert,               # CA certificate (x509.Certificate)
    subject_public_key,    # Requester's public key
    common_name: str,
    san_dns: list[str] = None,
    san_ip: list[str] = None,
    cert_type: str = "tls_server",   # tls_server | client | code_signing
    validity_days: int = 365
) -> x509.Certificate:
    
    now = datetime.datetime.utcnow()
    
    # Build Subject Alternative Names
    san_list = []
    for dns in (san_dns or []):
        san_list.append(x509.DNSName(dns))
    for ip in (san_ip or []):
        try:
            san_list.append(x509.IPAddress(ipaddress.ip_address(ip)))
        except ValueError:
            pass # Invalid IP
    
    builder = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ]))
        .issuer_name(ca_cert.subject)
        .public_key(subject_public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=validity_days))
    )

    if san_list:
        builder = builder.add_extension(x509.SubjectAlternativeName(san_list), critical=False)
        
    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True
    ).add_extension(
        x509.AuthorityKeyIdentifier.from_issuer_public_key(
            ca_cert.public_key()
        ), critical=False
    )
    
    # Add EKU based on cert type
    eku_map = {
        "tls_server": [ExtendedKeyUsageOID.SERVER_AUTH],
        "client":     [ExtendedKeyUsageOID.CLIENT_AUTH],
        "code_signing": [ExtendedKeyUsageOID.CODE_SIGNING],
    }
    builder = builder.add_extension(
        x509.ExtendedKeyUsage(eku_map.get(cert_type, [ExtendedKeyUsageOID.SERVER_AUTH])),
        critical=False
    )
    
    return builder.sign(ca_private_key, hashes.SHA256())
