import axios from 'axios';

const DEPLOYED_API_BASE_URL = 'https://se-project-backend-ddr9.onrender.com';
const API_BASE_URL = 'http://localhost:8000';


const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (formData) => {
    const data = new FormData();
    data.append('username', formData.username);
    data.append('password', formData.password);
    
    return api.post('/auth/login', data, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  register: (userData) => api.post('/auth/register', userData),
  getMe: () => api.get('/auth/me'),
};

export const creditsAPI = {
  addCredits: (amount) => api.post('/credits/add', { amount }),
  deductCredits: (amount) => api.post('/credits/deduct', { amount }),
  getBalance: () => api.get('/credits/balance'),
};

export const paymentsAPI = {
  createPayment: (amount) => api.post('/payments/create', { amount }),
  getPaymentHistory: () => api.get('/payments/history'),
};

export const transcriptionAPI = {
  logTranscription: (transcript_text) => api.post('/transcriptions/', { transcript_text }),
};

export const responseAPI = {
  logAIResponse: (query, ai_response, tokens_used) => 
    api.post('/responses/', { query, ai_response, tokens_used }),
};

export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard'),
  getUsers: () => api.get('/admin/users'),
  deleteUser: (userId) => api.delete(`/admin/users/${userId}`),
  grantCredits: (userId, amount) => api.post(`/admin/users/${userId}/grant_credits?amount=${amount}`),
  deductCredits: (userId, amount) => api.post(`/admin/users/${userId}/deduct_credits?amount=${amount}`),
  getAllPayments: () => api.get('/admin/payments'),
  getUserPayments: (userId) => api.get(`/admin/payments/${userId}`),
};

export default api;