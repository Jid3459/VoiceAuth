import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { 
  Mic, 
  Shield, 
  User, 
  LogOut, 
  ShoppingBag, 
  History, 
  Lock,
  Settings,
  Crown
} from 'lucide-react';

import VoiceEnrollment from './components/VoiceEnrollment';
import OrderForm from './components/OrderForm';
import OrderHistory from './components/OrderHistory';
import AuthLogs from './components/AuthLogs';
import AdminDashboard from './components/AdminDashboard';
import LoadingSpinner from './components/LoadingSpinner';
import { authAPI } from './services/api';
import { User as UserType } from './types';
import './App.css';

type TabType = 'order' | 'history' | 'logs';

function App() {
  const [currentUser, setCurrentUser] = useState<UserType | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [registrationMode, setRegistrationMode] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>('order');
  const [showAdmin, setShowAdmin] = useState(false);
  
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [regForm, setRegForm] = useState({ 
    username: '', 
    email: '', 
    password: '',
    confirmPassword: '' 
  });

  // Animations
  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!loginForm.email || !loginForm.password) {
      toast.error('Please enter email and password');
      return;
    }

    setIsLoading(true);
    try {
      const response = await authAPI.login(loginForm.email, loginForm.password);
      setCurrentUser(response.user);
      setLoginForm({ email: '', password: '' });
      toast.success(`Welcome back, ${response.user.username}!`);
    } catch (error: any) {
      console.error('Login error:', error);
      toast.error(error.response?.data?.detail || 'Invalid credentials');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!regForm.username || !regForm.email || !regForm.password) {
      toast.error('Please fill in all fields');
      return;
    }

    if (regForm.password !== regForm.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (regForm.password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    setIsLoading(true);
    try {
      const user = await authAPI.register(
        regForm.username, 
        regForm.email, 
        regForm.password
      );
      setCurrentUser(user);
      setRegistrationMode(false);
      setRegForm({ username: '', email: '', password: '', confirmPassword: '' });
      toast.success('Account created successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEnrollmentComplete = async () => {
    if (currentUser) {
      try {
        const updatedUser = await authAPI.getUser(currentUser.id);
        setCurrentUser(updatedUser);
        toast.success('Voice enrolled successfully!');
      } catch (error) {
        console.error('Error refreshing user:', error);
      }
    }
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setLoginForm({ email: '', password: '' });
    setActiveTab('order');
    setShowAdmin(false);
    toast.info('Logged out successfully');
  };

  // Login/Registration Screen
  if (!currentUser) {
    return (
      <>
        <ToastContainer position="top-right" theme="colored" />
        <div className="auth-wrapper">
          <div className="auth-background">
            <div className="gradient-orb orb-1"></div>
            <div className="gradient-orb orb-2"></div>
            <div className="gradient-orb orb-3"></div>
          </div>

          <motion.div 
            className="auth-container"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <div className="auth-card">
              {/* Logo & Header */}
              <div className="auth-header">
                <div className="logo">
                  <div className="logo-icon">
                    <Mic size={32} />
                  </div>
                  <h1>VoiceGuard</h1>
                </div>
                <p className="auth-subtitle">
                  {registrationMode 
                    ? 'Create your secure account' 
                    : 'Biometric Voice Authentication'}
                </p>
              </div>

              <AnimatePresence mode="wait">
                {!registrationMode ? (
                  // Login Form
                  <motion.form 
                    key="login"
                    onSubmit={handleLogin} 
                    className="auth-form"
                    variants={pageVariants}
                    initial="initial"
                    animate="animate"
                    exit="exit"
                  >
                    <div className="form-group">
                      <label>Email Address</label>
                      <div className="input-wrapper">
                        <User size={20} className="input-icon" />
                        <input
                          type="email"
                          placeholder="Enter your email"
                          value={loginForm.email}
                          onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
                          required
                        />
                      </div>
                    </div>

                    <div className="form-group">
                      <label>Password</label>
                      <div className="input-wrapper">
                        <Lock size={20} className="input-icon" />
                        <input
                          type="password"
                          placeholder="Enter your password"
                          value={loginForm.password}
                          onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                          required
                        />
                      </div>
                    </div>

                    <button 
                      type="submit" 
                      disabled={isLoading} 
                      className="btn btn-primary btn-large"
                    >
                      {isLoading ? <LoadingSpinner size="small" /> : 'Sign In'}
                    </button>

                    <div className="auth-divider">
                      <span>OR</span>
                    </div>

                    <button 
                      type="button"
                      onClick={() => setRegistrationMode(true)}
                      className="btn btn-secondary btn-large"
                    >
                      Create New Account
                    </button>
                  </motion.form>
                ) : (
                  // Registration Form
                  <motion.form 
                    key="register"
                    onSubmit={handleRegister} 
                    className="auth-form"
                    variants={pageVariants}
                    initial="initial"
                    animate="animate"
                    exit="exit"
                  >
                    <div className="form-group">
                      <label>Username</label>
                      <div className="input-wrapper">
                        <User size={20} className="input-icon" />
                        <input
                          type="text"
                          placeholder="Choose a username"
                          value={regForm.username}
                          onChange={(e) => setRegForm({...regForm, username: e.target.value})}
                          required
                        />
                      </div>
                    </div>

                    <div className="form-group">
                      <label>Email Address</label>
                      <div className="input-wrapper">
                        <User size={20} className="input-icon" />
                        <input
                          type="email"
                          placeholder="Enter your email"
                          value={regForm.email}
                          onChange={(e) => setRegForm({...regForm, email: e.target.value})}
                          required
                        />
                      </div>
                    </div>

                    <div className="form-group">
                      <label>Password</label>
                      <div className="input-wrapper">
                        <Lock size={20} className="input-icon" />
                        <input
                          type="password"
                          placeholder="Min. 8 characters"
                          value={regForm.password}
                          onChange={(e) => setRegForm({...regForm, password: e.target.value})}
                          required
                          minLength={8}
                        />
                      </div>
                    </div>

                    <div className="form-group">
                      <label>Confirm Password</label>
                      <div className="input-wrapper">
                        <Lock size={20} className="input-icon" />
                        <input
                          type="password"
                          placeholder="Re-enter password"
                          value={regForm.confirmPassword}
                          onChange={(e) => setRegForm({...regForm, confirmPassword: e.target.value})}
                          required
                          minLength={8}
                        />
                      </div>
                    </div>

                    <button 
                      type="submit" 
                      disabled={isLoading} 
                      className="btn btn-primary btn-large"
                    >
                      {isLoading ? <LoadingSpinner size="small" /> : 'Create Account'}
                    </button>

                    <div className="auth-divider">
                      <span>OR</span>
                    </div>

                    <button 
                      type="button"
                      onClick={() => setRegistrationMode(false)}
                      className="btn btn-secondary btn-large"
                    >
                      Back to Login
                    </button>
                  </motion.form>
                )}
              </AnimatePresence>

              {/* Features */}
              <div className="auth-features">
                <div className="feature">
                  <Shield size={16} />
                  <span>Bank-grade Security</span>
                </div>
                <div className="feature">
                  <Mic size={16} />
                  <span>Voice Biometrics</span>
                </div>
                <div className="feature">
                  <Lock size={16} />
                  <span>End-to-End Encrypted</span>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="auth-footer">
              <p>Powered by <strong>SpeechBrain ECAPA-TDNN</strong></p>
            </div>
          </motion.div>
        </div>
      </>
    );
  }

  // Main Application
  return (
    <>
      <ToastContainer position="top-right" theme="colored" />
      <div className="app-wrapper">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="sidebar-header">
            <div className="logo">
              <div className="logo-icon">
                <Mic size={24} />
              </div>
              <h2>VoiceGuard</h2>
            </div>
          </div>

          <nav className="sidebar-nav">
            <button
              className={`nav-item ${activeTab === 'order' ? 'active' : ''}`}
              onClick={() => { setActiveTab('order'); setShowAdmin(false); }}
            >
              <ShoppingBag size={20} />
              <span>Place Order</span>
            </button>

            <button
              className={`nav-item ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => { setActiveTab('history'); setShowAdmin(false); }}
            >
              <History size={20} />
              <span>Order History</span>
            </button>

            <button
              className={`nav-item ${activeTab === 'logs' ? 'active' : ''}`}
              onClick={() => { setActiveTab('logs'); setShowAdmin(false); }}
            >
              <Lock size={20} />
              <span>Auth Logs</span>
            </button>

            {(currentUser.is_admin || currentUser.is_superuser) && (
              <button
                className={`nav-item ${showAdmin ? 'active' : ''}`}
                onClick={() => setShowAdmin(!showAdmin)}
              >
                {currentUser.is_superuser ? <Crown size={20} /> : <Settings size={20} />}
                <span>Admin Panel</span>
              </button>
            )}
          </nav>

          {/* User Profile */}
          <div className="sidebar-profile">
            <div className="profile-info">
              <div className="avatar">
                {currentUser.username.charAt(0).toUpperCase()}
              </div>
              <div className="profile-details">
                <h4>{currentUser.username}</h4>
                <p>{currentUser.email}</p>
                {currentUser.is_voice_enrolled && (
                  <span className="status-badge">
                    <Shield size={12} />
                    Voice Enrolled
                  </span>
                )}
                {currentUser.is_superuser && (
                  <span className="role-badge superuser">
                    <Crown size={12} />
                    Superuser
                  </span>
                )}
                {currentUser.is_admin && !currentUser.is_superuser && (
                  <span className="role-badge admin">
                    <Settings size={12} />
                    Admin
                  </span>
                )}
              </div>
            </div>
            <button onClick={handleLogout} className="logout-btn" title="Logout">
              <LogOut size={20} />
            </button>
          </div>
        </aside>

        {/* Main Content */}
        <main className="main-content">
          <AnimatePresence mode="wait">
            {!currentUser.is_voice_enrolled ? (
              <motion.div
                key="enrollment"
                variants={pageVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="content-wrapper"
              >
                <VoiceEnrollment
                  userId={currentUser.id}
                  onEnrollmentComplete={handleEnrollmentComplete}
                />
              </motion.div>
            ) : showAdmin ? (
              <motion.div
                key="admin"
                variants={pageVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="content-wrapper"
              >
                <AdminDashboard userId={currentUser.id} />
              </motion.div>
            ) : (
              <motion.div
                key={activeTab}
                variants={pageVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="content-wrapper"
              >
                {activeTab === 'order' && <OrderForm userId={currentUser.id} />}
                {activeTab === 'history' && <OrderHistory userId={currentUser.id} />}
                {activeTab === 'logs' && <AuthLogs userId={currentUser.id} />}
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>
    </>
  );
}

export default App;