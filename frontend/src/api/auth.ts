import { apiClient } from './client';
import { User } from '../types';

export const authApi = {
  login: async (credentials: { username: string; password: string }): Promise<{ message: string; user: User }> => {
    const res = await apiClient.post('/auth/login/', credentials);
    return res.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout/');
  },

  getCurrentUser: async (): Promise<User> => {
    const res = await apiClient.get('/auth/me/');
    return res.data;
  },

  changePassword: async (passwords: { old_password: string; new_password: string }): Promise<void> => {
    await apiClient.post('/auth/change-password/', passwords);
  },
};
