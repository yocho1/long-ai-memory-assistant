import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5005';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  register: (email: string, password: string) =>
    api.post('/auth/register', { email, password }),
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
};

export const chatAPI = {
  sendMessage: (message: string, top_k: number = 4) =>
    api.post('/chat', { message, top_k }),
  getHistory: () => api.get('/history'),
};

export const ingestAPI = {
  uploadFile: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/ingest/upload', formData, {  // Updated endpoint
      headers: { 
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

export default api;