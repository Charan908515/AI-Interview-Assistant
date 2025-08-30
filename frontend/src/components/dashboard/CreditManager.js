import React, { useState } from 'react';

const CreditManager = ({ currentCredits, onPayment, onLogTranscription, onLogResponse, loading }) => {
  const [paymentAmount, setPaymentAmount] = useState('');
  const [transcriptionText, setTranscriptionText] = useState('');
  const [aiQuery, setAiQuery] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [tokensUsed, setTokensUsed] = useState('');
  const [activeTab, setActiveTab] = useState('payment');

  const handlePayment = (e) => {
    e.preventDefault();
    const amount = parseFloat(paymentAmount);
    if (amount > 0) {
      onPayment(amount);
      setPaymentAmount('');
    }
  };

  const handleTranscription = (e) => {
    e.preventDefault();
    if (transcriptionText.trim()) {
      onLogTranscription(transcriptionText.trim());
      setTranscriptionText('');
    }
  };

  const handleAIResponse = (e) => {
    e.preventDefault();
    const tokens = parseInt(tokensUsed);
    if (aiQuery.trim() && aiResponse.trim() && tokens > 0) {
      onLogResponse(aiQuery.trim(), aiResponse.trim(), tokens);
      setAiQuery('');
      setAiResponse('');
      setTokensUsed('');
    }
  };

  const tabs = [
    { id: 'payment', label: 'Buy Credits', icon: '💳' },
    { id: 'transcription', label: 'Log Transcription', icon: '🎤' },
    { id: 'ai-response', label: 'Log AI Response', icon: '🤖' }
  ];

  return (
    <div className="credit-manager">
      <div className="card-header">
        <h2>Credit Management</h2>
        <p className="current-credits">Current Balance: <span>{currentCredits}</span> credits</p>
      </div>

      <div className="tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      <div className="tab-content">
        {activeTab === 'payment' && (
          <form onSubmit={handlePayment}>
            <div className="form-group">
              <label htmlFor="amount">Amount (USD)</label>
              <input
                type="number"
                id="amount"
                value={paymentAmount}
                onChange={(e) => setPaymentAmount(e.target.value)}
                min="1"
                step="0.01"
                placeholder="Enter amount"
                required
                disabled={loading}
              />
              <small className="form-help">1 USD = 10 Credits</small>
            </div>
            <button type="submit" className="btn btn-success" disabled={loading}>
              {loading ? 'Processing...' : 'Buy Credits'}
            </button>
          </form>
        )}

        {activeTab === 'transcription' && (
          <form onSubmit={handleTranscription}>
            <div className="form-group">
              <label htmlFor="transcription">Transcription Text</label>
              <textarea
                id="transcription"
                value={transcriptionText}
                onChange={(e) => setTranscriptionText(e.target.value)}
                placeholder="Enter transcription text..."
                rows="4"
                required
                disabled={loading}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Logging...' : 'Log Transcription'}
            </button>
          </form>
        )}

        {activeTab === 'ai-response' && (
          <form onSubmit={handleAIResponse}>
            <div className="form-group">
              <label htmlFor="query">Query</label>
              <input
                type="text"
                id="query"
                value={aiQuery}
                onChange={(e) => setAiQuery(e.target.value)}
                placeholder="Enter your query..."
                required
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <label htmlFor="response">AI Response</label>
              <textarea
                id="response"
                value={aiResponse}
                onChange={(e) => setAiResponse(e.target.value)}
                placeholder="Enter AI response..."
                rows="3"
                required
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <label htmlFor="tokens">Tokens Used</label>
              <input
                type="number"
                id="tokens"
                value={tokensUsed}
                onChange={(e) => setTokensUsed(e.target.value)}
                min="1"
                placeholder="Enter tokens used"
                required
                disabled={loading}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Logging...' : 'Log AI Response'}
            </button>
          </form>
        )}
      </div>

      <style jsx>{`
        .credit-manager {
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
        
        .current-credits {
          color: #666;
          margin: 0;
        }
        
        .current-credits span {
          font-weight: 600;
          color: #007bff;
        }
        
        .tabs {
          display: flex;
          border-bottom: 1px solid #e0e0e0;
          margin-bottom: 24px;
        }
        
        .tab {
          background: none;
          border: none;
          padding: 12px 16px;
          cursor: pointer;
          border-bottom: 2px solid transparent;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .tab:hover {
          background-color: #f8f9fa;
        }
        
        .tab.active {
          border-bottom-color: #007bff;
          color: #007bff;
        }
        
        .tab-icon {
          font-size: 16px;
        }
        
        .tab-label {
          font-size: 14px;
          font-weight: 500;
        }
        
        .form-help {
          display: block;
          margin-top: 4px;
          color: #666;
          font-size: 12px;
        }
        
        textarea {
          resize: vertical;
        }
        
        @media (max-width: 768px) {
          .tabs {
            flex-direction: column;
          }
          
          .tab {
            justify-content: center;
            border-bottom: none;
            border-right: 2px solid transparent;
          }
          
          .tab.active {
            border-right-color: #007bff;
            border-bottom-color: transparent;
          }
        }
      `}</style>
    </div>
  );
};

export default CreditManager;