import React, { useState } from 'react';

const ActivityLog = () => {
  const [activities] = useState([
    {
      id: 1,
      type: 'payment',
      description: 'Payment processed successfully',
      amount: '$10.00',
      timestamp: new Date().toISOString(),
    },
    {
      id: 2,
      type: 'credit_add',
      description: '100 credits added to account',
      amount: '+100',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
    },
    {
      id: 3,
      type: 'transcription',
      description: 'Audio transcription logged',
      amount: '-5',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
    },
    {
      id: 4,
      type: 'ai_response',
      description: 'AI response generated',
      amount: '-15',
      timestamp: new Date(Date.now() - 10800000).toISOString(),
    },
  ]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getActivityIcon = (type) => {
    const icons = {
      payment: '💳',
      credit_add: '➕',
      credit_deduct: '➖',
      transcription: '🎤',
      ai_response: '🤖',
    };
    return icons[type] || '📝';
  };

  const getActivityColor = (type) => {
    const colors = {
      payment: '#28a745',
      credit_add: '#28a745',
      credit_deduct: '#dc3545',
      transcription: '#17a2b8',
      ai_response: '#6f42c1',
    };
    return colors[type] || '#6c757d';
  };

  return (
    <div className="activity-log">
      <div className="card-header">
        <h2>Recent Activity</h2>
        <p className="card-subtitle">Latest account activities and transactions</p>
      </div>

      <div className="activity-list">
        {activities.map((activity) => (
          <div key={activity.id} className="activity-item">
            <div className="activity-icon" style={{ backgroundColor: getActivityColor(activity.type) }}>
              {getActivityIcon(activity.type)}
            </div>
            
            <div className="activity-content">
              <div className="activity-description">{activity.description}</div>
              <div className="activity-timestamp">{formatDate(activity.timestamp)}</div>
            </div>
            
            <div className="activity-amount" style={{ color: getActivityColor(activity.type) }}>
              {activity.amount}
            </div>
          </div>
        ))}
      </div>

      <style jsx>{`
        .activity-log {
          padding: 24px;
        }
        
        .card-header {
          margin-bottom: 24px;
          padding-bottom: 16px;
          border-bottom: 1px solid #e0e0e0;
        }
        
        .card-header h2 {
          margin: 0 0 8px 0;
          color: #333;
        }
        
        .card-subtitle {
          color: #666;
          margin: 0;
          font-size: 14px;
        }
        
        .activity-list {
          max-height: 400px;
          overflow-y: auto;
        }
        
        .activity-item {
          display: flex;
          align-items: center;
          padding: 16px 0;
          border-bottom: 1px solid #f0f0f0;
        }
        
        .activity-item:last-child {
          border-bottom: none;
        }
        
        .activity-icon {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 16px;
          font-size: 16px;
        }
        
        .activity-content {
          flex: 1;
        }
        
        .activity-description {
          font-weight: 500;
          color: #333;
          margin-bottom: 4px;
        }
        
        .activity-timestamp {
          font-size: 12px;
          color: #666;
        }
        
        .activity-amount {
          font-weight: 600;
          font-size: 14px;
        }
        
        @media (max-width: 768px) {
          .activity-item {
            align-items: flex-start;
          }
          
          .activity-icon {
            margin-top: 4px;
          }
        }
      `}</style>
    </div>
  );
};

export default ActivityLog;