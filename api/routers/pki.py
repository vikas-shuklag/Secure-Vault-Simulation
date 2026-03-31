from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.deps import get_db
from pki.pki_service import PKIService
from pki.models import IssuedCertificate
from virtual_hsm.key_manager import load_ca_key
from cryptography.hazmat.primitives import serialization

router = APIRouter()

class CertificateRequest(BaseModel):
    common_name: str
    cert_type: str = "tls_server"
    validity_days: int = 365
    san_dns: list[str] = []
    san_ip: list[str] = []

@router.get("/ca/certificate")
async def get_ca_cert():
    """Download the Root CA certificate (PEM). No Auth required."""
    try:
        pki_service = PKIService(db_session=None)
        ca_cert = pki_service.load_ca_cert()
        ca_cert_pem = ca_cert.public_bytes(serialization.Encoding.PEM)
        return Response(content=ca_cert_pem, media_type="application/x-pem-file")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/certificates")
async def list_certificates(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """List all issued certificates from the database."""
    certs = db.query(IssuedCertificate).order_by(IssuedCertificate.id.desc()).all()
    return {"certificates": [{
        "id": c.id,
        "serial": c.serial,
        "commonName": c.common_name,
        "type": c.cert_type,
        "expires": c.expires_at.strftime("%Y-%m-%d"),
        "status": "revoked" if c.is_revoked else "active",
        "revoke_reason": c.revoke_reason
    } for c in certs]}

@router.post("/certificates/issue")
async def issue_certificate(
    cert_type: str = "tls_server",
    validity_days: int = 365,
    csr_file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Issue an X.509 certificate from a CSR file."""
    try:
        csr_pem = await csr_file.read()
        pki_service = PKIService(db_session=db)
        cert = pki_service.issue_certificate(csr_pem, cert_type, validity_days)
        cert_pem = cert.public_bytes(serialization.Encoding.PEM)
        return Response(
            content=cert_pem, 
            media_type="application/x-pem-file",
            headers={"X-Serial-Number": str(cert.serial_number)}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/certificates/{serial}/revoke")
async def revoke_certificate(
    serial: str,
    reason: str = "unspecified",
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a certificate by serial number."""
    pki_service = PKIService(db_session=db)
    try:
        pki_service.revoke_certificate(serial, reason)
        return {"status": "revoked", "serial": serial}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
