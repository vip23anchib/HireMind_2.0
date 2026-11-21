import { apiClient } from './client';
import { ActivityLog, PaginatedResponse } from '../types';

export const activityApi = {
  getActivityLogs: async (params?: { page?: number }): Promise<PaginatedResponse<ActivityLog>> => {
    const res = await apiClient.get('/activity-logs/', { params });
    return res.data;
  },
};
