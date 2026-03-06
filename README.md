# Virtual HSM — Hardware Security Module Simulation

A **Virtual Hardware Security Module (HSM)** that simulates real HSM behavior where cryptographic keys never leave the module boundary and applications request cryptographic operations through a secure API.

> Built for security hackathon demonstrations.

---

## Overview

A Hardware Security Module is a dedicated hardware device for managing cryptographic keys and performing crypto operations. This project simulates that architecture in software:

- **Keys never leave the HSM** — only operation results (ciphertext, signatures) are returned
- **All crypto operations** happen inside the module boundary
- **Policy engine** controls which operations are permitted
- **Authentication** is required before accessing any HSM function
- **Tkinter GUI dashboard** for easy interaction and demo

---

## Architecture

```
GUI Dashboard (gui.py)
        ↓
   HSM Core (hsm_core.py)
        ├── Authentication    (auth.py)
        ├── Policy Engine     (policy_engine.py)
        ├── Key Manager       (key_manager.py)
        └── Crypto Service    (crypto_service.py)
              ↓
      Secure Key Store (storage/keys.db)
```

---

## Project Structure

```
Virtual_HSM/
├── README.md
├── requirements.txt
├── .gitignore
│
├── virtual_hsm/
│   ├── __init__.py
│   ├── __main__.py           # Entry point for python -m
│   ├── main.py               # Launches GUI
│   ├── gui.py                # Tkinter dashboard
│   ├── hsm_core.py           # Central HSM controller
│   ├── auth.py               # SHA-256 authentication
│   ├── key_manager.py        # Key generation & storage
│   ├── crypto_service.py     # AES-GCM & RSA-PSS operations
│   ├── policy_engine.py      # Operation policy rules
│   │
│   └── storage/
│       └── keys.db           # SQLite key store (auto-created)
│
└── .venv/
```

---

## Modules

| Module | Responsibility |
|--------|---------------|
| `gui.py` | Tkinter GUI dashboard with dark theme |
| `auth.py` | SHA-256 password authentication |
| `key_manager.py` | AES-256 / RSA-2048 key generation, SQLite storage |
| `crypto_service.py` | AES-GCM encrypt/decrypt, RSA-PSS sign/verify |
| `policy_engine.py` | Rule-based operation access control |
| `hsm_core.py` | Central controller — enforces policy, delegates operations |
| `main.py` | Entry point — launches the GUI |

---

## Installation

```bash
# Clone the repository
git clone https://github.com/ShadowTracker13/Virtual_HSM.git
cd Virtual_HSM

# Create virtual environment
python3 -m venv .venv
for kali: source .venv/bin/activate
for windows:  .venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Launching the GUI

```bash
source .venv/bin/activate
or 
.venv\Scripts\Activate.ps1

python3 -m virtual_hsm.main
```

This opens the **Virtual HSM Dashboard** — a dark-themed Tkinter interface.

---

### Step 1 — Authentication

When the app launches, you'll see a login screen.

- Enter the default password: `admin123`
- Click **AUTHENTICATE** or press Enter
- On success, the dashboard loads

---

### Step 2 — Generate Keys

Use the **🔑 Key Generation** section:

| Button | What it does |
|--------|-------------|
| **Generate AES Key** | Creates a 256-bit AES key inside the HSM. Returns a key ID (e.g. `aes-8fcd25653335`) |
| **Generate RSA Key** | Creates a 2048-bit RSA key pair inside the HSM. Returns a key ID (e.g. `rsa-2338d92ef6f6`) |

> ⚠️ The key material is **never displayed**. Only the key ID is shown. Copy the key ID for later use.

---

### Step 3 — Encrypt / Decrypt Data

Use the **🔒 Encrypt / Decrypt** section:

1. **Encrypt:**
   - Paste your **AES Key ID** in the Key ID field
   - Type your plaintext in the Data field
   - Click **Encrypt**
   - The encrypted ciphertext (base64) appears in the Output Log

2. **Decrypt:**
   - Paste your **AES Key ID** in the Key ID field
   - Paste the **ciphertext** (from the Output Log) in the Data field
   - Click **Decrypt**
   - The original plaintext appears in the Output Log

---

### Step 4 — Sign / Verify Data

Use the **✍️ Sign / Verify** section:

1. **Sign:**
   - Paste your **RSA Key ID** in the Key ID field
   - Type the data to sign in the Data field
   - Click **Sign Data**
   - The signature auto-fills the Signature field and appears in the Output Log

2. **Verify:**
   - Keep the same RSA Key ID, Data, and Signature
   - Click **Verify Signature**
   - A popup confirms whether the signature is **VALID** or **INVALID**

---

### Output Log

The scrollable **📋 Output Log** at the bottom shows all operation results:
- 🔑 Key generation events
- ✓ Successful encryptions, decryptions, signatures
- ✗ Errors and failed verifications

All results are displayed here — this is your audit trail.

---

### Demo Workflow (Quick Reference)

| Step | Action | Result |
|------|--------|--------|
| 1 | Launch app | Login screen appears |
| 2 | Enter `admin123` | Dashboard loads |
| 3 | Click **Generate AES Key** | Key ID returned (e.g. `aes-...`) |
| 4 | Enter Key ID + plaintext → **Encrypt** | Ciphertext in Output Log |
| 5 | Enter Key ID + ciphertext → **Decrypt** | Original plaintext recovered |
| 6 | Click **Generate RSA Key** | Key ID returned (e.g. `rsa-...`) |
| 7 | Enter Key ID + data → **Sign Data** | Signature generated |
| 8 | Click **Verify Signature** | ✓ VALID confirmation |

---

## Security Model

- 🔒 **Keys never leave the HSM** — only key IDs are returned to the user
- 🔐 **AES-256-GCM** for authenticated encryption
- ✍️ **RSA-2048 PSS** for digital signatures
- 🛡️ **Policy engine** prevents unauthorized operations
- 🔑 **SQLite key store** — keys stored as BLOBs, never printed or exported

---

## Technologies

- Python 3
- `tkinter` — GUI dashboard
- `cryptography` — AES-GCM, RSA-PSS
- `sqlite3` — Secure key storage
- `hashlib` — SHA-256 authentication

---

## License

MIT
