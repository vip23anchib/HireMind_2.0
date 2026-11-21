import { apiClient } from './client';
import {
  DashboardMetrics,
  SkillDistributionItem,
  ExperienceDistributionItem,
  FunnelStage,
} from '../types';

export const analyticsApi = {
  getDashboardSummary: async (): Promise<DashboardMetrics> => {
    const res = await apiClient.get('/analytics/dashboard/');
    return res.data;
  },

  getSkillsDistribution: async (): Promise<SkillDistributionItem[]> => {
    const res = await apiClient.get('/analytics/skills/');
    return res.data;
  },

  getExperienceDistribution: async (): Promise<ExperienceDistributionItem[]> => {
    const res = await apiClient.get('/analytics/experience/');
    return res.data;
  },

  getFunnelMetrics: async (): Promise<FunnelStage[]> => {
    const res = await apiClient.get('/analytics/funnel/');
    return res.data;
  },
};
