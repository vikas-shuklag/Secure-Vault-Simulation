# PKI System Architecture

This document describes the design implementation for upgrading the Virtual HSM to a full Public Key Infrastructure (PKI) web service.

## Core Components
1. **Virtual HSM:** The existing core logic responsible for keys. Keys stay strictly within `virtual_hsm/storage/keys.db`.
2. **PKI Layer:** An abstraction above the HSM performing X.509 issuance, CSR ingestion, revocation lists (CRL), and validation.
3. **API Gateway (FastAPI):** Exposes PKI and HSM operations over REST endpoints, protected by JWT authentication.
4. **Relational Database (PostgreSQL):** Stores certificate metadata, revocation status, and user credentials.
5. **Cache (Redis):** In-memory cache for ultra-fast OCSP responder queries.

## Key Management Boundary
- **Root CA:** Generated internally by PKI service, securely stored into `keys.db`.
- **Issued Keys:** Always generated as `AES-256` or `RSA-2048` and never exported structurally.
