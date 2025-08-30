import React from 'react';

const AdminStats = ({ data, users, payments }) => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getRecentUsers = () => {
    return users
      .sort((a, b) => new Date(b.id) - new Date(a.id))
      .slice(0, 5);
  };

  const getRecentPayments = () => {
    return payments
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, 5);
  };

  const getTotalRevenue = () => {
    return payments.reduce((sum, payment) => sum + payment.amount, 0);
  };

  const getActiveUsers = () => {
    return users.filter(user => user.is_active).length;
  };

  const getAdminUsers = () => {
    return users.filter(user => user.is_admin).length;
  };

  return (
    <div className="admin-stats">
      <div className="stats-grid">
        <div className="stat-card primary">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-value">{data?.total_users || users.length}</div>
            <div className="stat-label">Total Users</div>
            <div className="stat-detail">
              {getActiveUsers()} active • {getAdminUsers()} admins
            </div>
          </div>
        </div>

        <div className="stat-card success">
          <div className="stat-icon">🏆</div>
          <div className="stat-content">
            <div className="stat-value">{data?.total_credits || 0}</div>
            <div className="stat-label">Total Credits</div>
            <div className="stat-detail">Across all users</div>
          </div>
        </div>

        <div className="stat-card info">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <div className="stat-value">{formatCurrency(data?.total_revenue || getTotalRevenue())}</div>
            <div className="stat-label">Total Revenue</div>
            <div className="stat-detail">{data?.total_payments || payments.length} payments</div>
          </div>
        </div>

        <div className="stat-card warning">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <div className="stat-value">{formatCurrency(getTotalRevenue() / (payments.length || 1))}</div>
            <div className="stat-label">Avg Payment</div>
            <div className="stat-detail">Per transaction</div>
          </div>
        </div>
      </div>

      <div className="recent-activities">
        <div className="recent-section">
          <h3>Recent Users</h3>
          <div className="recent-list">
            {getRecentUsers().map(user => (
              <div key={user.id} className="recent-item">
                <div className="recent-avatar">
                  {user.username[0].toUpperCase()}
                </div>
                <div className="recent-info">
                  <div className="recent-name">{user.username}</div>
                  <div className="recent-detail">{user.credits} credits</div>
                </div>
                <div className="recent-status">
                  {user.is_admin && <span className="badge admin">Admin</span>}
                  {user.is_active ? (
                    <span className="badge active">Active</span>
                  ) : (
                    <span className="badge inactive">Inactive</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="recent-section">
          <h3>Recent Payments</h3>
          <div className="recent-list">
            {getRecentPayments().map(payment => (
              <div key={payment.id} className="recent-item">
                <div className="recent-avatar payment">
                  💳
                </div>
                <div className="recent-info">
                  <div className="recent-name">{formatCurrency(payment.amount)}</div>
                  <div className="recent-detail">
                    User ID: {payment.user_id}
                  </div>
                </div>
                <div className="recent-status">
                  <span className={`badge ${payment.status}`}>{payment.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <style jsx>{`
        .admin-stats {
          padding: 32px;
        }
        
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 24px;
          margin-bottom: 40px;
        }
        
        .stat-card {
          background: white;
          border-radius: 12px;
          padding: 24px;
          display: flex;
          align-items: center;
          gap: 16px;
          border-left: 4px solid;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .stat-card.primary { border-left-color: #007bff; }
        .stat-card.success { border-left-color: #28a745; }
        .stat-card.info { border-left-color: #17a2b8; }
        .stat-card.warning { border-left-color: #ffc107; }
        
        .stat-icon {
          font-size: 36px;
          opacity: 0.8;
        }
        
        .stat-value {
          font-size: 24px;
          font-weight: 700;
          color: #333;
          margin-bottom: 4px;
        }
        
        .stat-label {
          font-size: 14px;
          font-weight: 600;
          color: #666;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 4px;
        }
        
        .stat-detail {
          font-size: 12px;
          color: #999;
        }
        
        .recent-activities {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 32px;
        }
        
        .recent-section h3 {
          color: #333;
          margin-bottom: 16px;
          font-size: 18px;
        }
        
        .recent-list {
          background: #f8f9fa;
          border-radius: 8px;
          padding: 16px;
        }
        
        .recent-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 0;
          border-bottom: 1px solid #e0e0e0;
        }
        
        .recent-item:last-child {
          border-bottom: none;
        }
        
        .recent-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: #007bff;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 14px;
        }
        
        .recent-avatar.payment {
          background: #28a745;
          font-size: 16px;
        }
        
        .recent-info {
          flex: 1;
        }
        
        .recent-name {
          font-weight: 500;
          color: #333;
          margin-bottom: 2px;
        }
        
        .recent-detail {
          font-size: 12px;
          color: #666;
        }
        
        .recent-status {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        
        .badge {
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 10px;
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .badge.admin {
          background: #6f42c1;
          color: white;
        }
        
        .badge.active {
          background: #d4edda;
          color: #155724;
        }
        
        .badge.inactive {
          background: #f8d7da;
          color: #721c24;
        }
        
        .badge.completed {
          background: #d4edda;
          color: #155724;
        }
        
        .badge.pending {
          background: #fff3cd;
          color: #856404;
        }
        
        @media (max-width: 768px) {
          .admin-stats {
            padding: 16px;
          }
          
          .stats-grid {
            grid-template-columns: 1fr;
          }
          
          .recent-activities {
            grid-template-columns: 1fr;
          }
          
          .stat-card {
            padding: 16px;
          }
          
          .stat-icon {
            font-size: 24px;
          }
          
          .stat-value {
            font-size: 20px;
          }
        }
      `}</style>
    </div>
  );
};

export default AdminStats;