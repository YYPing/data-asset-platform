/**
 * 材料相关类型定义
 */

// 材料类型
export type MaterialType = 
  | 'document'      // 文档
  | 'image'         // 图片
  | 'video'         // 视频
  | 'audio'         // 音频
  | 'archive'       // 压缩包
  | 'data'          // 数据文件
  | 'certificate'   // 证书
  | 'other'         // 其他

// 材料状态
export type MaterialStatus = 
  | 'uploading'     // 上传中
  | 'processing'    // 处理中
  | 'completed'     // 已完成
  | 'failed'        // 失败
  | 'deleted'       // 已删除

// 材料阶段
export type MaterialStage = 'registration' | 'inventory' | 'evaluation' | 'cataloging'

// 材料信息
export interface Material {
  id: number
  asset_id: number
  material_name: string
  material_type: MaterialType
  stage: MaterialStage
  file_path: string
  file_size: number
  file_hash?: string
  mime_type?: string
  status: MaterialStatus
  uploaded_by: string
  uploaded_by_name?: string
  uploaded_at: string
  description?: string
  metadata?: Record<string, any>
}

// 材料上传参数
export interface MaterialUploadParams {
  asset_id: number
  stage: MaterialStage
  material_type: MaterialType
  file: File
  description?: string
  onProgress?: (progress: number) => void
}

// 材料上传响应
export interface MaterialUploadResponse {
  material: Material
  upload_id?: string
}

// 分片上传参数
export interface ChunkUploadParams {
  file: File
  chunk_size?: number
  onProgress?: (progress: number) => void
  onChunkComplete?: (chunk: number, total: number) => void
}

// 分片信息
export interface ChunkInfo {
  chunk_index: number
  chunk_size: number
  total_chunks: number
  file_hash: string
  upload_id: string
}

// 材料清单项
export interface MaterialChecklistItem {
  name: string
  material_type: MaterialType
  is_required: boolean
  uploaded: boolean
  material?: Material
  description?: string
}

// 材料清单
export interface MaterialChecklist {
  stage: MaterialStage
  required_materials: MaterialChecklistItem[]
  optional_materials: MaterialChecklistItem[]
  completion_rate: number
}

// 材料预览信息
export interface MaterialPreview {
  id: number
  material_name: string
  material_type: MaterialType
  preview_url?: string
  download_url: string
  file_size: number
  can_preview: boolean
}

// 材料列表查询参数
export interface MaterialListParams {
  asset_id?: number
  stage?: MaterialStage
  material_type?: MaterialType
  status?: MaterialStatus
  page?: number
  page_size?: number
}

// 材料列表响应
export interface MaterialListResponse {
  items: Material[]
  total: number
  page: number
  page_size: number
}

// 文件哈希计算进度
export interface HashProgress {
  loaded: number
  total: number
  percentage: number
  hash?: string
}

// 上传进度信息
export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
  speed?: number
  remaining_time?: number
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed'
  error?: string
}

// 材料验证规则
export interface MaterialValidation {
  max_size?: number
  allowed_types?: string[]
  allowed_extensions?: string[]
  min_size?: number
}

// 材料批量操作
export interface MaterialBatchOperation {
  ids: number[]
  operation: 'delete' | 'download' | 'move'
  target_stage?: MaterialStage
}
