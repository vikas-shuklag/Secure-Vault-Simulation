from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.auth import get_current_user
from virtual_hsm import key_manager, crypto_service

router = APIRouter()

class KeyGenResponse(BaseModel):
    key_id: str
    type: str

class CryptoRequest(BaseModel):
    key_id: str
    data: str

@router.get("/keys")
async def get_keys(user=Depends(get_current_user)):
    """List all keys currently in the HSM."""
    keys = key_manager.list_keys()
    return {"keys": [{"id": k[0], "type": k[1]} for k in keys]}

@router.post("/keys/aes", response_model=KeyGenResponse)
async def generate_aes_key(user=Depends(get_current_user)):
    """Generate a new AES-256-GCM key inside the HSM."""
    key_id = key_manager.generate_aes_key()
    return {"key_id": key_id, "type": "AES-256"}

@router.post("/keys/rsa", response_model=KeyGenResponse)
async def generate_rsa_key(user=Depends(get_current_user)):
    """Generate a new RSA-2048 keypair inside the HSM."""
    key_id = key_manager.generate_rsa_key()
    return {"key_id": key_id, "type": "RSA-2048"}

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
