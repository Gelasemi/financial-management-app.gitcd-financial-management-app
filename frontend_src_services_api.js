import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // Redirect to login page or refresh token
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Dashboard API
export const fetchDashboardData = async (month) => {
  try {
    const response = await api.get(`/api/dashboard?month=${month}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    throw error;
  }
};

// Analysis API
export const fetchAnalysisData = async (month, type) => {
  try {
    const response = await api.get(`/api/analysis?month=${month}&type=${type}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching analysis data:', error);
    throw error;
  }
};

// Benchmarking API
export const fetchBenchmarkingData = async (month, type) => {
  try {
    const response = await api.get(`/api/benchmarking?month=${month}&type=${type}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching benchmarking data:', error);
    throw error;
  }
};

// File Upload API
export const uploadFile = async (formData, onUploadProgress) => {
  try {
    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
};

// Get Uploaded Files API
export const getUploadedFiles = async () => {
  try {
    const response = await api.get('/api/files');
    return response.data;
  } catch (error) {
    console.error('Error fetching uploaded files:', error);
    throw error;
  }
};

// Prediction API
export const fetchPredictionData = async (month, target, periods, modelType, scenario) => {
  try {
    const response = await api.post('/api/predict', {
      month,
      target,
      periods,
      model_type: modelType,
      scenario,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching prediction data:', error);
    throw error;
  }
};

// Chat API
export const sendChatMessage = async (messages) => {
  try {
    const response = await api.post('/api/chat', { messages });
    return response.data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};

export default api;