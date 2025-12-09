import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
    setMobileMenuOpen(false);
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-brand" onClick={closeMobileMenu}>
          <span className="brand-icon">🎯</span>
          AI Interview Assistant
        </Link>
        
        <button 
          className="mobile-menu-toggle"
          onClick={toggleMobileMenu}
          aria-label="Toggle menu"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <div className={`nav-menu ${mobileMenuOpen ? 'active' : ''}`}>
          <div className="nav-links">
            <Link 
              to="/" 
              className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              Home
            </Link>
            <Link 
              to="/download" 
              className={`nav-link ${location.pathname === '/download' ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              Download
            </Link>
            
            {isAuthenticated() ? (
              <>
                <Link 
                  to="/dashboard" 
                  className={`nav-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
                  onClick={closeMobileMenu}
                >
                  Dashboard
                </Link>
                <Link 
                  to="/profile" 
                  className={`nav-link ${location.pathname === '/profile' ? 'active' : ''}`}
                  onClick={closeMobileMenu}
                >
                  Profile
                </Link>
                {isAdmin() && (
                  <Link 
                    to="/admin" 
                    className={`nav-link admin-link ${location.pathname === '/admin' ? 'active' : ''}`}
                    onClick={closeMobileMenu}
                  >
                    Admin
                  </Link>
                )}
                
                <div className="nav-user">
                  <div className="user-info">
                    <span className="nav-username">{user?.username}</span>
                    <span className="nav-credits">💰 {user?.credits || 0}</span>
                  </div>
                  <button onClick={handleLogout} className="btn btn-secondary nav-logout">
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <div className="nav-auth">
                <Link 
                  to="/login" 
                  className="nav-link login-link"
                  onClick={closeMobileMenu}
                >
                  Login
                </Link>
                <Link 
                  to="/register" 
                  className="btn btn-primary nav-register"
                  onClick={closeMobileMenu}
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;