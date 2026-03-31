"""
Virtual HSM — PKI Service
Handles CA Initialization, X.509 Certificate Issuance, and Revocation.
"""

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import NameOID
import datetime
import uuid
from pathlib import Path

from virtual_hsm.crypto_service import issue_certificate
from virtual_hsm import key_manager
from pki.models import IssuedCertificate

# In this staged implementation (before PostgreSQL is fully wired with a Session), 
# we use a minimal interface or placeholders for DB just to scaffold the logic.
# A true DB session injection will come in future API commits.

STORAGE_DIR = Path("virtual_hsm/storage")
CA_CERT_PATH = STORAGE_DIR / "ca_root.crt"

class PKIService:
    def __init__(self, db_session=None):
        self.db = db_session

    def initialize_ca(self, common_name: str = "Virtual HSM Root CA"):
        """Generate self-signed Root CA. Call once at setup."""
        if CA_CERT_PATH.exists() and key_manager.get_key("ca-root"):
             # Already initialized
             return self.load_ca_cert()

        ca_key = rsa.generate_private_key(
            public_exponent=65537, key_size=4096
        )
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Virtual HSM"),
        ])
        now = datetime.datetime.utcnow()
        ca_cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(ca_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now)
            .not_valid_after(now + datetime.timedelta(days=3650))  # 10 years
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(ca_key, hashes.SHA256())
        )

        ca_key_pem = ca_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        )
        
        # Store CA key securely inside the HSM SQLite boundary
        key_manager.store_ca_key(ca_key_pem)

        # Store the public CA Cert on disk
        with open(CA_CERT_PATH, "wb") as f:
             f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

        return ca_cert

    def load_ca_cert(self) -> x509.Certificate:
        if not CA_CERT_PATH.exists():
            raise FileNotFoundError("CA Certificate not found. Initialize CA first.")
        with open(CA_CERT_PATH, "rb") as f:
            return x509.load_pem_x509_certificate(f.read())

    def issue_certificate(self, csr_pem: bytes, cert_type: str = "tls_server", validity_days: int = 365):
        """Issue a certificate from a CSR."""
        csr = x509.load_pem_x509_csr(csr_pem)
        if not csr.is_signature_valid:
            raise ValueError("Invalid CSR signature")
        
        ca_key_bytes = key_manager.load_ca_key()
        ca_key = serialization.load_pem_private_key(ca_key_bytes, password=None)
        ca_cert = self.load_ca_cert()
        
        common_name = csr.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

        cert = issue_certificate(
            ca_private_key=ca_key,
            ca_cert=ca_cert,
            subject_public_key=csr.public_key(),
            common_name=common_name,
            cert_type=cert_type,
            validity_days=validity_days
        )

        self._store_certificate(cert, common_name, cert_type)
        return cert

    def _store_certificate(self, cert: x509.Certificate, common_name: str, cert_type: str):
        """Save issuance record to DB."""
        if not self.db:
            return # Mocking if no DB session provided yet
            
        record = IssuedCertificate(
            serial=str(cert.serial_number),
            common_name=common_name,
            cert_type=cert_type,
            cert_pem=cert.public_bytes(serialization.Encoding.PEM).decode('utf-8'),
            expires_at=cert.not_valid_after
        )
        self.db.add(record)
        self.db.commit()

    def revoke_certificate(self, serial_number: str, reason: str = "unspecified"):
        """Add cert to revocation list."""
        if not self.db:
             return
             
        record = self.db.query(IssuedCertificate).filter_by(serial=serial_number).first()
        if not record:
             raise ValueError("Certificate not found.")
             
        record.is_revoked = True
        record.revoked_at = datetime.datetime.utcnow()
        record.revoke_reason = reason
        self.db.commit()

    def check_ocsp_status(self, serial_number: str) -> str:
        """Return 'good', 'revoked', or 'unknown'."""
        if not self.db:
             return "unknown"
             
        record = self.db.query(IssuedCertificate).filter_by(serial=serial_number).first()
        if not record:
             return "unknown"
        if record.is_revoked:
             return "revoked"
        return "good"
