# Hardware-Inspired Secure Storage Using Software-Based Trust Architecture

## Overview

This project implements a **secure storage system inspired by hardware security modules (TPM/HSM)** using a **software-based trust architecture**.
The goal is to demonstrate how secure key management, encrypted storage, and firmware integrity verification can be implemented without dedicated hardware.

The system protects sensitive information such as **cryptographic keys, API tokens, and firmware data** by encrypting them and storing them inside a secure vault.

This project was developed for the **SanDisk Hackathon – FUTURE-X Team**.

---

# System Architecture

```
                User / Application
                        │
                        ▼
                CLI Interface (main.py)
                        │
                        ▼
                Authentication Module
                   (auth.py)
                        │
                        ▼
                 Root of Trust
               (root_of_trust.py)
                        │
                        ▼
                 Crypto Engine
               (crypto_engine.py)
                        │
                        ▼
                 Secure Vault
               (secure_vault.py)
                        │
                        ▼
                 Encrypted Storage
                storage/vault.enc
```

Additional module:

```
firmware_check.py → Firmware integrity verification
```

---

# Features

* Secure authentication using **SHA-256 password hashing**
* **AES-256 encryption** for secure data storage
* Software-based **Root of Trust**
* **Encrypted secret vault**
* **Firmware integrity verification using SHA-256**
* Secure key generation and management

---

# Project Structure

```
secure_storage_system/

auth.py
crypto_engine.py
firmware_check.py
main.py
root_of_trust.py
secure_vault.py

keys/
   master.key

storage/
   vault.enc
   firmware.bin
```

---

# Module Description

### main.py

Entry point of the system.
Provides the CLI interface for storing and retrieving secrets.

### auth.py

Handles system authentication using SHA-256 hashed passwords.

### crypto_engine.py

Implements encryption and decryption using the **cryptography** library.

### secure_vault.py

Manages secure storage and retrieval of encrypted secrets.

### root_of_trust.py

Implements a basic root-of-trust verification system.

### firmware_check.py

Simulates firmware integrity verification using SHA-256 hashing.

---

# Installation

### 1. Clone or download the project

```
git clone <repository-url>
cd secure_storage_system
```

### 2. Create a virtual environment

```
python3 -m venv .venv
```

### 3. Activate the virtual environment

Mac/Linux

```
source .venv/bin/activate
```

Windows

```
.venv\Scripts\activate
```

### 4. Install dependencies

```
pip install cryptography
```

---

# Running the Project

Run the program using:

```
python main.py
```

Example output:

```
Enter system password: admin123

Secure Storage System
1 Store Secret
2 Retrieve Secret
3 Exit
```

---

# Usage

### Store Secret

Encrypts sensitive data and stores it securely in the encrypted vault.

### Retrieve Secret

Decrypts and retrieves stored data from the secure vault.

---

# Security Concepts Demonstrated

* Secure password hashing
* Encryption-based secure storage
* Software-based trust architecture
* Firmware integrity verification
* Secure key management

---

# Example Use Cases

* Secure storage for IoT devices
* Embedded system firmware protection
* Secure key storage
* Cloud edge device security

---

# Future Improvements

* Hardware-backed key storage
* Secure enclave simulation
* Device binding and key sealing
* Secure boot implementation
* Remote attestation

---

# Team

**Team Name:** FUTURE-X
**Hackathon:** SanDisk Hackathon

---

# License

This project is intended for **educational and research purposes**.
