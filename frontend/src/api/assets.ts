import api from './client';

export interface Asset {
  id: number;
  name: string;
  description: string | null;
  org_id: number;
  current_stage: string;
  asset_type: string | null;
  data_classification: string | null;
  valuation_amount: number | null;
  accounting_type: string | null;
  created_by: number | null;
}

export interface StageRecord {
  id: number;
  asset_id: number;
  stage: string;
  status: string;
  submitted_by: number | null;
  approved_by: number | null;
  reject_reason: string | null;
}

export interface Material {
  id: number;
  stage_record_id: number;
  file_name: string;
  file_size: number | null;
  file_type: string | null;
  hash_sha256: string;
  version: number;
}

export const assetApi = {
  list: (stage?: string) => api.get<Asset[]>('/assets', { params: stage ? { stage } : {} }),
  get: (id: number) => api.get<Asset>(`/assets/${id}`),
  create: (data: { name: string; description?: string; asset_type?: string; data_classification?: string }) =>
    api.post<Asset>('/assets', data),
};

export const stageApi = {
  submit: (assetId: number) => api.post<StageRecord>(`/stages/${assetId}/submit`),
  approve: (recordId: number) => api.post<StageRecord>(`/stages/records/${recordId}/approve`),
  reject: (recordId: number, reason: string) =>
    api.post<StageRecord>(`/stages/records/${recordId}/reject`, { reason }),
};

export const materialApi = {
  upload: (stageRecordId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<Material>(`/materials/upload/${stageRecordId}`, formData);
  },
  list: (stageRecordId: number) => api.get<Material[]>(`/materials/${stageRecordId}`),
};

export const statsApi = {
  city: () => api.get('/statistics/city'),
  holder: () => api.get('/statistics/holder'),
};

export const auditApi = {
  list: (params?: { action?: string; resource_type?: string; limit?: number }) =>
    api.get('/audit', { params }),
};
