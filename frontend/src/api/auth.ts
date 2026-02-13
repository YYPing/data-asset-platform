import api from './client';

export interface LoginParams {
  username: string;
  password: string;
}

export interface RegisterParams {
  username: string;
  password: string;
  real_name?: string;
  role: string;
  org_id?: number;
}

export interface UserInfo {
  id: number;
  username: string;
  real_name: string | null;
  role: string;
  org_id: number | null;
}

export const authApi = {
  login: (data: LoginParams) => {
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  register: (data: RegisterParams) => api.post('/auth/register', data),
  getMe: () => api.get<UserInfo>('/auth/me'),
};
