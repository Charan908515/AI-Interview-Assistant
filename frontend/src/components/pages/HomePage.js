import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './HomePage.css';

const HomePage = () => {
  const { isAuthenticated } = useAuth();

  const features = [
    {
      icon: '🎤',
      title: 'Voice-to-Text Transcription',
      description: 'Advanced AI transcription that accurately converts your speech to text in real-time'
    },
    {
      icon: '🤖',
      title: 'AI-Powered Responses',
      description: 'Get intelligent, contextual responses to help you practice and improve your interview skills'
    },
    {
      icon: '📊',
      title: 'Performance Analytics',
      description: 'Track your progress with detailed analytics and insights on your interview performance'
    },
    {
      icon: '💳',
      title: 'Credit-Based System',
      description: 'Flexible credit system - only pay for what you use with transparent pricing'
    },
    {
      icon: '🔒',
      title: 'Secure & Private',
      description: 'Your interview data is encrypted and secure. Practice with confidence'
    },
    {
      icon: '⚡',
      title: 'Real-time Processing',
      description: 'Lightning-fast AI responses to keep your interview practice flowing naturally'
    }
  ];

  const testimonials = [
    {
      name: 'Sarah Johnson',
      role: 'Software Engineer',
      text: 'AI Interview Assistant helped me land my dream job at a top tech company. The practice sessions were incredibly realistic!'
    },
    {
      name: 'Michael Chen',
      role: 'Product Manager',
      text: 'The AI responses were spot-on and helped me identify areas for improvement. Highly recommend!'
    },
    {
      name: 'Emily Rodriguez',
      role: 'Data Scientist',
      text: 'The transcription accuracy is amazing, and the feedback helped me become more confident in interviews.'
    }
  ];

  return (
    <div className="homepage">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-background">
          <div className="container">
            <div className="hero-content">
              <h1 className="hero-title">
                Master Your Interview Skills with
                <span className="highlight"> AI Interview Assistant</span>
              </h1>
              <p className="hero-subtitle">
                Practice interviews with advanced AI technology. Get real-time transcription, 
                intelligent responses, and detailed feedback to boost your confidence and land your dream job.
              </p>
              <div className="hero-buttons">
                <Link to="/download" className="btn btn-primary btn-large">
                  Download Now
                </Link>
                {!isAuthenticated() ? (
                  <Link to="/register" className="btn btn-secondary btn-large">
                    Get Started Free
                  </Link>
                ) : (
                  <Link to="/dashboard" className="btn btn-secondary btn-large">
                    Go to Dashboard
                  </Link>
                )}
              </div>
              <div className="hero-stats">
                <div className="stat">
                  <div className="stat-number">10+</div> 
                  <div className="stat-label">Successful Interviews</div>
                </div>
                <div className="stat">
                  <div className="stat-number">95%</div>
                  <div className="stat-label">User Success Rate</div>
                </div>
                <div className="stat">
                  <div className="stat-number">24/7</div>
                  <div className="stat-label">AI Availability</div>
                </div>
              </div>
            </div>
            <div className="hero-visual">
              <div className="app-preview">
                <div className="app-window">
                  <div className="app-header">
                    <div className="window-controls">
                      <span className="control red"></span>
                      <span className="control yellow"></span>
                      <span className="control green"></span>
                    </div>
                    <div className="window-title">AI Interview Assistant</div>
                  </div>
                  <div className="app-content">
                    <div className="chat-bubble ai">
                      <div className="bubble-header">🤖 AI Interviewer</div>
                      <div className="bubble-text">
                        "Tell me about a challenging project you've worked on and how you overcame obstacles."
                      </div>
                    </div>
                    <div className="chat-bubble user">
                      <div className="bubble-header">🎤 Your Response</div>
                      <div className="bubble-text">
                        "I worked on a complex data migration project where we had to transfer 10TB of data..."
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features">
        <div className="container">
          <div className="section-header">
            <h2>Why Choose AI Interview Assistant?</h2>
            <p>Everything you need to ace your next interview, powered by cutting-edge AI technology</p>
          </div>
          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">{feature.icon}</div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works">
        <div className="container">
          <div className="section-header">
            <h2>How It Works</h2>
            <p>Get started in just 3 simple steps</p>
          </div>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h3>Download & Install</h3>
                <p>Download our desktop application and create your account</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h3>Purchase Credits</h3>
                <p>Buy credits through our secure payment system ($1 = 10 credits)</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h3>Start Practicing</h3>
                <p>Begin your AI-powered interview sessions and improve your skills</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials">
        <div className="container">
          <div className="section-header">
            <h2>What Our Users Say</h2>
            <p>Join thousands of professionals who've improved their interview skills</p>
          </div>
          <div className="testimonials-grid">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="testimonial-card">
                <div className="testimonial-content">
                  <div className="quote-icon">"</div>
                  <p className="testimonial-text">{testimonial.text}</p>
                </div>
                <div className="testimonial-author">
                  <div className="author-avatar">
                    {testimonial.name[0]}
                  </div>
                  <div className="author-info">
                    <div className="author-name">{testimonial.name}</div>
                    <div className="author-role">{testimonial.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="pricing">
        <div className="container">
          <div className="section-header">
            <h2>Simple, Transparent Pricing</h2>
            <p>Pay only for what you use with our flexible credit system</p>
          </div>
          <div className="pricing-card">
            <div className="pricing-header">
              <h3>Credit-Based System</h3>
              <div className="price">
                <span className="currency">$</span>
                <span className="amount">1</span>
                <span className="period">= 10 Credits</span>
              </div>
            </div>
            <div className="pricing-features">
              <div className="feature">✅ Voice-to-text transcription</div>
              <div className="feature">✅ AI-powered responses</div>
              <div className="feature">✅ Performance analytics</div>
              <div className="feature">✅ Secure data storage</div>
              <div className="feature">✅ 24/7 availability</div>
            </div>
            <div className="pricing-footer">
              <Link to="/register" className="btn btn-primary btn-block">
                Start Your Free Account
              </Link>
              <p className="pricing-note">No subscription required • No hidden fees</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to Ace Your Next Interview?</h2>
            <p>Join thousands of professionals who've improved their interview skills with AI Interview Assistant</p>
            <div className="cta-buttons">
              <Link to="/download" className="btn btn-primary btn-large">
                Download Now
              </Link>
              <Link to="/register" className="btn btn-secondary btn-large">
                Create Free Account
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;