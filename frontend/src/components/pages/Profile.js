import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { paymentsAPI, authAPI } from '../../services/api';
import './Profile.css';

const Profile = () => {
  const { user, refreshUser } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [payments, setPayments] = useState([]);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  React.useEffect(() => {
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

  const handlePayment = async (e) => {
    e.preventDefault();
    const amount = parseFloat(paymentAmount);
    if (amount <= 0) return;

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Create payment - backend will automatically add credits for completed payments
      await paymentsAPI.createPayment(amount);
      
      // Refresh user data and payment history
      await refreshUser();
      await loadPaymentHistory();
      
      const creditsToAdd = amount * 10;
      setSuccess(`Payment of $${amount} processed successfully! ${creditsToAdd} credits added.`);
      setPaymentAmount('');
    } catch (error) {
      setError(error.response?.data?.detail || 'Payment failed');
    }

    setLoading(false);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getTotalSpent = () => {
    return payments.reduce((total, payment) => total + payment.amount, 0);
  };

  const getAccountAge = () => {
    // Assuming the user ID correlates with creation order
    const accountAge = Math.floor((Date.now() - user?.id * 86400000) / (1000 * 60 * 60 * 24));
    return Math.max(1, accountAge);
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '👤' },
    { id: 'credits', label: 'Buy Credits', icon: '💳' },
    { id: 'history', label: 'Payment History', icon: '📊' }
  ];

  return (
    <div className="profile-page">
      <div className="container">
        <div className="profile-header">
          <div className="profile-avatar">
            <div className="avatar-circle">
              {user?.username?.charAt(0)?.toUpperCase() || 'U'}
            </div>
          </div>
          <div className="profile-info">
            <h1>{user?.username || 'User'}</h1>
            <p className="profile-email">{user?.email}</p>
            <div className="profile-badges">
              {user?.is_admin && <span className="badge admin">Admin</span>}
              <span className="badge active">Active Member</span>
            </div>
          </div>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <div className="profile-tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`profile-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="profile-content">
          {activeTab === 'overview' && (
            <div className="overview-content">
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-icon">💰</div>
                  <div className="stat-content">
                    <div className="stat-value">{user?.credits || 0}</div>
                    <div className="stat-label">Available Credits</div>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">💳</div>
                  <div className="stat-content">
                    <div className="stat-value">{formatCurrency(getTotalSpent())}</div>
                    <div className="stat-label">Total Spent</div>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">📈</div>
                  <div className="stat-content">
                    <div className="stat-value">{payments.length}</div>
                    <div className="stat-label">Total Purchases</div>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">🗓️</div>
                  <div className="stat-content">
                    <div className="stat-value">{getAccountAge()}</div>
                    <div className="stat-label">Days Active</div>
                  </div>
                </div>
              </div>

              <div className="account-info">
                <h3>Account Information</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <label>Username</label>
                    <span>{user?.username}</span>
                  </div>
                  <div className="info-item">
                    <label>Email</label>
                    <span>{user?.email}</span>
                  </div>
                  <div className="info-item">
                    <label>Account Type</label>
                    <span>{user?.is_admin ? 'Administrator' : 'Regular User'}</span>
                  </div>
                  <div className="info-item">
                    <label>Status</label>
                    <span className="status-active">Active</span>
                  </div>
                </div>
              </div>

              <div className="quick-actions">
                <h3>Quick Actions</h3>
                <div className="actions-grid">
                  <button 
                    className="action-card"
                    onClick={() => setActiveTab('credits')}
                  >
                    <div className="action-icon">💳</div>
                    <div className="action-content">
                      <div className="action-title">Buy Credits</div>
                      <div className="action-subtitle">Add more credits to your account</div>
                    </div>
                  </button>
                  <button 
                    className="action-card"
                    onClick={() => setActiveTab('history')}
                  >
                    <div className="action-icon">📊</div>
                    <div className="action-content">
                      <div className="action-title">View History</div>
                      <div className="action-subtitle">Check your payment history</div>
                    </div>
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'credits' && (
            <div className="credits-content">
              <div className="purchase-section">
                <h3>Purchase Credits</h3>
                <p>Credits are used to access AI Interview Assistant features. 1 USD = 10 Credits</p>
                
                <form onSubmit={handlePayment} className="payment-form">
                  <div className="form-group">
                    <label htmlFor="amount">Amount (USD)</label>
                    <input
                      type="number"
                      id="amount"
                      value={paymentAmount}
                      onChange={(e) => setPaymentAmount(e.target.value)}
                      min="1"
                      max="1000"
                      step="1"
                      placeholder="Enter amount"
                      required
                      disabled={loading}
                    />
                    <div className="conversion-info">
                      {paymentAmount && (
                        <span>
                          ${paymentAmount} = {parseInt(paymentAmount) * 10} Credits
                        </span>
                      )}
                    </div>
                  </div>

                  <button 
                    type="submit" 
                    className="btn btn-primary btn-purchase"
                    disabled={loading || !paymentAmount}
                  >
                    {loading ? 'Processing...' : `Purchase Credits`}
                  </button>
                </form>

                <div className="quick-amounts">
                  <h4>Quick Purchase</h4>
                  <div className="amount-buttons">
                    {[5, 10, 25, 50].map(amount => (
                      <button
                        key={amount}
                        className="amount-btn"
                        onClick={() => setPaymentAmount(amount.toString())}
                        disabled={loading}
                      >
                        ${amount}
                        <span>{amount * 10} Credits</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'history' && (
            <div className="history-content">
              <h3>Payment History</h3>
              {payments.length === 0 ? (
                <div className="empty-history">
                  <div className="empty-icon">💳</div>
                  <p>No payment history yet</p>
                  <button 
                    className="btn btn-primary"
                    onClick={() => setActiveTab('credits')}
                  >
                    Make Your First Purchase
                  </button>
                </div>
              ) : (
                <div className="payments-table">
                  <div className="table-header">
                    <span>Date</span>
                    <span>Amount</span>
                    <span>Credits</span>
                    <span>Status</span>
                  </div>
                  {payments.map(payment => (
                    <div key={payment.id} className="table-row">
                      <span className="payment-date">
                        {formatDate(payment.timestamp)}
                      </span>
                      <span className="payment-amount">
                        {formatCurrency(payment.amount)}
                      </span>
                      <span className="payment-credits">
                        +{payment.amount * 10}
                      </span>
                      <span className={`payment-status ${payment.status}`}>
                        {payment.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;