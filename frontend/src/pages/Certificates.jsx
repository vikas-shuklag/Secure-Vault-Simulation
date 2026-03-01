import React, { useState } from 'react';
import { FilePlus, Trash2 } from 'lucide-react';

export default function Certificates() {
  const [certs, setCerts] = useState([
    { id: 1, commonName: 'api.production.internal', type: 'tls_server', expires: '2027-01-15', status: 'active' },
    { id: 2, commonName: 'gateway-01.dmz', type: 'tls_server', expires: '2027-02-28', status: 'active' },
    { id: 3, commonName: 'legacy-app.local', type: 'tls_server', expires: '2025-10-10', status: 'revoked' },
  ]);

  return (
    <div style={{ animationDelay: '0.2s' }} className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1>Certificate Issuance</h1>
          <p>X.509 PKI management interface</p>
        </div>
        <button className="btn">
          <FilePlus size={18} /> Configure New CSR
        </button>
      </div>

      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr>
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
                    <button className="btn btn-danger" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
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
    </div>
  );
}
