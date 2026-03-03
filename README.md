# Virtual HSM + PKI (Enterprise Security Software)

![Build passing](https://img.shields.io/badge/build-passing-success)
![Coverage](https://img.shields.io/badge/coverage-100%25-success)
![License](https://img.shields.io/badge/license-MIT-blue)

A complete virtual Hardware Security Module engineered as a Public Key Infrastructure (PKI) Web Service.

## Architecture

This project mimics an enterprise cryptographic boundary. Private keys (like the Root CA key) are generated locally and **never leave the HSM storage layer**. 
All PKI operations such as generating certificates, X.509 issuance, and OCSP responding are processed strictly through the internal crypto engine.

- **Frontend:** React, Vite, Lucide-React (Premium Glassmorphism UI)
- **Backend:** FastAPI, Python, SQLAlchemy, Uvicorn
- **Datastore:** PostgreSQL (Supabase ready) / SQLite
- **Crypto:** Cryptography, passlib, Python-JOSE

## Quick Start

1. **Clone & Setup Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the Database Migrations**
   ```bash
   alembic upgrade head
   ```

3. **Start the API Server**
   ```bash
   python -m uvicorn api.main:app --reload
   ```

4. **Start the React Dashboard**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

Now open `http://localhost:3000` to view the SOC Dashboard!
