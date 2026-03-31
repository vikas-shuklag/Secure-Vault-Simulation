"""
Virtual HSM — CRL Service
Generates Certificate Revocation Lists.
"""

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
import datetime

from virtual_hsm import key_manager
from pki.models import IssuedCertificate

class CRLService:
    def __init__(self, db_session=None):
        self.db = db_session

    def generate_crl(self, ca_cert: x509.Certificate) -> bytes:
        """Generate a DER-encoded CRL based on the database."""
        ca_key_bytes = key_manager.load_ca_key()
        ca_key = serialization.load_pem_private_key(ca_key_bytes, password=None)
        
        now = datetime.datetime.utcnow()
        builder = x509.CertificateRevocationListBuilder()
        builder = builder.issuer_name(ca_cert.subject)
        builder = builder.last_update(now)
        builder = builder.next_update(now + datetime.timedelta(days=1))
        
        if self.db:
            revoked_certs = self.db.query(IssuedCertificate).filter_by(is_revoked=True).all()
            for rec in revoked_certs:
                revoked_cert_builder = x509.RevokedCertificateBuilder()
                revoked_cert_builder = revoked_cert_builder.serial_number(int(rec.serial))
                revoked_cert_builder = revoked_cert_builder.revocation_date(rec.revoked_at)
                # Omitted specific ReasonFlags for brevity, maps from rec.revoke_reason
                revoked_cert = revoked_cert_builder.build()
                builder = builder.add_revoked_certificate(revoked_cert)

        crl = builder.sign(private_key=ca_key, algorithm=hashes.SHA256())
        return crl.public_bytes(serialization.Encoding.DER)
