import pytest
from pki.pki_service import PKIService
from pki.crl_service import CRLService
import os

# Ensuring storage directory for the database mocked session
os.makedirs("virtual_hsm/storage", exist_ok=True)

@pytest.fixture
def pki_service():
    # Pass None for the DB Session; it falls back to mock logic
    return PKIService(db_session=None)

def test_ca_initialization(pki_service):
    """Verify that the HSM orchestrates the signing correctly."""
    ca_cert = pki_service.initialize_ca(common_name="Virtual HSM Master Root CA")
    assert ca_cert is not None
    assert ca_cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value == "Virtual HSM Master Root CA"

def test_pki_issue_logic(pki_service):
    """Verify standard logic flow."""
    import cryptography.hazmat.primitives.asymmetric.rsa as rsa
    import cryptography.hazmat.primitives.hashes as hashes
    from cryptography.x509.oid import NameOID
    from cryptography import x509
    from cryptography.hazmat.primitives import serialization

    # Seed the test CA
    pki_service.initialize_ca("Test CA")

    # Generate test CSR
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024) # Small size for speed
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "mock.internal"),
    ])).sign(private_key, hashes.SHA256())
    csr_pem = csr.public_bytes(serialization.Encoding.PEM)

    # Issue from core service
    cert = pki_service.issue_certificate(csr_pem, cert_type="tls_server", validity_days=10)
    assert cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == "mock.internal"
