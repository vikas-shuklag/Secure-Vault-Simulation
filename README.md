# Virtual HSM - Hardware Security Module Simulation

A Python-based Virtual Hardware Security Module (HSM) for hackathon demos.

It simulates real HSM behavior where keys stay inside the module boundary and applications request cryptographic operations through an API surface.

## Overview

This project demonstrates core HSM concepts in software:

- Keys never leave the HSM boundary
- Encryption, decryption, signing, and verification are performed internally
- A policy engine gates allowed operations
- Authentication is required before HSM operations
- A Tkinter GUI provides an interactive dashboard

## Architecture

```text
GUI (gui.py)
   |
   v
HSM Core (hsm_core.py)
   |- Authentication service (auth.py)
   |- Policy engine (policy_engine.py)
   |- Key manager (key_manager.py)
   |- Crypto service (crypto_service.py)
   |
   v
Secure storage (virtual_hsm/storage/keys.db, auth.json)
```

## Project Structure

```text
Virtual_HSM/
|- README.md
|- requirements.txt
|- .gitignore
|- tests/
|  |- test_hsm_core.py
|- virtual_hsm/
   |- __init__.py
   |- __main__.py
   |- main.py
   |- gui.py
   |- hsm_core.py
   |- auth.py
   |- key_manager.py
   |- crypto_service.py
   |- policy_engine.py
   |- storage/
      |- keys.db      (runtime, ignored)
      |- auth.json    (runtime, ignored)
```

## Modules

| Module | Responsibility |
| --- | --- |
| `gui.py` | Tkinter dashboard and user interactions |
| `hsm_core.py` | Central API boundary, auth enforcement, policy checks |
| `auth.py` | Password verification and rotation using salted PBKDF2 |
| `key_manager.py` | AES/RSA key generation and SQLite persistence |
| `crypto_service.py` | AES-GCM encrypt/decrypt and RSA-PSS sign/verify |
| `policy_engine.py` | Operation allow/deny policy table |

## Security Features

- Authenticated HSM session required before operations
- Login rate limiting in GUI (temporary lockout after repeated failures)
- Password rotation action in admin section
- AES-256-GCM for encryption/decryption
- RSA-2048 with PSS + SHA-256 for signatures
- Policy-gated operations (`generate_key`, `encrypt`, `decrypt`, `sign`, `verify`, `list_keys`, `rotate_password`)

## Installation

```bash
git clone https://github.com/ShadowTracker13/Virtual_HSM.git
cd Virtual_HSM

python -m venv .venv
```

Activate environment:

- Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

- Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python -m virtual_hsm
```

Default bootstrap password: `admin123`

## Usage Flow

1. Launch app and authenticate.
2. Generate AES or RSA key IDs from the dashboard.
3. Use AES key ID for encrypt/decrypt operations.
4. Use RSA key ID for sign/verify operations.
5. Use the Admin section to rotate password when needed.

## Testing

Run unit tests:

```bash
python -m unittest discover -s tests -v
```

Current suite covers:

- auth-required behavior on core operations
- AES roundtrip
- RSA sign/verify roundtrip
- password rotation and re-auth behavior

## Git Hygiene

Runtime files are intentionally ignored and should never be committed:

- `virtual_hsm/storage/keys.db`
- `virtual_hsm/storage/auth.json`

## License

MIT
