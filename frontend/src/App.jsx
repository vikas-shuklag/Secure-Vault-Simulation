import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { Shield, Key, FileSignature, Settings, Activity } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Certificates from './pages/Certificates';

function App() {
  return (
    <Router>
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
              <Settings size={20} /> Settings
            </NavLink>
          </div>
        </nav>

        {/* Main Content Area */}
        <main className="main-content fade-in">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/certificates" element={<Certificates />} />
            {/* Fallback routes for demo */}
            <Route path="/keys" element={<div><h2>HSM Keys</h2><p>Coming Soon</p></div>} />
            <Route path="/settings" element={<div><h2>Settings</h2><p>Coming Soon</p></div>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
