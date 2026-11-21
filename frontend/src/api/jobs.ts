import { apiClient } from './client';
import { Job, JobFormData, PaginatedResponse, Application, Skill } from '../types';

export const jobsApi = {
  getJobs: async (params?: { page?: number; is_active?: boolean; department?: string; search?: string }): Promise<PaginatedResponse<Job>> => {
    const res = await apiClient.get('/jobs/', { params });
    return res.data;
  },

  getJob: async (idOrSlug: string | number): Promise<Job> => {
    const res = await apiClient.get(`/jobs/${idOrSlug}/`);
    return res.data;
  },

  createJob: async (jobData: JobFormData): Promise<Job> => {
    const res = await apiClient.post('/jobs/', jobData);
    return res.data;
  },

  updateJob: async (id: number, jobData: Partial<JobFormData>): Promise<Job> => {
    const res = await apiClient.patch(`/jobs/${id}/`, jobData);
    return res.data;
  },

  deleteJob: async (id: number): Promise<void> => {
    await apiClient.delete(`/jobs/${id}/`);
  },

  toggleJobStatus: async (id: number): Promise<Job> => {
    const res = await apiClient.post(`/jobs/${id}/toggle-status/`);
    return res.data;
  },

  getJobStatistics: async (id: number): Promise<{ total: number; [key: string]: number }> => {
    const res = await apiClient.get(`/jobs/${id}/statistics/`);
    return res.data;
  },

  getJobApplications: async (id: number): Promise<Application[]> => {
    const res = await apiClient.get(`/jobs/${id}/applications/`);
    return res.data;
  },

  getSkillCatalog: async (): Promise<Skill[]> => {
    // Search skills endpoint or extract from search params
    const res = await apiClient.get('/search/candidates/', { params: { skill: 'Python' } });
    // Candidate search returns matched catalog
    return [];
  }
};
