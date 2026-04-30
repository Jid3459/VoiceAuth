import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ShoppingBag, Mic, Search, DollarSign, CheckCircle, XCircle, Loader } from 'lucide-react';
import { toast } from 'react-toastify';
import VoiceRecorder from './VoiceRecorder';
import TrustScoreDisplay from './TrustScoreDisplay';
import { orderAPI } from '../services/api';
import { OrderResponse } from '../types';
import '../styles/OrderForm.css';

interface OrderFormProps {
  userId: number;
}

const OrderForm: React.FC<OrderFormProps> = ({ userId }) => {
  const [query, setQuery] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<OrderResponse | null>(null);

  const suggestedProducts = [
    "iPhone 15 Pro",
    "Samsung Galaxy S23",
    "MacBook Pro M3",
    "AirPods Pro",
    "Sony WH-1000XM5"
  ];

  const handleRecordingComplete = async (audioBlob: Blob) => {
    if (!query.trim()) {
      toast.error('Please enter a product query first');
      return;
    }

    setIsProcessing(true);
    setResult(null);

    try {
      const response = await orderAPI.processOrder(userId, query, audioBlob);
      setResult(response);

      if (response.decision === 'ALLOW') {
        toast.success('✅ Order approved!');
      } else {
        toast.error('❌ Order denied');
      }
    } catch (error: any) {
      console.error('Error processing order:', error);
      toast.error(error.response?.data?.detail || 'Failed to process order');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSuggestionClick = (product: string) => {
    setQuery(`Buy ${product}`);
  };

  return (
    <div className="order-form-container">
      <motion.div
        className="order-form-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {/* Header */}
        <div className="form-header">
          <div className="header-icon">
            <ShoppingBag size={28} />
          </div>
          <div>
            <h2>Place Your Order</h2>
            <p>Voice-authenticated secure ordering</p>
          </div>
        </div>

        {/* Product Query Input */}
        <div className="query-section">
          <label>What would you like to order?</label>
          <div className="search-input-wrapper">
            <Search size={20} className="search-icon" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Buy iPhone 15 Pro under ₹80000"
              className="search-input"
            />
            {query && (
              <button 
                onClick={() => setQuery('')}
                className="clear-btn"
                type="button"
              >
                ✕
              </button>
            )}
          </div>

          {/* Suggestions */}
          <div className="suggestions">
            <span className="suggestions-label">Quick suggestions:</span>
            <div className="suggestion-chips">
              {suggestedProducts.map((product, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(product)}
                  className="suggestion-chip"
                  type="button"
                >
                  {product}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Voice Authentication */}
        <div className="voice-auth-section">
          <div className="section-header">
            <Mic size={20} />
            <h3>Voice Authentication Required</h3>
          </div>
          <p className="section-description">
            Record your voice to verify your identity and complete the order
          </p>
          <VoiceRecorder
            onRecordingComplete={handleRecordingComplete}
            isRecording={isRecording}
            setIsRecording={setIsRecording}
          />
        </div>

        {/* Processing State */}
        {isProcessing && (
          <motion.div 
            className="processing-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <Loader className="processing-icon" size={48} />
            <h3>Processing Your Order...</h3>
            <p>Verifying voice authentication and analyzing transaction</p>
          </motion.div>
        )}

        {/* Results */}
        {result && !isProcessing && (
          <motion.div
            className="order-results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {/* Decision Banner */}
            <div className={`decision-banner ${result.decision.toLowerCase()}`}>
              {result.decision === 'ALLOW' ? (
                <>
                  <CheckCircle size={32} />
                  <div>
                    <h3>Order Approved</h3>
                    <p>{result.reason}</p>
                  </div>
                </>
              ) : (
                <>
                  <XCircle size={32} />
                  <div>
                    <h3>Order Denied</h3>
                    <p>{result.reason}</p>
                  </div>
                </>
              )}
            </div>

            {/* Product Details */}
            {result.is_product_query && result.product && (
              <div className="product-details-card">
                <h4>Order Details</h4>
                <div className="detail-row">
                  <span className="detail-label">Product:</span>
                  <span className="detail-value">{result.product}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Amount:</span>
                  <span className="detail-value amount">
                    ₹{result.amount_inr?.toLocaleString('en-IN')}
                  </span>
                </div>
                {result.budget_inr && (
                  <div className="detail-row">
                    <span className="detail-label">Your Budget:</span>
                    <span className="detail-value">
                      ₹{result.budget_inr.toLocaleString('en-IN')}
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* Trust Scores */}
            <TrustScoreDisplay
              trustScores={result.trust_scores}
              overallScore={result.overall_trust_score}
              similarity={result.speechbrain_similarity}
            />

            {/* New Order Button */}
            <button
              onClick={() => {
                setResult(null);
                setQuery('');
              }}
              className="btn btn-primary btn-large"
            >
              Place Another Order
            </button>
          </motion.div>
        )}
      </motion.div>

      {/* Security Notice */}
      <div className="security-notice">
        <div className="notice-content">
          <div className="notice-icon">🔒</div>
          <div>
            <h4>Secure Transaction</h4>
            <p>All orders are protected by voice biometric authentication and multi-layer trust scoring</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderForm;