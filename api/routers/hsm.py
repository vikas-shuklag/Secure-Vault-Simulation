from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from api.auth import get_current_user
from api.deps import get_db
from virtual_hsm import key_manager, crypto_service
from virtual_hsm.auth import change_password
from pki.models import IssuedCertificate

router = APIRouter()

class KeyGenRequest(BaseModel):
    label: str = ""

class KeyGenResponse(BaseModel):
    key_id: str
    type: str

class CryptoRequest(BaseModel):
    key_id: str
    data: str

class SignRequest(BaseModel):
    key_id: str
    data: str

class VerifyRequest(BaseModel):
    key_id: str
    data: str
    signature: str

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

@router.get("/stats")
async def get_stats(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Return real-time stats for the Dashboard."""
    total_certs = db.query(IssuedCertificate).count()
    revoked_certs = db.query(IssuedCertificate).filter_by(is_revoked=True).count()
    active_certs = total_certs - revoked_certs
    total_keys = key_manager.count_keys()
    return {
        "active_certificates": active_certs,
        "revoked_certificates": revoked_certs,
        "hsm_keys": total_keys
    }

@router.get("/keys")
async def get_keys(user=Depends(get_current_user)):
    """List all keys currently in the HSM."""
    keys = key_manager.list_keys()
    return {"keys": [{"id": k[0], "type": k[1], "label": k[2] if len(k) > 2 else ""} for k in keys]}

@router.post("/keys/aes", response_model=KeyGenResponse)
async def generate_aes_key(req: KeyGenRequest = KeyGenRequest(), user=Depends(get_current_user)):
    """Generate a new AES-256-GCM key inside the HSM."""
    key_id = key_manager.generate_aes_key(label=req.label)
    return {"key_id": key_id, "type": "AES-256"}

@router.post("/keys/rsa", response_model=KeyGenResponse)
async def generate_rsa_key(req: KeyGenRequest = KeyGenRequest(), user=Depends(get_current_user)):
    """Generate a new RSA-2048 keypair inside the HSM."""
    key_id = key_manager.generate_rsa_key(label=req.label)
    return {"key_id": key_id, "type": "RSA-2048"}

@router.delete("/keys/{key_id}")
async def delete_key(key_id: str, user=Depends(get_current_user)):
    """Destroy a key from the HSM vault. CA root key is protected."""
    try:
        deleted = key_manager.delete_key(key_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Key '{key_id}' not found.")
        return {"status": "destroyed", "key_id": key_id}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/crypto/encrypt")
async def encrypt_data(req: CryptoRequest, user=Depends(get_current_user)):
    """Encrypt plaintext using a stored AES key."""
    try:
        ciphertext = crypto_service.encrypt(req.key_id, req.data)
        return {"ciphertext": ciphertext}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/crypto/decrypt")
async def decrypt_data(req: CryptoRequest, user=Depends(get_current_user)):
    """Decrypt a base64 ciphertext using a stored AES key."""
    try:
        plaintext = crypto_service.decrypt(req.key_id, req.data)
        return {"plaintext": plaintext}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Decryption failed: {str(e)}")

@router.post("/crypto/sign")
async def sign_data(req: SignRequest, user=Depends(get_current_user)):
    """Sign data using a stored RSA key (RSA-PSS + SHA256)."""
    try:
        signature = crypto_service.sign(req.key_id, req.data)
        return {"signature": signature}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/crypto/verify")
async def verify_signature(req: VerifyRequest, user=Depends(get_current_user)):
    """Verify an RSA-PSS signature using a stored RSA key."""
    try:
        valid = crypto_service.verify(req.key_id, req.data, req.signature)
        return {"valid": valid}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/admin/password")
async def rotate_password(req: PasswordChangeRequest, user=Depends(get_current_user)):
    """Rotate the Admin Password of the HSM."""
    if change_password(req.old_password, req.new_password):
        return {"status": "success", "message": "Password changed successfully."}
    raise HTTPException(status_code=401, detail="Old password is incorrect.")
