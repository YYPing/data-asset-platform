/**
 * 材料相关API
 */

import request from './request'
import type {
  Material,
  MaterialUploadParams,
  MaterialUploadResponse,
  MaterialListParams,
  MaterialListResponse,
  MaterialChecklist,
  MaterialPreview,
  MaterialBatchOperation,
  ChunkInfo
} from '@/types/material'

// ==================== 材料上传 ====================

/**
 * 上传材料（单文件）
 */
export function uploadMaterial(params: MaterialUploadParams) {
  const formData = new FormData()
  formData.append('file', params.file)
  formData.append('asset_id', String(params.asset_id))
  formData.append('stage', params.stage)
  formData.append('material_type', params.material_type)
  
  if (params.description) {
    formData.append('description', params.description)
  }

  return request<MaterialUploadResponse>({
    url: '/materials/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (params.onProgress && progressEvent.total) {
        const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        params.onProgress(percentage)
      }
    }
  })
}

/**
 * 初始化分片上传
 */
export function initChunkUpload(data: {
  asset_id: number
  stage: string
  material_type: string
  file_name: string
  file_size: number
  file_hash: string
  total_chunks: number
}) {
  return request<{ upload_id: string; existing_chunks: number[] }>({
    url: '/materials/chunk/init',
    method: 'post',
    data
  })
}

/**
 * 上传文件分片
 */
export function uploadChunk(data: {
  upload_id: string
  chunk_index: number
  chunk_data: Blob
  onProgress?: (progress: number) => void
}) {
  const formData = new FormData()
  formData.append('upload_id', data.upload_id)
  formData.append('chunk_index', String(data.chunk_index))
  formData.append('chunk', data.chunk_data)

  return request<{ success: boolean }>({
    url: '/materials/chunk/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (data.onProgress && progressEvent.total) {
        const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        data.onProgress(percentage)
      }
    }
  })
}

/**
 * 完成分片上传
 */
export function completeChunkUpload(data: {
  upload_id: string
  description?: string
}) {
  return request<Material>({
    url: '/materials/chunk/complete',
    method: 'post',
    data
  })
}

/**
 * 取消分片上传
 */
export function cancelChunkUpload(uploadId: string) {
  return request({
    url: '/materials/chunk/cancel',
    method: 'post',
    data: { upload_id: uploadId }
  })
}

// ==================== 材料管理 ====================

/**
 * 获取材料列表
 */
export function getMaterialList(params: MaterialListParams) {
  return request<MaterialListResponse>({
    url: '/materials',
    method: 'get',
    params
  })
}

/**
 * 获取资产的材料列表
 */
export function getAssetMaterials(assetId: number, stage?: string) {
  return request<Material[]>({
    url: `/materials/asset/${assetId}`,
    method: 'get',
    params: { stage }
  })
}

/**
 * 获取材料详情
 */
export function getMaterialDetail(id: number) {
  return request<Material>({
    url: `/materials/${id}`,
    method: 'get'
  })
}

/**
 * 更新材料信息
 */
export function updateMaterial(id: number, data: {
  material_name?: string
  description?: string
  material_type?: string
}) {
  return request<Material>({
    url: `/materials/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除材料
 */
export function deleteMaterial(id: number) {
  return request({
    url: `/materials/${id}`,
    method: 'delete'
  })
}

/**
 * 批量删除材料
 */
export function batchDeleteMaterials(ids: number[]) {
  return request({
    url: '/materials/batch/delete',
    method: 'post',
    data: { ids }
  })
}

// ==================== 材料清单 ====================

/**
 * 获取材料清单
 */
export function getMaterialChecklist(assetId: number, stage: string) {
  return request<MaterialChecklist>({
    url: `/materials/checklist/${assetId}/${stage}`,
    method: 'get'
  })
}

/**
 * 获取阶段材料模板
 */
export function getStageMaterialTemplate(stage: string) {
  return request<{
    stage: string
    required_materials: Array<{
      name: string
      material_type: string
      description: string
    }>
    optional_materials: Array<{
      name: string
      material_type: string
      description: string
    }>
  }>({
    url: `/materials/template/${stage}`,
    method: 'get'
  })
}

// ==================== 材料预览和下载 ====================

/**
 * 获取材料预览信息
 */
export function getMaterialPreview(id: number) {
  return request<MaterialPreview>({
    url: `/materials/${id}/preview`,
    method: 'get'
  })
}

/**
 * 获取材料下载URL
 */
export function getMaterialDownloadUrl(id: number): string {
  return `/api/v1/materials/${id}/download`
}

/**
 * 下载材料
 */
export function downloadMaterial(id: number, filename?: string) {
  const url = getMaterialDownloadUrl(id)
  const link = document.createElement('a')
  link.href = url
  if (filename) {
    link.download = filename
  }
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * 批量下载材料
 */
export function batchDownloadMaterials(ids: number[]) {
  return request<{ download_url: string }>({
    url: '/materials/batch/download',
    method: 'post',
    data: { ids }
  })
}

// ==================== 材料验证 ====================

/**
 * 验证材料哈希
 */
export function verifyMaterialHash(id: number, hash: string) {
  return request<{ valid: boolean; stored_hash: string }>({
    url: `/materials/${id}/verify`,
    method: 'post',
    data: { hash }
  })
}

/**
 * 检查文件是否已存在（秒传）
 */
export function checkFileExists(hash: string, size: number) {
  return request<{
    exists: boolean
    material_id?: number
    can_reuse: boolean
  }>({
    url: '/materials/check',
    method: 'post',
    data: { hash, size }
  })
}

// ==================== 材料统计 ====================

/**
 * 获取材料统计信息
 */
export function getMaterialStatistics(assetId?: number) {
  return request<{
    total: number
    by_type: Record<string, number>
    by_stage: Record<string, number>
    by_status: Record<string, number>
    total_size: number
  }>({
    url: '/materials/statistics',
    method: 'get',
    params: { asset_id: assetId }
  })
}
