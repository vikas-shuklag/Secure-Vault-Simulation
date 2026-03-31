import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Key, Lock, Unlock, Plus, Tag, Trash2, FileSignature, CheckCircle, XCircle } from 'lucide-react';

export default function HSMKeys() {
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Key generation form state
  const [aesLabel, setAesLabel] = useState('');
  const [rsaLabel, setRsaLabel] = useState('');
  
  // Crypto form state
  const [encKeyId, setEncKeyId] = useState('');
  const [encData, setEncData] = useState('');
  const [encResult, setEncResult] = useState('');
  const [encError, setEncError] = useState('');

  // Sign/Verify form state
  const [signKeyId, setSignKeyId] = useState('');
  const [signData, setSignData] = useState('');
  const [signature, setSignature] = useState('');
  const [verifyResult, setVerifyResult] = useState(null); // null | true | false
  const [signError, setSignError] = useState('');

  const fetchKeys = async () => {
    try {
      const response = await axios.get('/api/v1/hsm/keys');
      setKeys(response.data.keys);
    } catch (err) {
      console.error("Failed to fetch keys", err);
    }
  };

  useEffect(() => { fetchKeys(); }, []);

  const generateKey = async (type, label) => {
    setLoading(true);
    try {
      await axios.post(`/api/v1/hsm/keys/${type.toLowerCase()}`, { label });
      await fetchKeys();
      if (type === 'AES') setAesLabel('');
      if (type === 'RSA') setRsaLabel('');
    } catch (err) {
      console.error(`Failed to generate ${type} key`, err);
    } finally {
      setLoading(false);
    }
  };

  const deleteKey = async (keyId) => {
    if (!window.confirm(`⚠ Permanently destroy key "${keyId}"? This cannot be undone.`)) return;
    try {
      await axios.delete(`/api/v1/hsm/keys/${keyId}`);
      await fetchKeys();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Deletion failed';
      alert(detail);
    }
  };

  // ─── Encrypt / Decrypt ─────────────────────────
  const handleCrypto = async (operation) => {
    if (!encKeyId || !encData) { setEncError('Key ID and Data are required.'); return; }
    setEncError(''); setEncResult(''); setLoading(true);
    try {
      const response = await axios.post(`/api/v1/hsm/crypto/${operation}`, { key_id: encKeyId, data: encData });
      setEncResult(operation === 'encrypt' ? response.data.ciphertext : response.data.plaintext);
    } catch (err) {
      setEncError(err.response?.data?.detail || `Failed to ${operation}`);
    } finally { setLoading(false); }
  };

  // ─── Sign ──────────────────────────────────────
  const handleSign = async () => {
    if (!signKeyId || !signData) { setSignError('Key ID and Data are required.'); return; }
    setSignError(''); setSignature(''); setVerifyResult(null); setLoading(true);
    try {
      const response = await axios.post('/api/v1/hsm/crypto/sign', { key_id: signKeyId, data: signData });
      setSignature(response.data.signature);
    } catch (err) {
      setSignError(err.response?.data?.detail || 'Signing failed');
    } finally { setLoading(false); }
  };

  // ─── Verify ────────────────────────────────────
  const handleVerify = async () => {
    if (!signKeyId || !signData || !signature) { setSignError('Key ID, Data, and Signature are all required.'); return; }
    setSignError(''); setVerifyResult(null); setLoading(true);
    try {
      const response = await axios.post('/api/v1/hsm/crypto/verify', { key_id: signKeyId, data: signData, signature });
      setVerifyResult(response.data.valid);
    } catch (err) {
      setSignError(err.response?.data?.detail || 'Verification failed');
    } finally { setLoading(false); }
  };

  const inputStyle = {
    width: '100%', padding: '12px', borderRadius: '8px',
    border: '1px solid rgba(255, 255, 255, 0.1)', background: 'rgba(0, 0, 0, 0.2)',
    color: 'white', outline: 'none', fontFamily: 'monospace'
  };

  return (
    <div style={{ animationDelay: '0.1s' }} className="fade-in">
      <div style={{ marginBottom: '24px' }}>
        <h1>Hardware Security Module</h1>
        <p>Key Generation, Cryptographic Operations, and Digital Signing</p>
      </div>

      {/* ═══ Row 1: Key Generation ═══ */}
      <div className="glass-panel" style={{ marginBottom: '24px' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
          <Key size={20} color="var(--accent-primary)" /> Key Generation
        </h2>
        <p className="stat-label" style={{ marginBottom: '20px' }}>
          Generate keys directly inside the HSM boundary. Assign a label to track what each key is used for.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          {/* AES */}
          <div style={{ padding: '16px', background: 'rgba(0,0,0,0.15)', borderRadius: '8px', border: '1px solid rgba(59, 185, 80, 0.2)' }}>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 600 }}>AES-256-GCM (Symmetric Encryption)</p>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <Tag size={14} color="var(--text-muted)" />
              <input type="text" placeholder="Label (e.g. DB Encryption)" value={aesLabel} onChange={(e) => setAesLabel(e.target.value)}
                style={{ ...inputStyle, fontFamily: 'inherit', flex: 1 }} />
              <button className="btn btn-success" onClick={() => generateKey('AES', aesLabel)} disabled={loading} style={{ padding: '10px 16px', whiteSpace: 'nowrap' }}>
                <Plus size={14} /> Generate
              </button>
            </div>
          </div>
          {/* RSA */}
          <div style={{ padding: '16px', background: 'rgba(0,0,0,0.15)', borderRadius: '8px', border: '1px solid rgba(188, 140, 255, 0.2)' }}>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 600 }}>RSA-2048 (Asymmetric Signing)</p>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <Tag size={14} color="var(--text-muted)" />
              <input type="text" placeholder="Label (e.g. Code Signing)" value={rsaLabel} onChange={(e) => setRsaLabel(e.target.value)}
                style={{ ...inputStyle, fontFamily: 'inherit', flex: 1 }} />
              <button className="btn" onClick={() => generateKey('RSA', rsaLabel)} disabled={loading} style={{ padding: '10px 16px', whiteSpace: 'nowrap', background: 'var(--accent-secondary)' }}>
                <Plus size={14} /> Generate
              </button>
            </div>
          </div>
        </div>

        {/* Stored Keys Table */}
        <div style={{ marginTop: '24px' }}>
          <h3 style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>Stored Keys ({keys.length})</h3>
          <div style={{ maxHeight: '240px', overflowY: 'auto' }}>
            {keys.length === 0 ? (
              <p className="stat-label">No keys found in HSM.</p>
            ) : (
              <table className="data-table" style={{ marginTop: 0 }}>
                <thead>
                  <tr>
                    <th>Key ID</th>
                    <th>Label</th>
                    <th>Type</th>
                    <th style={{ textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {keys.map((k, idx) => (
                    <tr key={idx}>
                      <td style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: 'var(--accent-primary)' }}>{k.id}</td>
                      <td style={{ color: k.label ? 'var(--text-secondary)' : 'var(--text-muted)', fontStyle: k.label ? 'normal' : 'italic', fontSize: '0.85rem' }}>
                        {k.label || 'No label'}
                      </td>
                      <td>
                        <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: '#e2e8f0', border: '1px solid rgba(255,255,255,0.1)'}}>{k.type}</span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          className="btn btn-danger"
                          style={{ padding: '4px 10px', fontSize: '0.8rem' }}
                          onClick={() => deleteKey(k.id)}
                          title="Destroy Key"
                        >
                          <Trash2 size={14} /> Destroy
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>

      {/* ═══ Row 2: Crypto Operations ═══ */}
      <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))' }}>

        {/* Encrypt / Decrypt Panel */}
        <div className="glass-panel">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
            <Lock size={20} color="var(--success)" /> AES Encrypt / Decrypt
          </h2>
          <p className="stat-label" style={{ marginBottom: '16px' }}>Use an AES-256-GCM key for authenticated symmetric encryption.</p>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '6px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>AES Key ID</label>
            <input type="text" placeholder="aes-xxxxxxxxxxxx" value={encKeyId} onChange={(e) => setEncKeyId(e.target.value)} style={inputStyle} />
          </div>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '6px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>Data</label>
            <textarea placeholder="Plaintext to encrypt, or Base64 ciphertext to decrypt" value={encData} onChange={(e) => setEncData(e.target.value)} rows={3} style={{ ...inputStyle, resize: 'vertical' }} />
          </div>
          {encError && <p style={{ color: 'var(--danger)', marginBottom: '12px', fontSize: '0.85rem' }}>{encError}</p>}
          <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
            <button className="btn btn-success" onClick={() => handleCrypto('encrypt')} disabled={loading} style={{ flex: 1, padding: '10px', justifyContent: 'center' }}>
              <Lock size={14} /> Encrypt
            </button>
            <button className="btn" onClick={() => handleCrypto('decrypt')} disabled={loading} style={{ flex: 1, padding: '10px', justifyContent: 'center', background: 'var(--warning)', color: '#000' }}>
              <Unlock size={14} /> Decrypt
            </button>
          </div>
          {encResult && (
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', border: '1px solid rgba(59,185,80,0.3)' }}>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: '6px' }}>Result:</p>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-all', color: 'var(--text-primary)', fontFamily: 'monospace', fontSize: '0.85rem' }}>{encResult}</pre>
            </div>
          )}
        </div>

        {/* Sign / Verify Panel */}
        <div className="glass-panel">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
            <FileSignature size={20} color="var(--accent-secondary)" /> RSA Sign / Verify
          </h2>
          <p className="stat-label" style={{ marginBottom: '16px' }}>Use an RSA-2048 key for RSA-PSS digital signatures (SHA-256).</p>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '6px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>RSA Key ID</label>
            <input type="text" placeholder="rsa-xxxxxxxxxxxx" value={signKeyId} onChange={(e) => setSignKeyId(e.target.value)} style={inputStyle} />
          </div>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '6px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>Data to Sign</label>
            <textarea placeholder="Enter data to sign or verify" value={signData} onChange={(e) => setSignData(e.target.value)} rows={2} style={{ ...inputStyle, resize: 'vertical' }} />
          </div>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '6px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>Signature (Base64)</label>
            <textarea placeholder="Generated signature will appear here, or paste to verify" value={signature} onChange={(e) => setSignature(e.target.value)} rows={2} style={{ ...inputStyle, resize: 'vertical' }} />
          </div>
          {signError && <p style={{ color: 'var(--danger)', marginBottom: '12px', fontSize: '0.85rem' }}>{signError}</p>}
          <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
            <button className="btn" onClick={handleSign} disabled={loading} style={{ flex: 1, padding: '10px', justifyContent: 'center', background: 'var(--accent-secondary)' }}>
              <FileSignature size={14} /> Sign Data
            </button>
            <button className="btn" onClick={handleVerify} disabled={loading} style={{ flex: 1, padding: '10px', justifyContent: 'center', background: 'var(--accent-primary)' }}>
              <CheckCircle size={14} /> Verify Signature
            </button>
          </div>
          {verifyResult !== null && (
            <div style={{
              padding: '14px', borderRadius: '8px',
              background: verifyResult ? 'rgba(59,185,80,0.1)' : 'rgba(248,81,73,0.1)',
              border: `1px solid ${verifyResult ? 'rgba(59,185,80,0.4)' : 'rgba(248,81,73,0.4)'}`
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {verifyResult ? <CheckCircle size={20} color="var(--success)" /> : <XCircle size={20} color="var(--danger)" />}
                <span style={{ color: verifyResult ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>
                  {verifyResult ? '✓ Signature is VALID' : '✗ Signature is INVALID'}
                </span>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
