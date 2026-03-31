import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ShieldCheck, Server, AlertOctagon, Info, Lock, Key, FileSignature, Cpu } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({
    issued: 0,
    revoked: 0,
    activeKeys: 0
  });
  const [apiOnline, setApiOnline] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get('/api/v1/hsm/stats');
        setStats({
          issued: response.data.active_certificates,
          revoked: response.data.revoked_certificates,
          activeKeys: response.data.hsm_keys
        });
        setApiOnline(true);
      } catch (err) {
        console.error("Failed to fetch stats:", err);
        setApiOnline(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <div style={{ animationDelay: '0.1s' }} className="fade-in">
      <h1>Security Operations Center</h1>
      <p>Real-time Virtual HSM and PKI metrics powered by Supabase PostgreSQL</p>

      <div className="stat-grid">
        <div className="glass-panel stat-card">
          <ShieldCheck size={32} color="var(--success)" style={{ marginBottom: '8px'}} />
          <div>
            <div className="stat-value">{stats.issued}</div>
            <div className="stat-label">Active Certificates</div>
          </div>
        </div>

        <div className="glass-panel stat-card">
          <Server size={32} color="var(--accent-primary)" style={{ marginBottom: '8px'}} />
          <div>
            <div className="stat-value">{stats.activeKeys}</div>
            <div className="stat-label">HSM Isolated Keys</div>
          </div>
        </div>

        <div className="glass-panel stat-card" style={{ borderColor: 'rgba(239, 68, 68, 0.3)'}}>
          <AlertOctagon size={32} color="var(--danger)" style={{ marginBottom: '8px'}} />
          <div>
            <div className="stat-value">{stats.revoked}</div>
            <div className="stat-label">Revoked via CRL</div>
          </div>
        </div>
      </div>

      <div className="glass-panel">
        <h2>System Status</h2>
        <div style={{ display: 'flex', gap: '32px', marginTop: '24px', flexWrap: 'wrap' }}>
          <div>
            <p className="stat-label">API Gateway</p>
            <span className={apiOnline ? 'badge badge-success' : 'badge badge-danger'}>
              {apiOnline ? 'Online - FastAPI' : 'Offline'}
            </span>
          </div>
          <div>
            <p className="stat-label">Hardware Module</p>
            <span className="badge badge-success">Virtual HSM Isolated</span>
          </div>
          <div>
             <p className="stat-label">Database Sync</p>
             <span className={apiOnline ? 'badge badge-success' : 'badge badge-danger'}>
               {apiOnline ? 'SQLite Connected' : 'Disconnected'}
             </span>
          </div>
          <div>
             <p className="stat-label">OCSP Responder</p>
             <span className="badge badge-success">Available</span>
          </div>
        </div>
      </div>

      {/* Educational Section: How It Works */}
      <div className="glass-panel" style={{ marginTop: '24px' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
          <Info size={20} color="var(--accent-primary)" /> How This Virtual HSM Works
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', lineHeight: '1.7' }}>
          A real Hardware Security Module (HSM) is a dedicated physical device that performs cryptographic operations
          inside tamper-resistant hardware. Private keys never leave the chip. This project <strong>simulates that exact
          boundary in software</strong>, enforcing the same architectural principle: <em>keys are generated, stored, and used
          internally — they are never exported or exposed to calling applications.</em>
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          
          <div style={{ padding: '20px', background: 'rgba(0,0,0,0.2)', borderRadius: '10px', border: '1px solid rgba(88, 166, 255, 0.15)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <Key size={18} color="var(--accent-primary)" />
              <h3 style={{ margin: 0, fontSize: '1rem' }}>Key Generation</h3>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.6', margin: 0 }}>
              <strong>AES-256-GCM</strong> keys use 32 bytes of cryptographically 
              secure random data (<code>os.urandom</code>). <strong>RSA-2048</strong> keys 
              are generated with a 65537 public exponent via the <code>cryptography</code> library. 
              All key material is stored in an isolated SQLite vault — the application only receives 
              a UUID reference, never the raw bytes.
            </p>
          </div>

          <div style={{ padding: '20px', background: 'rgba(0,0,0,0.2)', borderRadius: '10px', border: '1px solid rgba(59, 185, 80, 0.15)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <Lock size={18} color="var(--success)" />
              <h3 style={{ margin: 0, fontSize: '1rem' }}>Encryption & Decryption</h3>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.6', margin: 0 }}>
              Uses <strong>AES-256-GCM</strong> authenticated encryption with a randomly 
              generated 96-bit nonce per operation. GCM mode provides both confidentiality 
              and integrity verification. The ciphertext is returned as a Base64-encoded 
              blob containing <code>nonce || ciphertext</code>.
            </p>
          </div>

          <div style={{ padding: '20px', background: 'rgba(0,0,0,0.2)', borderRadius: '10px', border: '1px solid rgba(188, 140, 255, 0.15)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <FileSignature size={18} color="var(--accent-secondary)" />
              <h3 style={{ margin: 0, fontSize: '1rem' }}>Digital Signing</h3>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.6', margin: 0 }}>
              Utilizes <strong>RSA-PSS</strong> (Probabilistic Signature Scheme) with 
              SHA-256 hashing and MGF1 padding. PSS is the modern, more secure alternative 
              to PKCS#1 v1.5 signing. Signatures are verified against the derived 
              public key — private key never leaves the HSM.
            </p>
          </div>

          <div style={{ padding: '20px', background: 'rgba(0,0,0,0.2)', borderRadius: '10px', border: '1px solid rgba(210, 153, 34, 0.15)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <Cpu size={18} color="var(--warning)" />
              <h3 style={{ margin: 0, fontSize: '1rem' }}>PKI & X.509 Certificates</h3>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.6', margin: 0 }}>
              A self-signed <strong>Root CA</strong> (4096-bit RSA, 10-year validity) is generated 
              at initialization. Leaf certificates are issued from CSRs with proper 
              <strong> Extended Key Usage</strong> (TLS Server, Client Auth, Code Signing), 
              Subject Alternative Names, and Authority Key Identifiers. 
              Revocation is tracked via CRL status in the database.
            </p>
          </div>

        </div>
      </div>
    </div>
  );
}
