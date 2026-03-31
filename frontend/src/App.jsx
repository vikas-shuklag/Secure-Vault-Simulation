import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom';
import { Shield, Key, FileSignature, Settings as SettingsIcon, Activity } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Certificates from './pages/Certificates';
import HSMKeys from './pages/HSMKeys';
import Settings from './pages/Settings';
import Login from './pages/Login';

// Axios instance to cleanly provide auth header to all requests
import axios from 'axios';
axios.defaults.baseURL = 'http://localhost:8000';

function AppContent({ setAuthToken }) {
  const location = useLocation();
  
  const handleLogout = () => {
    localStorage.removeItem('hsm_token');
    setAuthToken(null);
  };

  return (
    <div className="app-container">
      {/* Glassmorphism Sidebar */}
      <nav className="sidebar">
        <NavLink to="/" className="sidebar-brand">
          <Shield size={28} color="var(--accent-primary)" />
          Secure Vault
        </NavLink>
        
        <div style={{ marginTop: '32px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <NavLink to="/dashboard" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
            <Activity size={20} /> Dashboard
          </NavLink>
          <NavLink to="/certificates" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
            <FileSignature size={20} /> PKI Certificates
          </NavLink>
          <NavLink to="/keys" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
            <Key size={20} /> HSM Keys
          </NavLink>
          <NavLink to="/settings" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
            <SettingsIcon size={20} /> Settings
          </NavLink>
        </div>

        <div style={{ marginTop: 'auto', marginBottom: '16px' }}>
          <button className="nav-link" style={{ width: '100%', textAlign: 'left', background: 'transparent', border: 'none', cursor: 'pointer' }} onClick={handleLogout}>
            Sign Out
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="main-content fade-in">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/certificates" element={<Certificates />} />
          <Route path="/keys" element={<HSMKeys />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  const [authToken, setAuthToken] = useState(localStorage.getItem('hsm_token'));

  useEffect(() => {
    if (authToken) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [authToken]);

  if (!authToken) {
    return <Login setAuthToken={setAuthToken} />;
  }

  return (
    <Router>
      <AppContent setAuthToken={setAuthToken} />
    </Router>
  );
}

export default App;
