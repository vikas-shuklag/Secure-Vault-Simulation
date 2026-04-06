import React, { useState } from 'react';
import axios from 'axios';
import { Download, ShieldAlert, KeyRound } from 'lucide-react';

export default function Settings() {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  const handleDownloadRoot = async () => {
    try {
      // Using browser fetch to trigger download instead of axios
      const response = await fetch('https://virtual-hsm-api.onrender.com/api/v1/pki/ca/certificate');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'ca_root.crt');
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (err) {
      console.error('Download failed', err);
      setMessage({ text: 'Failed to download Root CA', type: 'error' });
    }
  };

  const handlePasswordReset = async (e) => {
    e.preventDefault();
    if (!oldPassword || !newPassword) {
      setMessage({ text: 'Both passwords are required', type: 'error'});
      return;
    }
    if (newPassword.length < 8) {
      setMessage({ text: 'New password must be at least 8 characters long.', type: 'error'});
      return;
    }

    setLoading(true);
    setMessage({ text: '', type: ''});

    try {
      await axios.post('/api/v1/hsm/admin/password', {
        old_password: oldPassword,
        new_password: newPassword
      });
      setMessage({ text: 'Password successfully updated! You will need to use it on your next login.', type: 'success' });
      setOldPassword('');
      setNewPassword('');
    } catch (err) {
       if (err.response && err.response.data && err.response.data.detail) {
        setMessage({ text: err.response.data.detail, type: 'error' });
      } else {
        setMessage({ text: 'Failed to update password', type: 'error' });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ animationDelay: '0.1s' }} className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1>Administration Settings</h1>
          <p>Global Virtual HSM configurations</p>
        </div>
      </div>

      <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))' }}>
        
        {/* Root CA Panel */}
        <div className="glass-panel">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
            <ShieldAlert size={20} color="var(--accent-primary)" /> Trust Architecture
          </h2>
          <p className="stat-label" style={{ marginBottom: '20px' }}>
            Download the Virtual HSM Root Certificate Authority (CA) to establish a chain of trust on local devices.
          </p>
          
          <button 
            className="btn btn-success" 
            onClick={handleDownloadRoot}
            style={{ padding: '12px 24px' }}
          >
            <Download size={16} /> Download Root CA
          </button>
        </div>

        {/* Password Panel */}
        <div className="glass-panel" style={{ borderColor: 'rgba(239, 68, 68, 0.3)'}}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
            <KeyRound size={20} color="var(--danger)" /> Security Credentials
          </h2>
          <p className="stat-label" style={{ marginBottom: '20px' }}>
            Rotate the master administrative password used for the Virtual HSM.
          </p>
          
          <form onSubmit={handlePasswordReset}>
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-muted)' }}>Old Password</label>
              <input
                type="password"
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                style={{
                  width: '100%', padding: '12px', borderRadius: '8px',
                  border: '1px solid rgba(255, 255, 255, 0.1)', background: 'rgba(0, 0, 0, 0.2)',
                  color: 'white', outline: 'none'
                }}
              />
            </div>
            <div style={{ marginBottom: '24px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-muted)' }}>New Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                style={{
                  width: '100%', padding: '12px', borderRadius: '8px',
                  border: '1px solid rgba(255, 255, 255, 0.1)', background: 'rgba(0, 0, 0, 0.2)',
                  color: 'white', outline: 'none'
                }}
              />
            </div>

            {message.text && (
              <p style={{ color: message.type === 'error' ? 'var(--danger)' : 'var(--success)', marginBottom: '16px', fontSize: '0.9rem' }}>
                {message.text}
              </p>
            )}

            <button 
              type="submit" 
              className="btn btn-danger" 
              disabled={loading}
              style={{ width: '100%', padding: '12px', justifyContent: 'center' }}
            >
              {loading ? 'Processing...' : 'Change Password'}
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}
