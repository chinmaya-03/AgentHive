import axios from 'axios';

// Access API url from Vite environment or fall back to localhost FastAPI
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach access token automatically if present
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth endpoints
export const authApi = {
  register: (data: any) => api.post('/auth/register', data),
  login: (data: any) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
};

// Helper utility to safely format FastAPI/Axios error responses into string messages
export const extractErrorMessage = (err: any, fallback: string): string => {
  const detail = err?.response?.data?.detail;
  if (detail) {
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((d: any) => (typeof d === 'string' ? d : d.msg || JSON.stringify(d)))
        .join('; ');
    }
    if (typeof detail === 'object') {
      return detail.msg || JSON.stringify(detail);
    }
  }
  if (err?.code === 'ERR_NETWORK' || err?.message === 'Network Error' || !err?.response) {
    return 'Network Error: Unable to connect to the backend server. Please verify that the FastAPI server is running on http://localhost:8000.';
  }
  return err?.message || fallback;
};

// Projects endpoints
export const projectsApi = {
  list: () => api.get('/projects/'),
  get: (id: string) => api.get(`/projects/${id}`),
  create: (data: any) => api.post('/projects/', data),
  update: (id: string, data: any) => api.put(`/projects/${id}`, data),
  delete: (id: string) => api.delete(`/projects/${id}`),
  
  // Requirements sub-endpoints
  listRequirements: (projectId: string) => api.get(`/projects/${projectId}/requirements`),
  uploadRequirement: (projectId: string, formData: FormData) => 
    api.post(`/projects/${projectId}/requirements`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),
  deleteRequirement: (projectId: string, reqId: string) => 
    api.delete(`/projects/${projectId}/requirements/${reqId}`),
};

// Team & Skills endpoints
export const teamApi = {
  listMembers: (projectId: string) => api.get(`/team/?project_id=${projectId}`),
  addMember: (projectId: string, data: any) => api.post(`/team/?project_id=${projectId}`, data),
  updateMember: (projectId: string, memberId: string, data: any) => 
    api.put(`/team/${memberId}?project_id=${projectId}`, data),
  deleteMember: (projectId: string, memberId: string) => 
    api.delete(`/team/${memberId}?project_id=${projectId}`),
  
  // Global skills list
  listSkills: () => api.get('/skills/'),
  createSkill: (data: any) => api.post('/skills/', data),
};

// AI & Analytics endpoints
export const aiApi = {
  generateSprintPlan: (projectId: string, requirementId?: string) => 
    api.post(`/ai/projects/${projectId}/generate${requirementId ? `?requirement_id=${requirementId}` : ''}`),
  getLogs: (projectId: string) => api.get(`/ai/projects/${projectId}/logs`),
  getPlan: (projectId: string) => api.get(`/ai/projects/${projectId}/plan`),
  getDashboardMetrics: (projectId: string) => api.get(`/analytics/projects/${projectId}/dashboard-metrics`),
};

export default api;
