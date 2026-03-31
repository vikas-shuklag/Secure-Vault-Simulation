from fastapi import APIRouter, Request, Response, Depends
import base64
from sqlalchemy.orm import Session
from api.deps import get_db

router = APIRouter()

@router.get("/{request_b64}")
@router.post("/")
async def ocsp_endpoint(
    request: Request, 
    request_b64: str = None,
    db: Session = Depends(get_db)
):
    """
    OCSP Responder — RFC 6960 compliant.
        GET:  /ocsp/<base64-encoded-request>
        POST: /ocsp/ with DER body
    """
    if request_b64:
        try:
            ocsp_req_der = base64.b64decode(request_b64)
        except Exception:
             return Response(status_code=400, content="Invalid base64 payload")
    else:
        ocsp_req_der = await request.body()
        if not ocsp_req_der:
             return Response(status_code=400, content="Missing OCSP request body")

    # In a full phase 4 implementation, this connects to `pki.ocsp_service`
    # For now, return a placeholder until the ocsp_service is written in the next commit
    return Response(
        content=b"Placeholder OCSP Response bytes",
        media_type="application/ocsp-response",
        headers={"Cache-Control": "max-age=3600"}
    )
