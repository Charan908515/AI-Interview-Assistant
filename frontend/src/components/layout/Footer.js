import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <div className="footer-brand">
              <span className="brand-icon">🎯</span>
              <span className="brand-name">AI Interview Assistant</span>
            </div>
            <p className="footer-description">
              Master your interview skills with AI-powered practice sessions. 
              Get real-time feedback and boost your confidence.
            </p>
            
          </div>

          <div className="footer-section">
            <h4>Product</h4>
            <ul className="footer-links">
              <li><Link to="/">Home</Link></li>
              <li><Link to="/download">Download</Link></li>
              <li><a href="#features">Features</a></li>
              <li><a href="#pricing">Pricing</a></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>Account</h4>
            <ul className="footer-links">
              <li><Link to="/login">Login</Link></li>
              <li><Link to="/register">Sign Up</Link></li>
              <li><Link to="/profile">Profile</Link></li>
              <li><Link to="/dashboard">Dashboard</Link></li>
            </ul>
          </div>

          

          <div className="footer-section">
            <h4>Download</h4>
            <p className="download-description">
              Get our desktop application for the best experience.
            </p>
            <Link to="/download" className="footer-download-btn">
              <span>📥</span>
              Download for Windows
            </Link>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="footer-bottom-content">
            <p className="copyright">
              © 2024 AI Interview Assistant. All rights reserved.
            </p>
            
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;