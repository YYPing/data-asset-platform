/**
 * 资产相关类型定义
 */

// 资产状态
export type AssetStatus = 'draft' | 'pending' | 'approved' | 'rejected' | 'archived'

// 资产阶段
export type AssetStage = 'registration' | 'inventory' | 'evaluation' | 'cataloging'

// 资产分类
export type AssetCategory = 'business' | 'technical' | 'management'

// 数据分级
export type DataClassification = 'level1' | 'level2' | 'level3' | 'level4'

// 敏感级别
export type SensitivityLevel = 'public' | 'internal' | 'confidential' | 'top_secret'

// 资产基本信息
export interface Asset {
  id: number
  asset_code: string
  asset_name: string
  organization_id: number
  organization_name?: string
  category: AssetCategory
  data_classification: DataClassification
  sensitivity_level: SensitivityLevel
  description: string
  data_source: string
  data_volume: string
  data_format: string
  update_frequency: string
  current_stage: AssetStage
  status: AssetStatus
  asset_type: string
  estimated_value: number
  version: number
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 资产表单数据
export interface AssetFormData {
  asset_name: string
  organization_id?: number
  category: AssetCategory | ''
  data_classification: DataClassification | ''
  sensitivity_level: SensitivityLevel | ''
  description: string
  data_source: string
  data_volume: string
  data_format: string
  update_frequency: string
  asset_type?: string
  estimated_value?: number
}

// 资产列表查询参数
export interface AssetListParams {
  page?: number
  page_size?: number
  q?: string
  status?: AssetStatus | ''
  stage?: AssetStage | ''
  category?: AssetCategory | ''
  start_date?: string
  end_date?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

// 资产列表响应
export interface AssetListResponse {
  items: Asset[]
  total: number
  page: number
  page_size: number
}

// 资产版本信息
export interface AssetVersion {
  id: number
  asset_id: number
  version: number
  changes: string
  created_by: string
  created_at: string
  snapshot: Partial<Asset>
}

// 资产操作日志
export interface AssetOperationLog {
  id: number
  asset_id: number
  operation: string
  operation_type: 'create' | 'update' | 'delete' | 'submit' | 'approve' | 'reject' | 'archive'
  operator: string
  operator_name?: string
  details: string
  ip_address?: string
  user_agent?: string
  created_at: string
}

// 资产统计信息
export interface AssetStatistics {
  total: number
  by_status: Record<AssetStatus, number>
  by_stage: Record<AssetStage, number>
  by_category: Record<AssetCategory, number>
  total_value: number
  recent_created: number
  recent_updated: number
}

// 资产状态流转选项
export interface AssetStatusTransition {
  from: AssetStatus
  to: AssetStatus
  action: string
  label: string
  icon?: string
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  permission?: string
}

// 资产导出参数
export interface AssetExportParams {
  ids?: number[]
  filters?: AssetListParams
  fields?: string[]
  format?: 'xlsx' | 'csv' | 'pdf'
}

// 批量操作参数
export interface AssetBatchOperation {
  ids: number[]
  operation: 'delete' | 'submit' | 'approve' | 'reject' | 'archive'
  reason?: string
}

// 资产对比结果
export interface AssetComparison {
  field: string
  label: string
  old_value: any
  new_value: any
  changed: boolean
}
