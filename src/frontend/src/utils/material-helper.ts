/**
 * 材料相关工具函数
 */

import type {
  Material,
  MaterialType,
  MaterialStatus,
  MaterialStage,
  HashProgress,
  UploadProgress
} from '@/types/material'
import SparkMD5 from 'spark-md5'

// ==================== 标签映射 ====================

/**
 * 获取材料类型标签
 */
export function getMaterialTypeLabel(type: MaterialType | undefined): string {
  const map: Record<MaterialType, string> = {
    document: '文档',
    image: '图片',
    video: '视频',
    audio: '音频',
    archive: '压缩包',
    data: '数据文件',
    certificate: '证书',
    other: '其他'
  }
  return type ? map[type] || type : '-'
}

/**
 * 获取材料类型图标
 */
export function getMaterialTypeIcon(type: MaterialType | undefined): string {
  const map: Record<MaterialType, string> = {
    document: 'Document',
    image: 'Picture',
    video: 'VideoCamera',
    audio: 'Headset',
    archive: 'FolderOpened',
    data: 'DataLine',
    certificate: 'Medal',
    other: 'Files'
  }
  return type ? map[type] || 'Files' : 'Files'
}

/**
 * 获取材料状态标签
 */
export function getMaterialStatusLabel(status: MaterialStatus | undefined): string {
  const map: Record<MaterialStatus, string> = {
    uploading: '上传中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
    deleted: '已删除'
  }
  return status ? map[status] || status : '-'
}

/**
 * 获取材料状态标签类型
 */
export function getMaterialStatusType(status: MaterialStatus | undefined): 'success' | 'warning' | 'danger' | 'info' | '' {
  const map: Record<MaterialStatus, 'success' | 'warning' | 'danger' | 'info' | ''> = {
    uploading: 'warning',
    processing: 'info',
    completed: 'success',
    failed: 'danger',
    deleted: 'info'
  }
  return status ? map[status] || '' : ''
}

/**
 * 获取材料阶段标签
 */
export function getMaterialStageLabel(stage: MaterialStage | undefined): string {
  const map: Record<MaterialStage, string> = {
    registration: '登记',
    inventory: '盘点',
    evaluation: '评估',
    cataloging: '入表'
  }
  return stage ? map[stage] || stage : '-'
}

// ==================== 文件处理 ====================

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number | undefined): string {
  if (!bytes || bytes === 0) return '0 B'
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${units[i]}`
}

/**
 * 获取文件扩展名
 */
export function getFileExtension(filename: string): string {
  const parts = filename.split('.')
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : ''
}

/**
 * 根据文件名推断材料类型
 */
export function inferMaterialType(filename: string, mimeType?: string): MaterialType {
  const ext = getFileExtension(filename)
  
  // 图片
  if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'].includes(ext)) {
    return 'image'
  }
  
  // 文档
  if (['doc', 'docx', 'pdf', 'txt', 'md', 'rtf', 'odt'].includes(ext)) {
    return 'document'
  }
  
  // 视频
  if (['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm'].includes(ext)) {
    return 'video'
  }
  
  // 音频
  if (['mp3', 'wav', 'flac', 'aac', 'ogg', 'wma'].includes(ext)) {
    return 'audio'
  }
  
  // 压缩包
  if (['zip', 'rar', '7z', 'tar', 'gz', 'bz2'].includes(ext)) {
    return 'archive'
  }
  
  // 数据文件
  if (['csv', 'xlsx', 'xls', 'json', 'xml', 'sql', 'db'].includes(ext)) {
    return 'data'
  }
  
  // 证书
  if (['cer', 'crt', 'pem', 'p12', 'pfx'].includes(ext)) {
    return 'certificate'
  }
  
  return 'other'
}

/**
 * 检查文件是否可以预览
 */
export function canPreviewFile(material: Material): boolean {
  const ext = getFileExtension(material.material_name)
  const previewableExts = [
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', // 图片
    'pdf', 'txt', 'md', // 文档
    'mp4', 'webm', // 视频
    'mp3', 'wav', 'ogg' // 音频
  ]
  return previewableExts.includes(ext)
}

/**
 * 获取预览URL
 */
export function getPreviewUrl(material: Material): string | null {
  if (!canPreviewFile(material)) {
    return null
  }
  
  // 这里应该返回实际的预览URL，可能需要通过API获取
  return `/api/v1/materials/${material.id}/preview`
}

/**
 * 获取下载URL
 */
export function getDownloadUrl(material: Material): string {
  return `/api/v1/materials/${material.id}/download`
}

// ==================== 文件验证 ====================

/**
 * 验证文件大小
 */
export function validateFileSize(file: File, maxSize: number = 100 * 1024 * 1024): { valid: boolean; message?: string } {
  if (file.size > maxSize) {
    return {
      valid: false,
      message: `文件大小不能超过 ${formatFileSize(maxSize)}`
    }
  }
  return { valid: true }
}

/**
 * 验证文件类型
 */
export function validateFileType(file: File, allowedTypes?: string[]): { valid: boolean; message?: string } {
  if (!allowedTypes || allowedTypes.length === 0) {
    return { valid: true }
  }
  
  const ext = getFileExtension(file.name)
  if (!allowedTypes.includes(ext)) {
    return {
      valid: false,
      message: `只允许上传以下类型的文件: ${allowedTypes.join(', ')}`
    }
  }
  
  return { valid: true }
}

/**
 * 验证文件
 */
export function validateFile(
  file: File,
  options: {
    maxSize?: number
    allowedTypes?: string[]
    minSize?: number
  } = {}
): { valid: boolean; message?: string } {
  // 检查最小大小
  if (options.minSize && file.size < options.minSize) {
    return {
      valid: false,
      message: `文件大小不能小于 ${formatFileSize(options.minSize)}`
    }
  }
  
  // 检查最大大小
  const sizeValidation = validateFileSize(file, options.maxSize)
  if (!sizeValidation.valid) {
    return sizeValidation
  }
  
  // 检查文件类型
  const typeValidation = validateFileType(file, options.allowedTypes)
  if (!typeValidation.valid) {
    return typeValidation
  }
  
  return { valid: true }
}

// ==================== 文件哈希计算 ====================

/**
 * 计算文件MD5哈希
 */
export function calculateFileHash(
  file: File,
  onProgress?: (progress: HashProgress) => void
): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunkSize = 2 * 1024 * 1024 // 2MB chunks
    const chunks = Math.ceil(file.size / chunkSize)
    let currentChunk = 0
    const spark = new SparkMD5.ArrayBuffer()
    const fileReader = new FileReader()

    fileReader.onload = (e) => {
      if (!e.target?.result) {
        reject(new Error('Failed to read file'))
        return
      }

      spark.append(e.target.result as ArrayBuffer)
      currentChunk++

      if (onProgress) {
        onProgress({
          loaded: currentChunk * chunkSize,
          total: file.size,
          percentage: Math.min((currentChunk / chunks) * 100, 100)
        })
      }

      if (currentChunk < chunks) {
        loadNext()
      } else {
        const hash = spark.end()
        if (onProgress) {
          onProgress({
            loaded: file.size,
            total: file.size,
            percentage: 100,
            hash
          })
        }
        resolve(hash)
      }
    }

    fileReader.onerror = () => {
      reject(new Error('Failed to read file'))
    }

    function loadNext() {
      const start = currentChunk * chunkSize
      const end = Math.min(start + chunkSize, file.size)
      fileReader.readAsArrayBuffer(file.slice(start, end))
    }

    loadNext()
  })
}

// ==================== 分片上传 ====================

/**
 * 将文件分片
 */
export function sliceFile(file: File, chunkSize: number = 2 * 1024 * 1024): Blob[] {
  const chunks: Blob[] = []
  let start = 0
  
  while (start < file.size) {
    const end = Math.min(start + chunkSize, file.size)
    chunks.push(file.slice(start, end))
    start = end
  }
  
  return chunks
}

/**
 * 计算上传速度
 */
export function calculateUploadSpeed(loaded: number, startTime: number): number {
  const elapsed = (Date.now() - startTime) / 1000 // 秒
  return elapsed > 0 ? loaded / elapsed : 0
}

/**
 * 计算剩余时间
 */
export function calculateRemainingTime(loaded: number, total: number, speed: number): number {
  if (speed === 0) return 0
  const remaining = total - loaded
  return remaining / speed
}

/**
 * 格式化时间（秒）
 */
export function formatTime(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}秒`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    const secs = Math.round(seconds % 60)
    return `${minutes}分${secs}秒`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}小时${minutes}分`
  }
}

/**
 * 格式化速度
 */
export function formatSpeed(bytesPerSecond: number): string {
  return `${formatFileSize(bytesPerSecond)}/s`
}

// ==================== 材料清单 ====================

/**
 * 计算材料清单完成率
 */
export function calculateCompletionRate(required: number, uploaded: number): number {
  if (required === 0) return 100
  return Math.round((uploaded / required) * 100)
}

/**
 * 检查材料清单是否完整
 */
export function isChecklistComplete(requiredCount: number, uploadedCount: number): boolean {
  return uploadedCount >= requiredCount
}

// ==================== 拖拽上传 ====================

/**
 * 从拖拽事件中提取文件
 */
export function extractFilesFromDragEvent(event: DragEvent): File[] {
  const files: File[] = []
  
  if (event.dataTransfer?.items) {
    // 使用 DataTransferItemList 接口
    for (let i = 0; i < event.dataTransfer.items.length; i++) {
      const item = event.dataTransfer.items[i]
      if (item.kind === 'file') {
        const file = item.getAsFile()
        if (file) {
          files.push(file)
        }
      }
    }
  } else if (event.dataTransfer?.files) {
    // 使用 FileList 接口
    for (let i = 0; i < event.dataTransfer.files.length; i++) {
      files.push(event.dataTransfer.files[i])
    }
  }
  
  return files
}

/**
 * 检查是否为拖拽文件事件
 */
export function isDragFileEvent(event: DragEvent): boolean {
  if (!event.dataTransfer) return false
  
  // 检查是否包含文件
  return Array.from(event.dataTransfer.types).includes('Files')
}
