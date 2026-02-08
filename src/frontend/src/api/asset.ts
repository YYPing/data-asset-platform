import request from '@/api/request'

// ==================== 类型定义 ====================

export interface Asset {
  id: number
  asset_code: string
  asset_name: string
  organization_id: number
  organization_name?: string
  category: string
  data_classification: string
  sensitivity_level: string
  description: string
  data_source: string
  data_volume: string
  data_format: string
  update_frequency: string
  current_stage: string
  status: string
  asset_type: string
  estimated_value: number
  version: number
  created_at: string
  updated_at: string
  materials?: Material[]
}

export interface Material {
  id: number
  asset_id: number
  material_name: string
  material_type: string
  stage: string
  file_path: string
  file_size: number
  uploaded_by: string
  uploaded_at: string
}

export interface MaterialChecklistItem {
  name: string
  is_required: boolean
  uploaded: boolean
}

export interface MaterialChecklist {
  stage: string
  required_materials: MaterialChecklistItem[]
}

export interface AssetListParams {
  page?: number
  page_size?: number
  q?: string
  status?: string
  stage?: string
  category?: string
}

export interface AssetListResponse {
  items: Asset[]
  total: number
  page: number
  page_size: number
}

export interface AssetFormData {
  asset_name: string
  organization_id?: number
  category: string
  data_classification: string
  sensitivity_level: string
  description: string
  data_source: string
  data_volume: string
  data_format: string
  update_frequency: string
  asset_type?: string
  estimated_value?: number
}

// ==================== API 函数 ====================

/**
 * 获取资产列表
 */
export function getAssetList(params: AssetListParams) {
  return request<AssetListResponse>({
    url: '/api/v1/assets/',
    method: 'get',
    params
  })
}

/**
 * 获取资产详情
 */
export function getAssetDetail(id: number) {
  return request<Asset>({
    url: `/api/v1/assets/${id}`,
    method: 'get'
  })
}

/**
 * 创建资产（草稿）
 */
export function createAsset(data: AssetFormData) {
  return request<Asset>({
    url: '/api/v1/assets/',
    method: 'post',
    data
  })
}

/**
 * 更新资产
 */
export function updateAsset(id: number, data: AssetFormData) {
  return request<Asset>({
    url: `/api/v1/assets/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除资产
 */
export function deleteAsset(id: number) {
  return request({
    url: `/api/v1/assets/${id}`,
    method: 'delete'
  })
}

/**
 * 提交资产审批
 */
export function submitAsset(id: number) {
  return request<Asset>({
    url: `/api/v1/assets/${id}/submit`,
    method: 'post'
  })
}

/**
 * 上传材料
 */
export function uploadMaterial(data: FormData) {
  return request<Material>({
    url: '/api/v1/materials/upload',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取资产材料列表
 */
export function getMaterialList(assetId: number) {
  return request<Material[]>({
    url: `/api/v1/materials/${assetId}`,
    method: 'get'
  })
}

/**
 * 获取材料清单
 */
export function getMaterialChecklist(stage: string) {
  return request<MaterialChecklist>({
    url: `/api/v1/materials/checklist/${stage}`,
    method: 'get'
  })
}
