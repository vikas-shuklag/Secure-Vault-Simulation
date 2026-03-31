from cryptography.x509 import ocsp
from cryptography.hazmat.primitives import hashes, serialization
import datetime
from sqlalchemy.orm import Session

from pki.pki_service import PKIService
from virtual_hsm.crypto_service import key_manager
from cryptography import x509

class OCSPService:
    def __init__(self, db_session: Session):
        self.pki = PKIService(db_session=db_session)

    def generate_response(self, ocsp_req_der: bytes) -> bytes:
        """Process an OCSP request and generate an RFC 6960 signed response."""
        ocsp_request = ocsp.load_der_ocsp_request(ocsp_req_der)
        serial = str(ocsp_request.serial_number)
        
        status = self.pki.check_ocsp_status(serial)
        ca_cert = self.pki.load_ca_cert()
        ca_key_bytes = key_manager.load_ca_key()
        ca_key = serialization.load_pem_private_key(ca_key_bytes, password=None)

        if status == "good":
            cert_status = ocsp.OCSPCertStatus.GOOD
            revocation_time = None
            revocation_reason = None
        elif status == "revoked":
            cert_status = ocsp.OCSPCertStatus.REVOKED
            # Usually queried from DB; placeholder here for structure
            revocation_time = datetime.datetime.utcnow() 
            revocation_reason = x509.ReasonFlags.unspecified
        else:
            cert_status = ocsp.OCSPCertStatus.UNKNOWN
            revocation_time = None
            revocation_reason = None

        builder = (
            ocsp.OCSPResponseBuilder()
            .add_response(
                cert=None, # In a fully wired impl, provide the specific target cert
                issuer=ca_cert,
                algorithm=hashes.SHA256(),
                cert_status=cert_status,
                this_update=datetime.datetime.utcnow(),
                next_update=datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                revocation_time=revocation_time,
                revocation_reason=revocation_reason
            )
            .responder_id(ocsp.OCSPResponderEncoding.HASH, ca_cert)
        )
        response = builder.sign(ca_key, hashes.SHA256())
        return response.public_bytes(serialization.Encoding.DER)
