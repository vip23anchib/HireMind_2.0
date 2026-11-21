import { apiClient } from './client';
import { Candidate, PaginatedResponse, Application } from '../types';

export const candidatesApi = {
  getCandidates: async (params?: { page?: number; search?: string; skill?: string }): Promise<PaginatedResponse<Candidate>> => {
    const res = await apiClient.get('/candidates/', { params });
    return res.data;
  },

  getCandidate: async (id: number): Promise<Candidate> => {
    const res = await apiClient.get(`/candidates/${id}/`);
    return res.data;
  },

  createCandidate: async (candidateData: Partial<Candidate>): Promise<Candidate> => {
    const res = await apiClient.post('/candidates/', candidateData);
    return res.data;
  },

  updateCandidate: async (id: number, candidateData: Partial<Candidate>): Promise<Candidate> => {
    const res = await apiClient.patch(`/candidates/${id}/`, candidateData);
    return res.data;
  },

  deleteCandidate: async (id: number): Promise<void> => {
    await apiClient.delete(`/candidates/${id}/`);
  },

  getCandidateApplications: async (id: number): Promise<Application[]> => {
    const res = await apiClient.get(`/candidates/${id}/applications/`);
    return res.data;
  },

  getResumeDownloadUrl: (id: number): string => {
    return `/api/v1/candidates/${id}/resume/`;
  },
};
