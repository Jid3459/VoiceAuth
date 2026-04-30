import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-toastify';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import {
  Settings,
  TrendingUp,
  Users,
  ShieldCheck,
  DollarSign,
  Activity,
  BarChart3,
  FileText,
  Save,
  RefreshCw,
  AlertCircle,
  Package,
  CheckCircle,
  XCircle,
  Eye,
  EyeOff,
  Zap,
  Shield,
  Lock,
  Unlock,
  Bell,
  Clock,
  Database,
  Server,
  Cpu,
  HardDrive,
} from 'lucide-react';
import { adminAPI } from '../services/api';
import { SystemSettings, SystemStats } from '../types';
import LoadingSpinner from './LoadingSpinner';
import '../styles/AdminDashboard.css';

interface AdminDashboardProps {
  userId: number;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ userId }) => {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [activeSection, setActiveSection] = useState<'overview' | 'settings' | 'logs' | 'security'>('overview');
  const [hasChanges, setHasChanges] = useState(false);
  const [error, setError] = useState<string>('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    loadData();
  }, [userId]);

  const loadData = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const [settingsData, statsData] = await Promise.all([
        adminAPI.getSettings(userId),
        adminAPI.getStats(userId),
      ]);
      
      setSettings(settingsData);
      setStats(statsData);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to load admin data';
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const loadLogs = async () => {
    try {
      const logsData = await adminAPI.getLogs(userId, 200);
      setLogs(logsData.logs || []);
    } catch (error: any) {
      toast.error('Failed to load logs');
    }
  };

  const handleUpdateSettings = async () => {
    if (!settings) return;

    setIsSaving(true);
    try {
      const updated = await adminAPI.updateSettings(userId, settings);
      setSettings(updated);
      setHasChanges(false);
      toast.success('✅ Settings updated successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleInputChange = (field: keyof SystemSettings, value: any) => {
    if (!settings) return;
    setSettings({ ...settings, [field]: value });
    setHasChanges(true);
  };

  // Chart data preparation
  const getOrderTrendData = () => {
    if (!stats) return [];
    return [
      { name: 'Week 1', approved: 45, denied: 5 },
      { name: 'Week 2', approved: 52, denied: 8 },
      { name: 'Week 3', approved: 48, denied: 6 },
      { name: 'Week 4', approved: stats.approved_orders, denied: stats.denied_orders },
    ];
  };

  const getTrustScoreDistribution = () => {
    return [
      { name: 'Excellent (85-100)', value: 35, color: '#10b981' },
      { name: 'Good (70-84)', value: 45, color: '#3b82f6' },
      { name: 'Fair (50-69)', value: 15, color: '#f59e0b' },
      { name: 'Poor (0-49)', value: 5, color: '#ef4444' },
    ];
  };

  if (error && !settings) {
    return (
      <div className="admin-error-container">
        <div className="error-icon-wrapper">
          <AlertCircle size={64} />
        </div>
        <h2>Failed to Load Admin Panel</h2>
        <p>{error}</p>
        <button onClick={loadData} className="btn btn-primary btn-large">
          <RefreshCw size={20} />
          Retry
        </button>
      </div>
    );
  }

  if (isLoading && !settings) {
    return (
      <div className="admin-loading-container">
        <div className="loading-spinner-wrapper">
          <LoadingSpinner size="large" />
        </div>
        <h3>Loading Admin Dashboard</h3>
        <p>Please wait while we fetch the data...</p>
      </div>
    );
  }

  if (!settings || !stats) {
    return (
      <div className="admin-error-container">
        <AlertCircle size={64} color="#f59e0b" />
        <h2>No Data Available</h2>
        <button onClick={loadData} className="btn btn-primary">
          <RefreshCw size={20} />
          Reload
        </button>
      </div>
    );
  }

  return (
    <div className="admin-dashboard-pro">
      {/* Top Bar */}
      <div className="admin-top-bar">
        <div className="top-bar-left">
          <div className="dashboard-logo">
            <Shield size={28} />
            <span>Admin Control Center</span>
          </div>
        </div>
        <div className="top-bar-right">
          <button className="icon-btn" title="Notifications">
            <Bell size={20} />
            <span className="notification-badge">3</span>
          </button>
          <button onClick={loadData} className="icon-btn" title="Refresh">
            <RefreshCw size={20} />
          </button>
          <div className="admin-status-indicator">
            <div className="status-dot"></div>
            <span>System Healthy</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="admin-main-content">
        {/* Sidebar Navigation */}
        <aside className="admin-sidebar-nav">
          <nav>
            <button
              className={`nav-link ${activeSection === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveSection('overview')}
            >
              <div className="nav-link-icon">
                <BarChart3 size={22} />
              </div>
              <div className="nav-link-content">
                <span className="nav-link-title">Overview</span>
                <span className="nav-link-subtitle">Dashboard</span>
              </div>
            </button>

            <button
              className={`nav-link ${activeSection === 'settings' ? 'active' : ''}`}
              onClick={() => setActiveSection('settings')}
            >
              <div className="nav-link-icon">
                <Settings size={22} />
              </div>
              <div className="nav-link-content">
                <span className="nav-link-title">Settings</span>
                <span className="nav-link-subtitle">Configuration</span>
              </div>
            </button>

            <button
              className={`nav-link ${activeSection === 'security' ? 'active' : ''}`}
              onClick={() => setActiveSection('security')}
            >
              <div className="nav-link-icon">
                <Shield size={22} />
              </div>
              <div className="nav-link-content">
                <span className="nav-link-title">Security</span>
                <span className="nav-link-subtitle">Authentication</span>
              </div>
            </button>

            <button
              className={`nav-link ${activeSection === 'logs' ? 'active' : ''}`}
              onClick={() => {
                setActiveSection('logs');
                if (logs.length === 0) loadLogs();
              }}
            >
              <div className="nav-link-icon">
                <FileText size={22} />
              </div>
              <div className="nav-link-content">
                <span className="nav-link-title">Logs</span>
                <span className="nav-link-subtitle">System Logs</span>
              </div>
            </button>
          </nav>

          {/* System Info */}
          <div className="sidebar-system-info">
            <h4>System Resources</h4>
            <div className="resource-item">
              <Cpu size={16} />
              <div className="resource-bar">
                <div className="resource-fill" style={{ width: '45%' }}></div>
              </div>
              <span>45%</span>
            </div>
            <div className="resource-item">
              <HardDrive size={16} />
              <div className="resource-bar">
                <div className="resource-fill" style={{ width: '62%' }}></div>
              </div>
              <span>62%</span>
            </div>
            <div className="resource-item">
              <Database size={16} />
              <div className="resource-bar">
                <div className="resource-fill" style={{ width: '28%' }}></div>
              </div>
              <span>28%</span>
            </div>
          </div>
        </aside>

        {/* Content Area */}
        <div className="admin-content-area">
          <AnimatePresence mode="wait">
            {/* OVERVIEW SECTION */}
            {activeSection === 'overview' && (
              <motion.div
                key="overview"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="dashboard-section"
              >
                <div className="section-header">
                  <h1>Dashboard Overview</h1>
                  <p>Real-time system analytics and performance metrics</p>
                </div>

                {/* KPI Cards */}
                <div className="kpi-grid">
                  <div className="kpi-card gradient-blue">
                    <div className="kpi-icon">
                      <Users size={32} />
                    </div>
                    <div className="kpi-content">
                      <h3>Total Users</h3>
                      <div className="kpi-value">{stats.total_users}</div>
                      <div className="kpi-trend positive">
                        <TrendingUp size={16} />
                        <span>+12% this month</span>
                      </div>
                    </div>
                    <div className="kpi-chart">
                      <div style={{ width: 80, height: 80 }}>
                        <CircularProgressbar
                          value={Math.round((stats.enrolled_users / stats.total_users) * 100)}
                          text={`${Math.round((stats.enrolled_users / stats.total_users) * 100)}%`}
                          styles={buildStyles({
                            pathColor: '#fff',
                            textColor: '#fff',
                            trailColor: 'rgba(255,255,255,0.2)',
                          })}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="kpi-card gradient-green">
                    <div className="kpi-icon">
                      <CheckCircle size={32} />
                    </div>
                    <div className="kpi-content">
                      <h3>Approved Orders</h3>
                      <div className="kpi-value">{stats.approved_orders}</div>
                      <div className="kpi-trend positive">
                        <TrendingUp size={16} />
                        <span>{stats.approval_rate}% approval rate</span>
                      </div>
                    </div>
                    <div className="kpi-sparkline">
                      <ResponsiveContainer width="100%" height={60}>
                        <AreaChart data={getOrderTrendData()}>
                          <Area
                            type="monotone"
                            dataKey="approved"
                            stroke="#fff"
                            fill="rgba(255,255,255,0.3)"
                            strokeWidth={2}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div className="kpi-card gradient-purple">
                    <div className="kpi-icon">
                      <ShieldCheck size={32} />
                    </div>
                    <div className="kpi-content">
                      <h3>Voice Enrolled</h3>
                      <div className="kpi-value">{stats.enrolled_users}</div>
                      <div className="kpi-trend positive">
                        <TrendingUp size={16} />
                        <span>Active users</span>
                      </div>
                    </div>
                    <div className="kpi-badge">
                      <Zap size={20} />
                      <span>Secure</span>
                    </div>
                  </div>

                  <div className="kpi-card gradient-orange">
                    <div className="kpi-icon">
                      <Activity size={32} />
                    </div>
                    <div className="kpi-content">
                      <h3>Auth Logs</h3>
                      <div className="kpi-value">{stats.total_auth_logs}</div>
                      <div className="kpi-trend neutral">
                        <Clock size={16} />
                        <span>Last 24h</span>
                      </div>
                    </div>
                    <div className="kpi-progress">
                      <div className="progress-circle">
                        <div className="progress-ring"></div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Charts Row */}
                <div className="charts-grid">
                  <div className="chart-card large">
                    <div className="chart-header">
                      <h3>Order Trends</h3>
                      <div className="chart-legend">
                        <span className="legend-item">
                          <span className="legend-dot approved"></span>
                          Approved
                        </span>
                        <span className="legend-item">
                          <span className="legend-dot denied"></span>
                          Denied
                        </span>
                      </div>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={getOrderTrendData()}>
                        <defs>
                          <linearGradient id="colorApproved" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                          </linearGradient>
                          <linearGradient id="colorDenied" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="name" stroke="#6b7280" />
                        <YAxis stroke="#6b7280" />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#fff',
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px',
                          }}
                        />
                        <Area
                          type="monotone"
                          dataKey="approved"
                          stroke="#10b981"
                          strokeWidth={3}
                          fill="url(#colorApproved)"
                        />
                        <Area
                          type="monotone"
                          dataKey="denied"
                          stroke="#ef4444"
                          strokeWidth={3}
                          fill="url(#colorDenied)"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="chart-card">
                    <div className="chart-header">
                      <h3>Trust Score Distribution</h3>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={getTrustScoreDistribution()}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={100}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {getTrustScoreDistribution().map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="pie-legend">
                      {getTrustScoreDistribution().map((item, index) => (
                        <div key={index} className="pie-legend-item">
                          <span
                            className="pie-legend-dot"
                            style={{ background: item.color }}
                          ></span>
                          <span>{item.name}</span>
                          <span className="pie-legend-value">{item.value}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="quick-stats-grid">
                  <div className="quick-stat-card">
                    <div className="stat-icon-wrapper green">
                      <CheckCircle size={24} />
                    </div>
                    <div className="stat-details">
                      <span className="stat-label">Success Rate</span>
                      <span className="stat-value">{stats.approval_rate}%</span>
                    </div>
                  </div>

                  <div className="quick-stat-card">
                    <div className="stat-icon-wrapper blue">
                      <Package size={24} />
                    </div>
                    <div className="stat-details">
                      <span className="stat-label">Total Orders</span>
                      <span className="stat-value">{stats.total_orders}</span>
                    </div>
                  </div>

                  <div className="quick-stat-card">
                    <div className="stat-icon-wrapper purple">
                      <Activity size={24} />
                    </div>
                    <div className="stat-details">
                      <span className="stat-label">Active Sessions</span>
                      <span className="stat-value">{stats.total_auth_logs}</span>
                    </div>
                  </div>

                  <div className="quick-stat-card">
                    <div className="stat-icon-wrapper orange">
                      <TrendingUp size={24} />
                    </div>
                    <div className="stat-details">
                      <span className="stat-label">Growth</span>
                      <span className="stat-value">+24%</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* SETTINGS SECTION */}
            {activeSection === 'settings' && (
              <motion.div
                key="settings"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="dashboard-section"
              >
                <div className="section-header">
                  <h1>System Configuration</h1>
                  <p>Manage thresholds and system parameters</p>
                </div>

                <div className="settings-pro-grid">
                  {/* Voice Authentication */}
                  <div className="settings-pro-card">
                    <div className="settings-card-header">
                      <div className="settings-icon">
                        <ShieldCheck size={24} />
                      </div>
                      <div>
                        <h3>Voice Authentication</h3>
                        <p>Similarity thresholds for voice matching</p>
                      </div>
                    </div>
                    <div className="settings-card-body">
                      <div className="setting-pro-item">
                        <label>
                          <span>Strong Match Threshold</span>
                          <span className="setting-badge">Recommended: 0.75</span>
                        </label>
                        <div className="slider-container">
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.01"
                            value={settings.similarity_threshold_strong}
                            onChange={(e) =>
                              handleInputChange(
                                'similarity_threshold_strong',
                                parseFloat(e.target.value)
                              )
                            }
                            className="pro-slider"
                          />
                          <div className="slider-value">{settings.similarity_threshold_strong}</div>
                        </div>
                      </div>

                      <div className="setting-pro-item">
                        <label>
                          <span>Weak Match Threshold</span>
                          <span className="setting-badge warning">Security Critical</span>
                        </label>
                        <div className="slider-container">
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.01"
                            value={settings.similarity_threshold_weak}
                            onChange={(e) =>
                              handleInputChange(
                                'similarity_threshold_weak',
                                parseFloat(e.target.value)
                              )
                            }
                            className="pro-slider"
                          />
                          <div className="slider-value">{settings.similarity_threshold_weak}</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Transaction Limits */}
                  <div className="settings-pro-card">
                    <div className="settings-card-header">
                      <div className="settings-icon">
                        <DollarSign size={24} />
                      </div>
                      <div>
                        <h3>Transaction Limits</h3>
                        <p>Amount thresholds for authorization</p>
                      </div>
                    </div>
                    <div className="settings-card-body">
                      <div className="setting-pro-item">
                        <label>Low Threshold (Auto-approve)</label>
                        <div className="input-with-currency">
                          <span className="currency-symbol">₹</span>
                          <input
                            type="number"
                            step="100"
                            value={settings.amount_threshold_low}
                            onChange={(e) =>
                              handleInputChange('amount_threshold_low', parseFloat(e.target.value))
                            }
                            className="pro-input"
                          />
                        </div>
                      </div>

                      <div className="setting-pro-item">
                        <label>Medium Threshold</label>
                        <div className="input-with-currency">
                          <span className="currency-symbol">₹</span>
                          <input
                            type="number"
                            step="100"
                            value={settings.amount_threshold_medium}
                            onChange={(e) =>
                              handleInputChange('amount_threshold_medium', parseFloat(e.target.value))
                            }
                            className="pro-input"
                          />
                        </div>
                      </div>

                      <div className="setting-pro-item">
                        <label>High Threshold</label>
                        <div className="input-with-currency">
                          <span className="currency-symbol">₹</span>
                          <input
                            type="number"
                            step="100"
                            value={settings.amount_threshold_high}
                            onChange={(e) =>
                              handleInputChange('amount_threshold_high', parseFloat(e.target.value))
                            }
                            className="pro-input"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Trust Scores */}
                  <div className="settings-pro-card">
                    <div className="settings-card-header">
                      <div className="settings-icon">
                        <TrendingUp size={24} />
                      </div>
                      <div>
                        <h3>Trust Score Requirements</h3>
                        <p>Minimum scores for transaction approval</p>
                      </div>
                    </div>
                    <div className="settings-card-body">
                      <div className="trust-score-visual">
                        <div className="trust-level">
                          <div className="trust-level-bar">
                            <div
                              className="trust-level-fill low"
                              style={{ width: `${settings.trust_score_low}%` }}
                            ></div>
                          </div>
                          <div className="trust-level-info">
                            <span>Low Amount</span>
                            <input
                              type="number"
                              min="0"
                              max="100"
                              value={settings.trust_score_low}
                              onChange={(e) =>
                                handleInputChange('trust_score_low', parseInt(e.target.value))
                              }
                              className="trust-score-input"
                            />
                          </div>
                        </div>

                        <div className="trust-level">
                          <div className="trust-level-bar">
                            <div
                              className="trust-level-fill medium"
                              style={{ width: `${settings.trust_score_medium}%` }}
                            ></div>
                          </div>
                          <div className="trust-level-info">
                            <span>Medium Amount</span>
                            <input
                              type="number"
                              min="0"
                              max="100"
                              value={settings.trust_score_medium}
                              onChange={(e) =>
                                handleInputChange('trust_score_medium', parseInt(e.target.value))
                              }
                              className="trust-score-input"
                            />
                          </div>
                        </div>

                        <div className="trust-level">
                          <div className="trust-level-bar">
                            <div
                              className="trust-level-fill high"
                              style={{ width: `${settings.trust_score_high}%` }}
                            ></div>
                          </div>
                          <div className="trust-level-info">
                            <span>High Amount</span>
                            <input
                              type="number"
                              min="0"
                              max="100"
                              value={settings.trust_score_high}
                              onChange={(e) =>
                                handleInputChange('trust_score_high', parseInt(e.target.value))
                              }
                              className="trust-score-input"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Logging */}
                  <div className="settings-pro-card">
                    <div className="settings-card-header">
                      <div className="settings-icon">
                        <FileText size={24} />
                      </div>
                      <div>
                        <h3>Logging & Debugging</h3>
                        <p>System logging configuration</p>
                      </div>
                    </div>
                    <div className="settings-card-body">
                      <div className="toggle-group">
                        <label className="toggle-item">
                          <div className="toggle-info">
                            <span className="toggle-title">Debug Mode</span>
                            <span className="toggle-desc">Enable verbose logging</span>
                          </div>
                          <div className="toggle-switch">
                            <input
                              type="checkbox"
                              checked={settings.enable_debug}
                              onChange={(e) => handleInputChange('enable_debug', e.target.checked)}
                            />
                            <span className="toggle-slider"></span>
                          </div>
                        </label>

                        <label className="toggle-item">
                          <div className="toggle-info">
                            <span className="toggle-title">Console Logging</span>
                            <span className="toggle-desc">Output logs to console</span>
                          </div>
                          <div className="toggle-switch">
                            <input
                              type="checkbox"
                              checked={settings.log_to_console}
                              onChange={(e) => handleInputChange('log_to_console', e.target.checked)}
                            />
                            <span className="toggle-slider"></span>
                          </div>
                        </label>

                        <label className="toggle-item">
                          <div className="toggle-info">
                            <span className="toggle-title">File Logging</span>
                            <span className="toggle-desc">Save logs to file</span>
                          </div>
                          <div className="toggle-switch">
                            <input
                              type="checkbox"
                              checked={settings.log_to_file}
                              onChange={(e) => handleInputChange('log_to_file', e.target.checked)}
                            />
                            <span className="toggle-slider"></span>
                          </div>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Save Button */}
                <AnimatePresence>
                  {hasChanges && (
                    <motion.div
                      initial={{ y: 100, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      exit={{ y: 100, opacity: 0 }}
                      className="floating-save-bar"
                    >
                      <div className="save-bar-content">
                        <div className="save-bar-info">
                          <AlertCircle size={20} />
                          <span>You have unsaved changes</span>
                        </div>
                        <div className="save-bar-actions">
                          <button
                            onClick={() => {
                              loadData();
                              setHasChanges(false);
                            }}
                            className="btn btn-ghost"
                          >
                            Discard
                          </button>
                          <button
                            onClick={handleUpdateSettings}
                            disabled={isSaving}
                            className="btn btn-primary btn-glow"
                          >
                            {isSaving ? <LoadingSpinner size="small" /> : <Save size={20} />}
                            {isSaving ? 'Saving...' : 'Save Changes'}
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}

            {/* SECURITY SECTION */}
            {activeSection === 'security' && (
              <motion.div
                key="security"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="dashboard-section"
              >
                <div className="section-header">
                  <h1>Security Center</h1>
                  <p>Authentication and access control</p>
                </div>

                <div className="security-grid">
                  <div className="security-card">
                    <div className="security-icon-wrapper">
                      <Lock size={32} />
                    </div>
                    <h3>Access Control</h3>
                    <p>Manage user permissions and roles</p>
                    <div className="security-status active">
                      <div className="status-indicator"></div>
                      <span>Active</span>
                    </div>
                  </div>

                  <div className="security-card">
                    <div className="security-icon-wrapper">
                      <Shield size={32} />
                    </div>
                    <h3>Voice Biometrics</h3>
                    <p>ECAPA-TDNN model status</p>
                    <div className="security-status active">
                      <div className="status-indicator"></div>
                      <span>Operational</span>
                    </div>
                  </div>

                  <div className="security-card">
                    <div className="security-icon-wrapper">
                      <Activity size={32} />
                    </div>
                    <h3>Real-time Monitoring</h3>
                    <p>Active threat detection</p>
                    <div className="security-status active">
                      <div className="status-indicator"></div>
                      <span>Monitoring</span>
                    </div>
                  </div>

                  <div className="security-card">
                    <div className="security-icon-wrapper">
                      <Database size={32} />
                    </div>
                    <h3>Data Encryption</h3>
                    <p>End-to-end encryption</p>
                    <div className="security-status active">
                      <div className="status-indicator"></div>
                      <span>Enabled</span>
                    </div>
                  </div>
                </div>

                <div className="security-details-card">
                  <h3>Security Overview</h3>
                  <div className="security-metrics">
                    <div className="security-metric">
                      <span className="metric-label">Authentication Success Rate</span>
                      <div className="metric-bar">
                        <div className="metric-fill" style={{ width: '94%', background: '#10b981' }}></div>
                      </div>
                      <span className="metric-value">94%</span>
                    </div>
                    <div className="security-metric">
                      <span className="metric-label">Blocked Attempts</span>
                      <div className="metric-bar">
                        <div className="metric-fill" style={{ width: '6%', background: '#ef4444' }}></div>
                      </div>
                      <span className="metric-value">6%</span>
                    </div>
                    <div className="security-metric">
                      <span className="metric-label">System Uptime</span>
                      <div className="metric-bar">
                        <div className="metric-fill" style={{ width: '99.9%', background: '#10b981' }}></div>
                      </div>
                      <span className="metric-value">99.9%</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* LOGS SECTION */}
            {activeSection === 'logs' && (
              <motion.div
                key="logs"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="dashboard-section"
              >
                <div className="section-header">
                  <div>
                    <h1>System Logs</h1>
                    <p>Real-time application logging</p>
                  </div>
                  <button onClick={loadLogs} className="btn btn-primary">
                    <RefreshCw size={20} />
                    Refresh Logs
                  </button>
                </div>

                <div className="logs-pro-viewer">
                  <div className="logs-toolbar">
                    <div className="logs-controls">
                      <button className="log-filter-btn active">All</button>
                      <button className="log-filter-btn">Errors</button>
                      <button className="log-filter-btn">Warnings</button>
                      <button className="log-filter-btn">Info</button>
                    </div>
                    <div className="logs-search">
                      <input type="text" placeholder="Search logs..." />
                    </div>
                  </div>
                  <div className="logs-content-pro">
                    {logs.length === 0 ? (
                      <div className="logs-empty-state">
                        <FileText size={64} />
                        <h3>No Logs Available</h3>
                        <p>Logs will appear here as they are generated</p>
                      </div>
                    ) : (
                      <pre className="logs-text">{logs.join('')}</pre>
                    )}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;