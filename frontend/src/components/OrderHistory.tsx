import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-toastify';
import {
  Package,
  Calendar,
  DollarSign,
  TrendingUp,
  Filter,
  Search,
  ChevronDown,
  CheckCircle,
  XCircle,
  Eye,
} from 'lucide-react';
import { orderAPI } from '../services/api';
import { OrderHistoryItem } from '../types/api.types';
import { formatDate, formatCurrency } from '../utils/formatters';
import LoadingSpinner from './LoadingSpinner';
import '../styles/OrderHistory.css';

interface OrderHistoryProps {
  userId: number;
}

const OrderHistory: React.FC<OrderHistoryProps> = ({ userId }) => {
  const [orders, setOrders] = useState<OrderHistoryItem[]>([]);
  const [filteredOrders, setFilteredOrders] = useState<OrderHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'approved' | 'denied'>('all');
  const [selectedOrder, setSelectedOrder] = useState<OrderHistoryItem | null>(null);

  useEffect(() => {
    loadOrders();
  }, [userId]);

  useEffect(() => {
    applyFilters();
  }, [orders, searchQuery, filterStatus]);

  const loadOrders = async () => {
    setIsLoading(true);
    try {
      const data = await orderAPI.getOrderHistory(userId);
      setOrders(data);
    } catch (error: any) {
      console.error('Error loading orders:', error);
      toast.error('Failed to load order history');
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...orders];

    // Apply status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(order =>
        filterStatus === 'approved'
          ? order.decision === 'ALLOW'
          : order.decision === 'DENY'
      );
    }

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(order =>
        order.product_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        order.search_query?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredOrders(filtered);
  };

  const getStats = () => {
    const total = orders.length;
    const approved = orders.filter(o => o.decision === 'ALLOW').length;
    const denied = orders.filter(o => o.decision === 'DENY').length;
    const totalSpent = orders
      .filter(o => o.decision === 'ALLOW')
      .reduce((sum, o) => sum + o.amount_inr, 0);

    return { total, approved, denied, totalSpent };
  };

  const stats = getStats();

  if (isLoading) {
    return (
      <div className="order-history-loading">
        <LoadingSpinner size="large" />
        <p>Loading order history...</p>
      </div>
    );
  }

  return (
    <div className="order-history-container">
      {/* Header */}
      <div className="order-history-header">
        <div className="header-content">
          <div className="header-icon">
            <Package size={32} />
          </div>
          <div>
            <h2>Order History</h2>
            <p>View all your past transactions</p>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="order-stats">
        <div className="stat-item">
          <div className="stat-icon primary">
            <Package size={24} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Orders</div>
          </div>
        </div>

        <div className="stat-item">
          <div className="stat-icon success">
            <CheckCircle size={24} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.approved}</div>
            <div className="stat-label">Approved</div>
          </div>
        </div>

        <div className="stat-item">
          <div className="stat-icon error">
            <XCircle size={24} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{stats.denied}</div>
            <div className="stat-label">Denied</div>
          </div>
        </div>

        <div className="stat-item">
          <div className="stat-icon info">
            <DollarSign size={24} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{formatCurrency(stats.totalSpent)}</div>
            <div className="stat-label">Total Spent</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="order-filters">
        <div className="search-box">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search orders..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-buttons">
          <button
            className={`filter-btn ${filterStatus === 'all' ? 'active' : ''}`}
            onClick={() => setFilterStatus('all')}
          >
            All Orders
          </button>
          <button
            className={`filter-btn ${filterStatus === 'approved' ? 'active' : ''}`}
            onClick={() => setFilterStatus('approved')}
          >
            Approved
          </button>
          <button
            className={`filter-btn ${filterStatus === 'denied' ? 'active' : ''}`}
            onClick={() => setFilterStatus('denied')}
          >
            Denied
          </button>
        </div>
      </div>

      {/* Orders List */}
      {filteredOrders.length === 0 ? (
        <div className="no-orders">
          <Package size={64} />
          <h3>No orders found</h3>
          <p>
            {searchQuery || filterStatus !== 'all'
              ? 'Try adjusting your filters'
              : 'Start placing orders to see them here'}
          </p>
        </div>
      ) : (
        <div className="orders-list">
          {filteredOrders.map((order) => (
            <motion.div
              key={order.id}
              className="order-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              whileHover={{ y: -4 }}
            >
              <div className="order-card-header">
                <div className="order-product">
                  <h3>{order.product_name}</h3>
                  <p>{formatDate(order.created_at)}</p>
                </div>
                <div className={`order-status ${order.decision.toLowerCase()}`}>
                  {order.decision === 'ALLOW' ? (
                    <>
                      <CheckCircle size={20} />
                      <span>Approved</span>
                    </>
                  ) : (
                    <>
                      <XCircle size={20} />
                      <span>Denied</span>
                    </>
                  )}
                </div>
              </div>

              <div className="order-card-body">
                <div className="order-info-grid">
                  <div className="info-item">
                    <span className="info-label">Amount</span>
                    <span className="info-value amount">
                      {formatCurrency(order.amount_inr)}
                    </span>
                  </div>

                  <div className="info-item">
                    <span className="info-label">Voice Match</span>
                    <span className="info-value">
                      {(order.speechbrain_similarity * 100).toFixed(1)}%
                    </span>
                  </div>

                  <div className="info-item">
                    <span className="info-label">Trust Score</span>
                    <span className="info-value">
                      {order.overall_trust_score}/100
                    </span>
                  </div>
                </div>

                <div className="order-reason">
                  <p>{order.decision_reason}</p>
                </div>
              </div>

              <div className="order-card-footer">
                <button
                  onClick={() => setSelectedOrder(order)}
                  className="view-details-btn"
                >
                  <Eye size={16} />
                  View Details
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Order Details Modal */}
      <AnimatePresence>
        {selectedOrder && (
          <motion.div
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedOrder(null)}
          >
            <motion.div
              className="modal-content order-details-modal"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="modal-header">
                <h2>Order Details</h2>
                <button
                  className="modal-close"
                  onClick={() => setSelectedOrder(null)}
                >
                  ✕
                </button>
              </div>

              {/* Modal Body */}
              <div className="modal-body">
                <div className={`order-status-banner ${selectedOrder.decision.toLowerCase()}`}>
                  {selectedOrder.decision === 'ALLOW' ? (
                    <CheckCircle size={32} />
                  ) : (
                    <XCircle size={32} />
                  )}
                  <div>
                    <h3>{selectedOrder.decision === 'ALLOW' ? 'Approved' : 'Denied'}</h3>
                    <p>{selectedOrder.decision_reason}</p>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Product Information</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span className="detail-label">Product</span>
                      <span className="detail-value">{selectedOrder.product_name}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Amount</span>
                      <span className="detail-value amount">
                        {formatCurrency(selectedOrder.amount_inr)}
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Date</span>
                      <span className="detail-value">
                        {formatDate(selectedOrder.created_at)}
                      </span>
                    </div>
                    {selectedOrder.budget_inr && (
                      <div className="detail-item">
                        <span className="detail-label">Budget</span>
                        <span className="detail-value">
                          {formatCurrency(selectedOrder.budget_inr)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Authentication</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span className="detail-label">Voice Similarity</span>
                      <span className="detail-value">
                        {(selectedOrder.speechbrain_similarity * 100).toFixed(2)}%
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Overall Trust</span>
                      <span className="detail-value">
                        {selectedOrder.overall_trust_score}/100
                      </span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Trust Layer Breakdown</h4>
                  <div className="trust-layers">
                    {Object.entries(selectedOrder.trust_scores).map(([key, value]) => (
                      <div key={key} className="trust-layer">
                        <div className="layer-header">
                          <span className="layer-name">
                            {key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                          </span>
                          <span className="layer-score">{value}/100</span>
                        </div>
                        <div className="layer-progress">
                          <div
                            className="layer-progress-fill"
                            style={{
                              width: `${value}%`,
                              background: value >= 70 ? '#10b981' : value >= 50 ? '#f59e0b' : '#ef4444'
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default OrderHistory;