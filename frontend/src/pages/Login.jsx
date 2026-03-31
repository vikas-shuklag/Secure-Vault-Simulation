import React, { useState } from 'react';
import axios from 'axios';
import { ShieldCheck } from 'lucide-react';

export default function Login({ setAuthToken }) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!password) {
      setError('Password is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // FastAPI OAuth2PasswordRequestForm expects form data
      const formData = new URLSearchParams();
      formData.append('username', 'admin'); // Ignored by backend but required by OAuth2 spec
      formData.append('password', password);

      const response = await axios.post('http://localhost:8000/api/v1/auth/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const token = response.data.access_token;
      localStorage.setItem('hsm_token', token);
      setAuthToken(token);
    } catch (err) {
      if (err.response && err.response.status === 401) {
        setError('Invalid password');
      } else {
        setError('Server connection error. Is the backend running?');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', width: '100vw' }}>
      <div className="glass-panel" style={{ width: '400px', padding: '40px', textAlign: 'center' }}>
        <ShieldCheck size={48} color="var(--accent-primary)" style={{ marginBottom: '20px' }} />
        <h2 style={{ marginBottom: '8px' }}>Virtual HSM</h2>
        <p className="stat-label" style={{ marginBottom: '32px' }}>Hardware Security Module Simulation</p>
        
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '20px', textAlign: 'left' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-muted)' }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                background: 'rgba(0, 0, 0, 0.2)',
                color: 'white',
                outline: 'none',
              }}
            />
          </div>
          
          {error && <p style={{ color: 'var(--danger)', marginBottom: '20px', fontSize: '0.9rem' }}>{error}</p>}
          
          <button 
            type="submit" 
            className="btn" 
            disabled={loading}
            style={{ width: '100%', padding: '12px', justifyContent: 'center', background: 'var(--accent-primary)' }}
          >
            {loading ? 'Authenticating...' : 'AUTHENTICATE'}
          </button>
        </form>
      </div>
    </div>
  );
}
