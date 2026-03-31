from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routers import hsm, pki, ocsp, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("HSM PKI Service starting up...")
    yield
    print("HSM PKI Service shutting down...")

app = FastAPI(
    title="Virtual HSM + PKI Service",
    description="Software HSM with PKI capabilities — X.509 issuance, revocation, OCSP",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Expand this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(hsm.router, prefix="/api/v1/hsm", tags=["HSM Operations"])
app.include_router(pki.router, prefix="/api/v1/pki", tags=["PKI / Certificates"])
app.include_router(ocsp.router, prefix="/ocsp", tags=["OCSP responder"])

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
