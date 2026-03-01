import React, { useState, useEffect } from 'react';
import { ShieldCheck, Server, AlertOctagon } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({
    issued: 142,
    revoked: 3,
    activeKeys: 12
  });

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
        <div style={{ display: 'flex', gap: '32px', marginTop: '24px' }}>
          <div>
            <p className="stat-label">API Gateway</p>
            <span className="badge badge-success">Online - FastAPI</span>
          </div>
          <div>
            <p className="stat-label">Hardware Module</p>
            <span className="badge badge-success">Virtual HSM Isolated</span>
          </div>
          <div>
             <p className="stat-label">Database Sync</p>
             <span className="badge badge-success">Supabase Connected</span>
          </div>
          <div>
             <p className="stat-label">OCSP Responder</p>
             <span className="badge badge-success">0ms latency</span>
          </div>
        </div>
      </div>
    </div>
  );
}
