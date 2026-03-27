import axios, { AxiosInstance } from 'axios';
import type {
  AuthResponse,
  User,
  InspectionList,
  Inspection,
  DefectRate,
  ModelPerformance,
  ModelVersion,
} from '@/types/api';

const TOKEN_KEY = 'factorymind_token';

const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Auto-logout on 401
apiClient.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY);
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export async function login(username: string, password: string): Promise<AuthResponse> {
  const res = await apiClient.post<AuthResponse>('/api/v1/auth/login', { username, password });
  return res.data;
}

export async function logout(): Promise<void> {
  await apiClient.post('/api/v1/auth/logout');
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export async function getMe(): Promise<User> {
  const res = await apiClient.get<User>('/api/v1/auth/me');
  return res.data;
}

export async function getInspections(page = 1, size = 20): Promise<InspectionList> {
  const res = await apiClient.get<InspectionList>('/api/v1/inspections', {
    params: { page, size },
  });
  return res.data;
}

export async function getInspection(id: string): Promise<Inspection> {
  const res = await apiClient.get<Inspection>(`/api/v1/inspections/${id}`);
  return res.data;
}

export async function getDefectRates(): Promise<DefectRate[]> {
  const res = await apiClient.get<DefectRate[]>('/api/v1/analytics/defect-rates');
  return res.data;
}

export async function getModelPerformance(): Promise<ModelPerformance[]> {
  const res = await apiClient.get<ModelPerformance[]>('/api/v1/analytics/model-performance');
  return res.data;
}

export async function getModels(): Promise<ModelVersion[]> {
  const res = await apiClient.get<ModelVersion[]>('/api/v1/models');
  return res.data;
}

export async function promoteModel(name: string): Promise<void> {
  await apiClient.post(`/api/v1/models/${name}/promote`);
}

export async function rollbackModel(name: string): Promise<void> {
  await apiClient.post(`/api/v1/models/${name}/rollback`);
}

export default apiClient;
