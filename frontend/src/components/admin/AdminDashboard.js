import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import AdminStats from './AdminStats';
import UserManagement from './UserManagement';
import PaymentManagement from './PaymentManagement';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [users, setUsers] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Auto-dismiss messages after 5 seconds
  useEffect(() => {
    if (success || error) {
      const timer = setTimeout(() => {
        setSuccess('');
        setError('');
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [success, error]);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    setLoading(true);
    try {
      const [dashboardResponse, usersResponse, paymentsResponse] = await Promise.all([
        adminAPI.getDashboard(),
        adminAPI.getUsers(),
        adminAPI.getAllPayments(),
      ]);

      setDashboardData(dashboardResponse.data);
      setUsers(usersResponse.data);
      setPayments(paymentsResponse.data);
    } catch (error) {
      setError('Failed to load admin data');
      console.error('Admin data loading error:', error);
    }
    setLoading(false);
  };

  const handleUserAction = async (action, username, amount = null) => {
    try {
      switch (action) {
        case 'delete':
          await adminAPI.deleteUser(username);
          setSuccess('User deleted successfully');
          break;
        case 'grantCredits':
          await adminAPI.grantCredits(username, amount);
          setSuccess(`${amount} credits granted successfully`);
          break;
        case 'deductCredits':
          await adminAPI.deductCredits(username, amount);
          setSuccess(`${amount} credits deducted successfully`);
          break;
        default:
          break;
      }
      await loadAdminData();
    } catch (error) {
      setError(error.response?.data?.detail || `Failed to ${action}`);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'users', label: 'User Management', icon: '👥' },
    { id: 'payments', label: 'Payment Management', icon: '💳' }
  ];

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="container">
        <div className="admin-header">
          <h1>Admin Dashboard</h1>
          <p>Manage users, credits, and monitor system activity</p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <div className="admin-tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`admin-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="admin-content">
          {activeTab === 'overview' && (
            <AdminStats 
              data={dashboardData}
              users={users}
              payments={payments}
            />
          )}

          {activeTab === 'users' && (
            <UserManagement 
              users={users}
              onUserAction={handleUserAction}
            />
          )}

          {activeTab === 'payments' && (
            <PaymentManagement 
              payments={payments}
              users={users}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;