import React, { useState } from 'react';

const UserManagement = ({ users, onUserAction }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState('desc');
  const [filterAdmin, setFilterAdmin] = useState('all');
  const [selectedUser, setSelectedUser] = useState(null);
  const [creditAmount, setCreditAmount] = useState('');
  const [showCreditModal, setShowCreditModal] = useState(false);
  const [creditAction, setCreditAction] = useState('grant');

  const filteredUsers = users
    .filter(user => {
      const matchesSearch = user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           user.email.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesFilter = filterAdmin === 'all' || 
                           (filterAdmin === 'admin' && user.is_admin) ||
                           (filterAdmin === 'user' && !user.is_admin);
      return matchesSearch && matchesFilter;
    })
    .sort((a, b) => {
      let aVal = a[sortBy];
      let bVal = b[sortBy];
      
      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
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

  const handleCreditAction = async () => {
    const amount = parseInt(creditAmount);
    if (amount > 0 && selectedUser) {
      await onUserAction(creditAction, selectedUser.username, amount);
      setShowCreditModal(false);
      setCreditAmount('');
      setSelectedUser(null);
    }
  };

  const openCreditModal = (user, action) => {
    setSelectedUser(user);
    setCreditAction(action);
    setShowCreditModal(true);
  };

  const getSortIcon = (field) => {
    if (sortBy !== field) return '↕️';
    return sortOrder === 'asc' ? '↗️' : '↘️';
  };

  return (
    <div className="user-management">
      <div className="management-header">
        <h2>User Management</h2>
        
        <div className="management-controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <select
            value={filterAdmin}
            onChange={(e) => setFilterAdmin(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Users</option>
            <option value="admin">Admins Only</option>
            <option value="user">Regular Users</option>
          </select>
        </div>
      </div>

      <div className="users-table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('username')} className="sortable">
                Username {getSortIcon('username')}
              </th>
              <th onClick={() => handleSort('email')} className="sortable">
                Email {getSortIcon('email')}
              </th>
              <th onClick={() => handleSort('credits')} className="sortable">
                Credits {getSortIcon('credits')}
              </th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.map(user => (
              <tr key={user.username}>
                <td>
                  <div className="user-info">
                    <div className="user-avatar">
                      {user.username[0].toUpperCase()}
                    </div>
                    <span className="username">{user.username}</span>
                  </div>
                </td>
                <td>{user.email}</td>
                <td>
                  <span className="credits-badge">{user.credits}</span>
                </td>
                <td>
                  <div className="status-badges">
                    {user.is_admin && <span className="badge admin">Admin</span>}
                    <span className={`badge ${user.is_active ? 'active' : 'inactive'}`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </td>
                <td>
                  <div className="action-buttons">
                    <button
                      className="btn btn-sm btn-success"
                      onClick={() => openCreditModal(user, 'grantCredits')}
                      title="Grant Credits"
                    >
                      ➕
                    </button>
                    <button
                      className="btn btn-sm btn-secondary"
                      onClick={() => openCreditModal(user, 'deductCredits')}
                      title="Deduct Credits"
                      disabled={user.credits === 0}
                    >
                      ➖
                    </button>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => onUserAction('delete', user.username)}
                      title="Delete User"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredUsers.length === 0 && (
          <div className="empty-state">
            <p>No users found matching your criteria</p>
          </div>
        )}
      </div>

      {showCreditModal && selectedUser && (
        <div className="modal-overlay" onClick={() => setShowCreditModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                {creditAction === 'grantCredits' ? 'Grant Credits' : 'Deduct Credits'}
              </h3>
              <button 
                className="modal-close"
                onClick={() => setShowCreditModal(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="modal-body">
              <p>
                {creditAction === 'grantCredits' ? 'Grant' : 'Deduct'} credits {creditAction === 'grantCredits' ? 'to' : 'from'} <strong>{selectedUser.username}</strong>
              </p>
              <p>Current balance: <strong>{selectedUser.credits}</strong> credits</p>
              
              <div className="form-group">
                <label>Amount</label>
                <input
                  type="number"
                  value={creditAmount}
                  onChange={(e) => setCreditAmount(e.target.value)}
                  min="1"
                  max={creditAction === 'deductCredits' ? selectedUser.credits : undefined}
                  placeholder="Enter amount"
                  autoFocus
                />
              </div>
            </div>
            
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowCreditModal(false)}
              >
                Cancel
              </button>
              <button 
                className={`btn ${creditAction === 'grantCredits' ? 'btn-success' : 'btn-secondary'}`}
                onClick={() => handleCreditAction(creditAction, selectedUser.id)}
                disabled={!creditAmount || parseInt(creditAmount) <= 0}
              >
                {creditAction === 'grantCredits' ? 'Grant' : 'Deduct'} Credits
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .user-management {
          padding: 32px;
        }
        
        .management-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 24px;
          flex-wrap: wrap;
          gap: 16px;
        }
        
        .management-header h2 {
          color: #333;
          margin: 0;
        }
        
        .management-controls {
          display: flex;
          gap: 16px;
          align-items: center;
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
        
        .users-table-container {
          overflow-x: auto;
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .users-table {
          width: 100%;
          border-collapse: collapse;
        }
        
        .users-table th,
        .users-table td {
          padding: 12px 16px;
          text-align: left;
          border-bottom: 1px solid #e0e0e0;
        }
        
        .users-table th {
          background: #f8f9fa;
          font-weight: 600;
          color: #333;
          position: sticky;
          top: 0;
        }
        
        .users-table th.sortable {
          cursor: pointer;
          user-select: none;
        }
        
        .users-table th.sortable:hover {
          background: #e9ecef;
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
        
        .username {
          font-weight: 500;
        }
        
        .credits-badge {
          background: #e3f2fd;
          color: #1976d2;
          padding: 4px 12px;
          border-radius: 16px;
          font-size: 12px;
          font-weight: 500;
        }
        
        .status-badges {
          display: flex;
          gap: 4px;
          flex-wrap: wrap;
        }
        
        .badge {
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 10px;
          font-weight: 500;
          text-transform: uppercase;
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
        
        .action-buttons {
          display: flex;
          gap: 4px;
        }
        
        .btn-sm {
          padding: 6px 8px;
          font-size: 12px;
          min-width: 32px;
        }
        
        .empty-state {
          padding: 40px;
          text-align: center;
          color: #666;
        }
        
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }
        
        .modal {
          background: white;
          border-radius: 8px;
          min-width: 400px;
          max-width: 90vw;
        }
        
        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px;
          border-bottom: 1px solid #e0e0e0;
        }
        
        .modal-header h3 {
          margin: 0;
          color: #333;
        }
        
        .modal-close {
          background: none;
          border: none;
          font-size: 18px;
          cursor: pointer;
          padding: 4px;
        }
        
        .modal-body {
          padding: 20px;
        }
        
        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 12px;
          padding: 20px;
          border-top: 1px solid #e0e0e0;
        }
        
        @media (max-width: 768px) {
          .user-management {
            padding: 16px;
          }
          
          .management-header {
            flex-direction: column;
            align-items: stretch;
          }
          
          .management-controls {
            flex-direction: column;
          }
          
          .search-box input {
            width: 100%;
          }
          
          .modal {
            min-width: auto;
            margin: 20px;
          }
        }
      `}</style>
    </div>
  );
};

export default UserManagement;