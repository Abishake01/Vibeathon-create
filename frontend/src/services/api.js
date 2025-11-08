import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  register: async (email, username, password) => {
    const response = await api.post('/auth/register', {
      email,
      username,
      password,
    });
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/auth/login-json', {
      email,
      password,
    });
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
    }
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
};

export const projectsAPI = {
  create: async (name, description = '') => {
    const response = await api.post('/projects', {
      name,
      description,
    });
    return response.data;
  },

  list: async () => {
    const response = await api.get('/projects');
    return response.data;
  },

  get: async (projectId) => {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  },

  update: async (projectId, name, description) => {
    const response = await api.patch(`/projects/${projectId}`, {
      name,
      description,
    });
    return response.data;
  },

  delete: async (projectId) => {
    await api.delete(`/projects/${projectId}`);
  },

  getFiles: async (projectId) => {
    const response = await api.get(`/projects/${projectId}/files`);
    return response.data;
  },

  getFile: async (projectId, filename) => {
    const response = await api.get(`/projects/${projectId}/files/${filename}`);
    return response.data;
  },

  updateFile: async (projectId, filename, content) => {
    const response = await api.put(`/projects/${projectId}/files/${filename}`, {
      content,
    });
    return response.data;
  },

  getPreviewUrl: (projectId) => {
    return `${API_BASE_URL}/projects/${projectId}/preview`;
  },
};

export default api;

