import React, { useState } from 'react';

const PaymentManagement = ({ payments, users }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('timestamp');
  const [sortOrder, setSortOrder] = useState('desc');
  const [statusFilter, setStatusFilter] = useState('all');

  const getUserById = (userId) => {
    return users.find(user => user.id === userId);
  };

  const filteredPayments = payments
    .filter(payment => {
      const user = getUserById(payment.user_id);
      const matchesSearch = user?.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           user?.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           payment.id.toString().includes(searchTerm);
      const matchesStatus = statusFilter === 'all' || payment.status === statusFilter;
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      let aVal = a[sortBy];
      let bVal = b[sortBy];
      
      if (sortBy === 'timestamp') {
        aVal = new Date(aVal);
        bVal = new Date(bVal);
      }
      
      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const getSortIcon = (field) => {
    if (sortBy !== field) return '↕️';
    return sortOrder === 'asc' ? '↗️' : '↘️';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getTotalRevenue = () => {
    return filteredPayments.reduce((sum, payment) => sum + payment.amount, 0);
  };

  const getStatusStats = () => {
    const stats = filteredPayments.reduce((acc, payment) => {
      acc[payment.status] = (acc[payment.status] || 0) + 1;
      return acc;
    }, {});
    return stats;
  };

  const statusStats = getStatusStats();

  return (
    <div className="payment-management">
      <div className="management-header">
        <div className="header-content">
          <h2>Payment Management</h2>
          <div className="payment-stats">
            <div className="stat-item">
              <span className="stat-label">Total Revenue:</span>
              <span className="stat-value">{formatCurrency(getTotalRevenue())}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Payments:</span>
              <span className="stat-value">{filteredPayments.length}</span>
            </div>
          </div>
        </div>
        
        <div className="management-controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search payments..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Status</option>
            <option value="completed">Completed</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {Object.keys(statusStats).length > 0 && (
        <div className="status-overview">
          {Object.entries(statusStats).map(([status, count]) => (
            <div key={status} className={`status-card ${status}`}>
              <div className="status-count">{count}</div>
              <div className="status-label">{status}</div>
            </div>
          ))}
        </div>
      )}

      <div className="payments-table-container">
        <table className="payments-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('id')} className="sortable">
                Payment ID {getSortIcon('id')}
              </th>
              <th onClick={() => handleSort('user_id')} className="sortable">
                User {getSortIcon('user_id')}
              </th>
              <th onClick={() => handleSort('amount')} className="sortable">
                Amount {getSortIcon('amount')}
              </th>
              <th onClick={() => handleSort('status')} className="sortable">
                Status {getSortIcon('status')}
              </th>
              <th onClick={() => handleSort('timestamp')} className="sortable">
                Date {getSortIcon('timestamp')}
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredPayments.map(payment => {
              const user = getUserById(payment.user_id);
              return (
                <tr key={payment.id}>
                  <td>
                    <span className="payment-id">#{payment.id}</span>
                  </td>
                  <td>
                    <div className="user-info">
                      {user ? (
                        <>
                          <div className="user-avatar">
                            {user.username[0].toUpperCase()}
                          </div>
                          <div className="user-details">
                            <div className="username">{user.username}</div>
                            <div className="user-email">{user.email}</div>
                          </div>
                        </>
                      ) : (
                        <span className="user-unknown">User #{payment.user_id}</span>
                      )}
                    </div>
                  </td>
                  <td>
                    <span className="amount">{formatCurrency(payment.amount)}</span>
                  </td>
                  <td>
                    <span className={`status-badge ${payment.status}`}>
                      {payment.status}
                    </span>
                  </td>
                  <td>
                    <div className="payment-date">
                      <div className="date-primary">{formatDate(payment.timestamp)}</div>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {filteredPayments.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">💳</div>
            <p>No payments found matching your criteria</p>
          </div>
        )}
      </div>

      <style jsx>{`
        .payment-management {
          padding: 32px;
        }
        
        .management-header {
          margin-bottom: 24px;
        }
        
        .header-content {
          margin-bottom: 16px;
        }
        
        .header-content h2 {
          color: #333;
          margin: 0 0 12px 0;
        }
        
        .payment-stats {
          display: flex;
          gap: 24px;
          flex-wrap: wrap;
        }
        
        .stat-item {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .stat-label {
          color: #666;
          font-size: 14px;
        }
        
        .stat-value {
          font-weight: 600;
          color: #333;
          font-size: 16px;
        }
        
        .management-controls {
          display: flex;
          gap: 16px;
          align-items: center;
          flex-wrap: wrap;
        }
        
        .search-box input {
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          width: 200px;
        }
        
        .filter-select {
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          background: white;
        }
        
        .status-overview {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }
        
        .status-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          text-align: center;
          border-left: 4px solid;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .status-card.completed { border-left-color: #28a745; }
        .status-card.pending { border-left-color: #ffc107; }
        .status-card.failed { border-left-color: #dc3545; }
        
        .status-count {
          font-size: 24px;
          font-weight: 700;
          color: #333;
          margin-bottom: 4px;
        }
        
        .status-label {
          font-size: 12px;
          font-weight: 500;
          text-transform: uppercase;
          color: #666;
          letter-spacing: 0.5px;
        }
        
        .payments-table-container {
          overflow-x: auto;
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .payments-table {
          width: 100%;
          border-collapse: collapse;
        }
        
        .payments-table th,
        .payments-table td {
          padding: 12px 16px;
          text-align: left;
          border-bottom: 1px solid #e0e0e0;
        }
        
        .payments-table th {
          background: #f8f9fa;
          font-weight: 600;
          color: #333;
          position: sticky;
          top: 0;
        }
        
        .payments-table th.sortable {
          cursor: pointer;
          user-select: none;
        }
        
        .payments-table th.sortable:hover {
          background: #e9ecef;
        }
        
        .payment-id {
          font-family: monospace;
          background: #f8f9fa;
          padding: 2px 6px;
          border-radius: 3px;
          font-size: 12px;
        }
        
        .user-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .user-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: #007bff;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 12px;
        }
        
        .user-details .username {
          font-weight: 500;
          color: #333;
        }
        
        .user-details .user-email {
          font-size: 12px;
          color: #666;
        }
        
        .user-unknown {
          color: #666;
          font-style: italic;
        }
        
        .amount {
          font-weight: 600;
          color: #28a745;
          font-size: 16px;
        }
        
        .status-badge {
          padding: 4px 12px;
          border-radius: 16px;
          font-size: 12px;
          font-weight: 500;
          text-transform: capitalize;
        }
        
        .status-badge.completed {
          background: #d4edda;
          color: #155724;
        }
        
        .status-badge.pending {
          background: #fff3cd;
          color: #856404;
        }
        
        .status-badge.failed {
          background: #f8d7da;
          color: #721c24;
        }
        
        .payment-date {
          font-size: 13px;
        }
        
        .date-primary {
          color: #333;
        }
        
        .empty-state {
          padding: 40px;
          text-align: center;
          color: #666;
        }
        
        .empty-icon {
          font-size: 48px;
          margin-bottom: 16px;
          opacity: 0.5;
        }
        
        @media (max-width: 768px) {
          .payment-management {
            padding: 16px;
          }
          
          .management-controls {
            flex-direction: column;
            align-items: stretch;
          }
          
          .search-box input {
            width: 100%;
          }
          
          .payment-stats {
            flex-direction: column;
            gap: 8px;
          }
          
          .status-overview {
            grid-template-columns: 1fr 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default PaymentManagement;