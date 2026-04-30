import axios from 'axios';
import { User, OrderResponse, AuthLog, SystemSettings, SystemStats } from '../types';
import { OrderHistoryItem } from '../types/api.types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: async (username: string, email: string, password: string): Promise<User> => {
    const response = await api.post('/auth/register', { username, email, password });
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  enrollVoice: async (userId: number, audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'voice.wav');
    
    const response = await api.post(`/auth/enroll-voice/${userId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  verifyVoice: async (userId: number, audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'voice.wav');
    
    const response = await api.post(`/auth/verify-voice/${userId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getUser: async (userId: number): Promise<User> => {
    const response = await api.get(`/auth/users/${userId}`);
    return response.data;
  },
};

export const orderAPI = {
  processOrder: async (userId: number, query: string, audioBlob: Blob): Promise<OrderResponse> => {
    const formData = new FormData();
    formData.append('user_id', userId.toString());
    formData.append('query', query);
    formData.append('audio', audioBlob, 'voice.wav');
    
    const response = await api.post('/orders/process', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getOrderHistory: async (userId: number): Promise<OrderHistoryItem[]> => {
    const response = await api.get(`/orders/history/${userId}`);
    return response.data;
  },

  getAuthLogs: async (userId: number, limit: number = 20): Promise<AuthLog[]> => {
    const response = await api.get(`/orders/auth-logs/${userId}?limit=${limit}`);
    return response.data;
  },
};

export const adminAPI = {
  getSettings: async (userId: number): Promise<SystemSettings> => {
    const response = await api.get(`/admin/settings?user_id=${userId}`);
    return response.data;
  },

  updateSettings: async (userId: number, settings: Partial<SystemSettings>): Promise<SystemSettings> => {
    const response = await api.put(`/admin/settings?user_id=${userId}`, settings);
    return response.data;
  },

  getStats: async (userId: number): Promise<SystemStats> => {
    const response = await api.get(`/admin/stats?user_id=${userId}`);
    return response.data;
  },

  getLogs: async (userId: number, lines: number = 100) => {
    const response = await api.get(`/admin/logs?user_id=${userId}&lines=${lines}`);
    return response.data;
  },

  clearLogs: async (userId: number) => {
    const response = await api.post(`/admin/logs/clear?user_id=${userId}`);
    return response.data;
  },
};