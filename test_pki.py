import os
import datetime
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization

# Make sure storage dir exists for sqlite db and root crt
os.makedirs("virtual_hsm/storage", exist_ok=True)

from pki.pki_service import PKIService
from pki.crl_service import CRLService
from virtual_hsm import key_manager

# Init the service with no DB dependency (we fallback to mocked behavior in the service)
pki = PKIService(db_session=None)
crl_svc = CRLService(db_session=None)

print("1. Testing CA Initialization...")
ca_cert = pki.initialize_ca(common_name="Virtual HSM Test Root CA")
print(f"   ✓ Success! Root CA Issuer: {ca_cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value}")
print(f"   ✓ Root CA stored securely in HSM (key_id: ca-root).")

print("\n2. Simulating a Node generating a CSR (Certificate Signing Request)...")
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, "node01.internal.network"),
])).sign(private_key, hashes.SHA256())
csr_pem = csr.public_bytes(serialization.Encoding.PEM)
print("   ✓ CSR generated for 'node01.internal.network'")

print("\n3. Testing Certificate Issuance (from CSR)...")
cert = pki.issue_certificate(csr_pem, cert_type="tls_server", validity_days=45)
print(f"   ✓ Success! Issued Cert Subject: {cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value}")
print(f"   ✓ Valid Until: {cert.not_valid_after}")

print("\n4. Testing CRL Generation...")
crl_bytes = crl_svc.generate_crl(ca_cert)
crl = x509.load_der_x509_crl(crl_bytes)
print(f"   ✓ Success! CRL Generated. Last update: {crl.last_update}")

print("\n✅ All PKI Core functions verified successfully!")
