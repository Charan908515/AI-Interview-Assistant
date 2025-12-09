import React, { useState } from 'react';

const CreditPurchase = ({ currentCredits, onPayment, loading }) => {
  const [paymentAmount, setPaymentAmount] = useState('');

  const handlePayment = (e) => {
    e.preventDefault();
    const amount = parseFloat(paymentAmount);
    if (amount > 0) {
      onPayment(amount);
      setPaymentAmount('');
    }
  };

  const quickAmounts = [5, 10, 25, 50];

  return (
    <div className="credit-purchase">
      <div className="section-header">
        <h2>💳 Purchase Credits</h2>
        <p>Add credits to your account for use in the AI Interview Assistant app</p>
      </div>

      <div className="current-balance">
        <div className="balance-display">
          <span className="balance-label">Current Balance:</span>
          <span className="balance-value">{currentCredits} credits</span>
        </div>
      </div>

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
          {paymentAmount && (
            <div className="conversion-display">
              ${paymentAmount} = {parseInt(paymentAmount) * 10} credits
            </div>
          )}
        </div>

        <button 
          type="submit" 
          className="btn btn-primary btn-purchase"
          disabled={loading || !paymentAmount}
        >
          {loading ? 'Processing Payment...' : 'Purchase Credits'}
        </button>
      </form>

      <div className="quick-purchase">
        <h4>Quick Purchase Options</h4>
        <div className="quick-buttons">
          {quickAmounts.map(amount => (
            <button
              key={amount}
              type="button"
              className="quick-btn"
              onClick={() => setPaymentAmount(amount.toString())}
              disabled={loading}
            >
              <div className="quick-amount">${amount}</div>
              <div className="quick-credits">{amount * 10} credits</div>
            </button>
          ))}
        </div>
      </div>

      <div className="pricing-info">
        <div className="pricing-note">
          <strong>💡 Pricing:</strong> 1 USD = 10 Credits
        </div>
        <div className="usage-note">
          Credits are consumed in the desktop app based on AI interactions and features used.
        </div>
      </div>
    </div>
  );
};

export default CreditPurchase;