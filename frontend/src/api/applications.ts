import { apiClient } from './client';
import { Application, ApplicationStatus, ApplicationStatusHistory, PaginatedResponse } from '../types';

export const applicationsApi = {
  getApplications: async (params?: { page?: number; job?: number; status?: string; search?: string }): Promise<PaginatedResponse<Application>> => {
    const res = await apiClient.get('/applications/', { params });
    return res.data;
  },

  getApplication: async (id: number): Promise<Application> => {
    const res = await apiClient.get(`/applications/${id}/`);
    return res.data;
  },

  submitApplication: async (formData: FormData): Promise<Application> => {
    const res = await apiClient.post('/applications/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  updateStatus: async (id: number, status: ApplicationStatus, notes?: string): Promise<Application> => {
    const res = await apiClient.patch(`/applications/${id}/status/`, { status, notes });
    return res.data;
  },

  getStatusHistory: async (id: number): Promise<ApplicationStatusHistory[]> => {
    const res = await apiClient.get(`/applications/${id}/history/`);
    return res.data;
  },
};
