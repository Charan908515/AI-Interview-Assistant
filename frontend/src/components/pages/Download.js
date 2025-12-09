import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Download.css';

const Download = () => {
  const { isAuthenticated } = useAuth();
  const [downloadStarted, setDownloadStarted] = useState(false);

  const handleDownload = () => {
    setDownloadStarted(true);
    // Create a download link for the .exe file
    const link = document.createElement('a');
    link.href = '/Whisper AI.exe';
    link.download = 'Whisper AI.exe';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Reset download started state after 3 seconds
    setTimeout(() => setDownloadStarted(false), 3000);
  };

  const systemRequirements = [
    { requirement: 'Operating System', value: 'Windows 10 or later' },
    { requirement: 'RAM', value: '4 GB minimum, 8 GB recommended' },
    { requirement: 'Storage', value: '500 MB free space' },
    { requirement: 'Internet', value: 'Stable internet connection required' },
    { requirement: 'Microphone', value: 'Built-in or external microphone' },
    { requirement: 'Audio', value: 'Speakers or headphones' }
  ];

  const features = [
    {
      icon: '🎤',
      title: 'Voice Recognition',
      description: 'Advanced speech-to-text technology with high accuracy'
    },
    {
      icon: '🤖',
      title: 'AI Responses',
      description: 'Intelligent AI interviewer with contextual questions'
    },
    {
      icon: '📊',
      title: 'Progress Tracking',
      description: 'Detailed analytics of your interview performance'
    },
    {
      icon: '💾',
      title: 'Session History',
      description: 'Save and review your past interview sessions'
    },
    {
      icon: '🔒',
      title: 'Offline Mode',
      description: 'Basic functionality available without internet'
    },
    {
      icon: '⚡',
      title: 'Fast Processing',
      description: 'Lightning-fast AI responses and transcription'
    }
  ];

  return (
    <div className="download-page">
      {/* Hero Section */}
      <section className="download-hero">
        <div className="container">
          <div className="download-content">
            <h1>Download AI Interview Assistant</h1>
            <p className="download-subtitle">
              Get the desktop application and start practicing your interview skills with AI-powered assistance.
            </p>
            
            <div className="download-main">
              <div className="download-card">
                <div className="app-icon">
                  <div className="icon-circle">
                    🎯
                  </div>
                </div>
                <h2>AI Interview Assistant</h2>
                <p>Version 1.0.0</p>
                <div className="download-size">
                  <span>📦 File size: ~50 MB</span>
                  <span>🖥️ Windows 10+</span>
                </div>
                
                <button 
                  onClick={handleDownload}
                  className={`btn-download ${downloadStarted ? 'downloading' : ''}`}
                  disabled={downloadStarted}
                >
                  {downloadStarted ? (
                    <>
                      <span className="download-spinner"></span>
                      Downloading...
                    </>
                  ) : (
                    <>
                      <span>📥</span>
                      Download Now
                    </>
                  )}
                </button>
                
                {downloadStarted && (
                  <div className="download-message">
                    <p>✅ Download started! Check your Downloads folder.</p>
                  </div>
                )}
                
                <div className="download-note">
                  <p>Free download • No subscription required</p>
                  {!isAuthenticated() && (
                    <p>
                      <Link to="/register">Create a free account</Link> to manage your credits and track progress.
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Installation Steps */}
      <section className="installation-steps">
        <div className="container">
          <h2>Installation Guide</h2>
          <div className="steps-grid">
            <div className="step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h3>Download the Installer</h3>
                <p>Click the download button above to get the AI_Interview_Assistant_Setup.exe file</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h3>Run the Installer</h3>
                <p>Locate the downloaded file and double-click to start the installation process</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h3>Follow Setup Wizard</h3>
                <p>Follow the installation wizard steps and choose your preferred installation location</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">4</div>
              <div className="step-content">
                <h3>Launch & Login</h3>
                <p>Open the application and log in with your account to start using AI Interview Assistant</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* App Features */}
      <section className="app-features">
        <div className="container">
          <h2>Application Features</h2>
          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">{feature.icon}</div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* System Requirements */}
      <section className="system-requirements">
        <div className="container">
          <h2>System Requirements</h2>
          <div className="requirements-card">
            <div className="requirements-list">
              {systemRequirements.map((req, index) => (
                <div key={index} className="requirement-item">
                  <span className="requirement-label">{req.requirement}:</span>
                  <span className="requirement-value">{req.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Support Section */}
      <section className="support-section">
        <div className="container">
          <div className="support-card">
            <h2>Need Help?</h2>
            <p>If you encounter any issues during installation or usage, we're here to help!</p>
            <div className="support-options">
              <div className="support-option">
                <h4>📧 Email Support</h4>
                <p>support@aiinterviewassistant.com</p>
              </div>
              <div className="support-option">
                <h4>💬 Live Chat</h4>
                <p>Available 24/7 in the application</p>
              </div>
              <div className="support-option">
                <h4>📖 Documentation</h4>
                <p>Comprehensive user guide included</p>
              </div>
            </div>
            {!isAuthenticated() && (
              <div className="account-prompt">
                <p>Don't have an account yet?</p>
                <Link to="/register" className="btn btn-primary">
                  Create Free Account
                </Link>
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Download;