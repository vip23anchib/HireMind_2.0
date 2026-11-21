import { apiClient } from './client';
import { SearchResponse, MatchAnalysisResponse } from '../types';

export const searchApi = {
  searchCandidates: async (params: {
    skill?: string;
    search_type?: 'and' | 'or';
    min_experience?: number;
    job_id?: number;
  }): Promise<SearchResponse> => {
    const res = await apiClient.get('/search/candidates/', { params });
    return res.data;
  },

  getCandidateJobMatch: async (candidateId: number, jobId: number): Promise<MatchAnalysisResponse> => {
    const res = await apiClient.get('/search/matches/', {
      params: {
        candidate_id: candidateId,
        job_id: jobId,
      },
    });
    return res.data;
  },
};
