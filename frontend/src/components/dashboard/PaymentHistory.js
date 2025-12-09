import React from 'react';

const PaymentHistory = ({ payments, showTitle = false }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatAmount = (amount) => {
    return `$${amount.toFixed(2)}`;
  };

  const getStatusBadge = (status) => {
    const statusClass = status === 'completed' ? 'status-success' : 'status-pending';
    return <span className={`status-badge ${statusClass}`}>{status}</span>;
  };

  const recentPayments = payments.slice(0, 5);

  return (
    <div className="payment-history">
      {showTitle && (
        <div className="section-header">
          <h3>💳 Recent Payments</h3>
          {payments.length > 0 && (
            <p>Latest transactions from your account</p>
          )}
        </div>
      )}

      {payments.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">💳</div>
          <p>No payments yet</p>
          <small>Your payment history will appear here</small>
        </div>
      ) : (
        <div className="payments-list">
          {recentPayments.map((payment) => (
            <div key={payment.id} className="payment-item">
              <div className="payment-info">
                <div className="payment-amount">{formatAmount(payment.amount)}</div>
                <div className="payment-details">
                  <span className="payment-credits">+{payment.amount * 10} credits</span>
                  <span className="payment-date">{formatDate(payment.timestamp)}</span>
                </div>
              </div>
              <div className="payment-status">
                {getStatusBadge(payment.status)}
              </div>
            </div>
          ))}
          
          {payments.length > 5 && (
            <div className="view-more">
              <p>{payments.length - 5} more transactions</p>
              <small>Visit your profile to see all payments</small>
            </div>
          )}
        </div>
      )}

      <style jsx>{`
        .payment-history {
          height: 100%;
        }
        
        .section-header {
          margin-bottom: 20px;
        }
        
        .section-header h3 {
          margin: 0 0 8px 0;
          color: #333;
          font-size: 18px;
          font-weight: 600;
        }
        
        .section-header p {
          margin: 0;
          color: #666;
          font-size: 14px;
        }
        
        .empty-state {
          text-align: center;
          padding: 40px 20px;
          color: #666;
        }
        
        .empty-icon {
          font-size: 48px;
          margin-bottom: 16px;
          opacity: 0.5;
        }
        
        .empty-state p {
          margin: 0 0 8px 0;
          font-weight: 500;
        }
        
        .empty-state small {
          font-size: 12px;
          color: #999;
        }
        
        .payments-list {
          max-height: 300px;
          overflow-y: auto;
        }
        
        .payment-item {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          padding: 16px 0;
          border-bottom: 1px solid #f0f0f0;
        }
        
        .payment-item:last-child {
          border-bottom: none;
        }
        
        .payment-amount {
          font-weight: 600;
          color: #333;
          font-size: 16px;
          margin-bottom: 4px;
        }
        
        .payment-details {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        
        .payment-credits {
          font-size: 12px;
          color: #28a745;
          font-weight: 500;
        }
        
        .payment-date {
          font-size: 12px;
          color: #666;
        }
        
        .status-badge {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 500;
          text-transform: capitalize;
        }
        
        .status-success {
          background-color: #d4edda;
          color: #155724;
        }
        
        .status-pending {
          background-color: #fff3cd;
          color: #856404;
        }
        
        .view-more {
          text-align: center;
          padding: 16px 0;
          border-top: 1px solid #f0f0f0;
          margin-top: 8px;
        }
        
        .view-more p {
          margin: 0 0 4px 0;
          color: #666;
          font-size: 14px;
          font-weight: 500;
        }
        
        .view-more small {
          color: #999;
          font-size: 12px;
        }
        
        @media (max-width: 768px) {
          .payment-item {
            align-items: center;
          }
        }
      `}</style>
    </div>
  );
};

export default PaymentHistory;