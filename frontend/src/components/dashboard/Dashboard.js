import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { creditsAPI, paymentsAPI } from '../../services/api';
import CreditPurchase from './CreditPurchase';
import PaymentHistory from './PaymentHistory';
import './Dashboard.css';

const Dashboard = () => {
  const { user, refreshUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [payments, setPayments] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadPaymentHistory();
  }, []);

  const loadPaymentHistory = async () => {
    try {
      const response = await paymentsAPI.getPaymentHistory();
      setPayments(response.data);
    } catch (error) {
      console.error('Error loading payment history:', error);
    }
  };

  const handlePayment = async (amount) => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Create payment - backend will automatically add credits for completed payments
      await paymentsAPI.createPayment(amount);
      
      // Refresh user data and payment history
      await refreshUser();
      await loadPaymentHistory();
      
      setSuccess(`Payment of $${amount} processed successfully! ${amount * 10} credits added.`);
    } catch (error) {
      setError(error.response?.data?.detail || 'Payment failed');
    }

    setLoading(false);
  };

  const getTotalSpent = () => {
    return payments.reduce((total, payment) => total + payment.amount, 0);
  };

  const getRecentPayments = () => {
    return payments
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, 3);
  };

  return (
    <div className="dashboard">
      <div className="container">
        <div className="dashboard-header">
          <div className="header-content">
            <h1>Welcome back, {user?.username}! 👋</h1>
            <p className="header-subtitle">
              Manage your credits and download the AI Interview Assistant app to start practicing.
            </p>
          </div>
          
          <div className="quick-actions">
            <Link to="/download" className="btn btn-primary quick-action-btn">
              <span>📥</span>
              Download App
            </Link>
            <Link to="/profile" className="btn btn-secondary quick-action-btn">
              <span>👤</span>
              View Profile
            </Link>
          </div>
        </div>

        <div className="dashboard-stats">
          <div className="stat-card primary">
            <div className="stat-icon">💰</div>
            <div className="stat-content">
              <div className="stat-value">{user?.credits || 0}</div>
              <div className="stat-label">Available Credits</div>
              <div className="stat-help">Use credits in the desktop app</div>
            </div>
          </div>
          
          <div className="stat-card success">
            <div className="stat-icon">💳</div>
            <div className="stat-content">
              <div className="stat-value">${getTotalSpent().toFixed(2)}</div>
              <div className="stat-label">Total Spent</div>
              <div className="stat-help">{payments.length} transactions</div>
            </div>
          </div>
          
          <div className="stat-card info">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-value">{getRecentPayments().length > 0 ? 'Active' : 'New'}</div>
              <div className="stat-label">Account Status</div>
              <div className="stat-help">
                {getRecentPayments().length > 0 ? 'Recent activity' : 'Ready to start'}
              </div>
            </div>
          </div>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <div className="dashboard-content">
          <div className="main-section">
            <div className="section-card">
              <div className="section-header">
                <h2>🎯 Getting Started</h2>
                <p>Follow these steps to start using AI Interview Assistant</p>
              </div>
              
              <div className="getting-started">
                <div className="step-item">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <h3>Download the App</h3>
                    <p>Get our desktop application for the full AI Interview Assistant experience</p>
                    <Link to="/download" className="step-action">
                      Download Now <span>→</span>
                    </Link>
                  </div>
                </div>
                
                <div className="step-item">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <h3>Purchase Credits</h3>
                    <p>Buy credits to power your AI interview sessions (1 USD = 10 credits)</p>
                    {(user?.credits || 0) === 0 ? (
                      <button 
                        className="step-action"
                        onClick={() => document.getElementById('credit-purchase').scrollIntoView()}
                      >
                        Buy Credits <span>→</span>
                      </button>
                    ) : (
                      <span className="step-complete">✅ Credits Available</span>
                    )}
                  </div>
                </div>
                
                <div className="step-item">
                  <div className="step-number">3</div>
                  <div className="step-content">
                    <h3>Start Practicing</h3>
                    <p>Login to the desktop app and begin your AI-powered interview practice sessions</p>
                    <span className="step-info">Open the downloaded app and login with your account</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="section-card" id="credit-purchase">
              <CreditPurchase 
                currentCredits={user?.credits || 0}
                onPayment={handlePayment}
                loading={loading}
              />
            </div>
          </div>

          <div className="sidebar-section">
            <div className="section-card">
              <PaymentHistory payments={payments} showTitle={true} />
            </div>

            <div className="section-card">
              <div className="section-header">
                <h3>💡 Tips</h3>
              </div>
              <div className="tips-list">
                <div className="tip-item">
                  <div className="tip-icon">🎤</div>
                  <div className="tip-text">
                    <strong>Clear Audio:</strong> Use a good microphone for better transcription accuracy
                  </div>
                </div>
                <div className="tip-item">
                  <div className="tip-icon">🤖</div>
                  <div className="tip-text">
                    <strong>Practice Regularly:</strong> Consistent practice improves your interview confidence
                  </div>
                </div>
                <div className="tip-item">
                  <div className="tip-icon">💰</div>
                  <div className="tip-text">
                    <strong>Credit Usage:</strong> Each AI interaction costs credits based on complexity
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;