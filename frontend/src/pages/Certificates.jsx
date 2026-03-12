import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FilePlus, Trash2, X } from 'lucide-react';

export default function Certificates() {
  const [certs, setCerts] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [csrText, setCsrText] = useState('');
  const [certType, setCertType] = useState('tls_server');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchCertificates = async () => {
    try {
      const response = await axios.get('/api/v1/pki/certificates');
      setCerts(response.data.certificates || []);
    } catch (err) {
      console.error("Failed to fetch certificates:", err);
    }
  };

  useEffect(() => {
    fetchCertificates();
  }, []);

  const handleRevoke = async (serial) => {
    try {
      await axios.post(`/api/v1/pki/certificates/${serial}/revoke`);
      fetchCertificates();
    } catch (err) {
      console.error("Failed to revoke certificate:", err);
      alert("Revocation failed. See console for details.");
    }
  };

  const handleIssue = async (e) => {
    e.preventDefault();
    if (!csrText) {
      setError("Please paste a valid CSR block.");
      return;
    }
    setError("");
    setLoading(true);

    try {
      const formData = new FormData();
      const blob = new Blob([csrText], { type: 'text/plain' });
      formData.append('csr_file', blob, 'request.csr');
      // The FastAPI endpoint uses query params for cert_type and validity_days by default if not Form fields
      // We pass them as query params just to be safe
      
      await axios.post(`/api/v1/pki/certificates/issue?cert_type=${certType}&validity_days=365`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setShowModal(false);
      setCsrText('');
      fetchCertificates();
    } catch (err) {
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Failed to issue certificate. Ensure the CSR is valid.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ animationDelay: '0.2s' }} className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1>Certificate Issuance</h1>
          <p>X.509 PKI management interface</p>
        </div>
        <button className="btn" onClick={() => setShowModal(true)}>
          <FilePlus size={18} /> Configure New CSR
        </button>
      </div>

      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Serial Number</th>
              <th>Common Name (CN)</th>
              <th>Usage Type</th>
              <th>Expiration</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {certs.map(cert => (
              <tr key={cert.id}>
                <td style={{ fontFamily: 'monospace', color: 'var(--text-muted)' }}>{cert.serial.substring(0, 8)}...</td>
                <td style={{ fontWeight: '500', color: 'var(--text-primary)'}}>{cert.commonName}</td>
                <td><span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: '#e2e8f0', border: '1px solid rgba(255,255,255,0.1)'}}>{cert.type}</span></td>
                <td>{cert.expires}</td>
                <td>
                  <span className={cert.status === 'active' ? 'badge badge-success' : 'badge badge-danger'}>
                    {cert.status}
                  </span>
                </td>
                <td>
                  {cert.status === 'active' && (
                    <button className="btn btn-danger" style={{ padding: '6px 12px', fontSize: '0.8rem' }} onClick={() => handleRevoke(cert.serial)}>
                      <Trash2 size={14} /> Revoke
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {certs.length === 0 && (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)'}}>
            No certificates found in the PostgreSQL database.
          </div>
        )}
      </div>

      {showModal && (
        <div style={{ 
          position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', 
          background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(5px)',
          display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
        }}>
          <div className="glass-panel" style={{ width: '500px', padding: '30px', position: 'relative' }}>
            <button 
              onClick={() => setShowModal(false)}
              style={{ position: 'absolute', top: '20px', right: '20px', background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
              <X size={24} />
            </button>
            <h2 style={{ marginBottom: '20px' }}>Issue New Certificate</h2>
            
            <form onSubmit={handleIssue}>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-muted)' }}>Usage Type</label>
                <select 
                  value={certType} 
                  onChange={(e) => setCertType(e.target.value)}
                  style={{
                    width: '100%', padding: '12px', borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.1)', background: 'rgba(0, 0, 0, 0.2)',
                    color: 'white', outline: 'none'
                  }}
                >
                  <option value="tls_server">TLS Server Auth</option>
                  <option value="client">Client Auth</option>
                  <option value="code_signing">Code Signing</option>
                </select>
              </div>

              <div style={{ marginBottom: '24px' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-muted)' }}>Certificate Signing Request (PEM)</label>
                <textarea
                  placeholder="-----BEGIN CERTIFICATE REQUEST-----..."
                  value={csrText}
                  onChange={(e) => setCsrText(e.target.value)}
                  rows={8}
                  style={{
                    width: '100%', padding: '12px', borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.1)', background: 'rgba(0, 0, 0, 0.2)',
                    color: 'white', outline: 'none', resize: 'vertical', fontFamily: 'monospace'
                  }}
                />
              </div>

              {error && <p style={{ color: 'var(--danger)', marginBottom: '16px', fontSize: '0.9rem' }}>{error}</p>}

              <button 
                type="submit" 
                className="btn btn-success" 
                disabled={loading}
                style={{ width: '100%', padding: '12px', justifyContent: 'center', background: 'var(--accent-primary)' }}
              >
                {loading ? 'Issuing...' : 'Issue Certificate'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
