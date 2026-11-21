import { apiClient } from './client';
import { DocumentRecord } from '../types';

export interface ResumeUploadResponse extends DocumentRecord {
  task_id?: string;
}

export const resumesApi = {
  uploadResume: async (file: File, candidateId?: number, jobId?: number): Promise<ResumeUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (candidateId) formData.append('candidate_id', candidateId.toString());
    if (jobId) formData.append('job_id', jobId.toString());

    const res = await apiClient.post('/resumes/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  getResumeStatus: async (documentId: number): Promise<DocumentRecord> => {
    const res = await apiClient.get(`/resumes/${documentId}/status/`);
    return res.data;
  },
};
