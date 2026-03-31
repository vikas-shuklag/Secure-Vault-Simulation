from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from api.auth import create_access_token
from virtual_hsm.auth import verify_password

router = APIRouter()

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # We ignore the username completely and just check if the HSM password matches
    if not verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Normally, you'd include the username or ID in the token's 'sub' field. 
    # For this simulation, we'll just put "admin".
    access_token = create_access_token(data={"sub": "admin"})
    return {"access_token": access_token, "token_type": "bearer"}
