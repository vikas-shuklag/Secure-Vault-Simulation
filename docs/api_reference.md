# API Reference Planning

## Authentication
All endpoints (except OCSP) expect a Bearer Token attached to the `Authorization` header.

## Primary Routes
### HSM Core (`/api/v1/hsm`)
- `POST /keys/aes` -> Generate AES 256
- `POST /keys/rsa` -> Generate RSA 2048
- `GET /keys` -> List existing keys
- `POST /crypto/encrypt` -> Provide `key_id` and `data`
- `POST /crypto/decrypt` -> Provide `key_id` and `token`

### PKI Service (`/api/v1/pki`)
- `GET /ca/certificate` -> Download the Root CA (PEM)
- `POST /certificates/issue` -> Upload `.csr` file to receive signed cert
- `POST /certificates/{serial}/revoke` -> Mark a certificate as revoked
- `GET /crl` -> Download latest Revocation List (DER)

### OCSP (`/ocsp`)
- `GET /{request_b64}`
- `POST /` -> Standard RFC 6960 endpoint for live queries
