<template>
  <div class="material-upload-container">
    <div
      class="upload-area"
      :class="{ 'is-dragover': isDragover, 'is-disabled': disabled }"
      @drop.prevent="handleDrop"
      @dragover.prevent="handleDragover"
      @dragleave.prevent="handleDragleave"
    >
      <el-icon class="upload-icon"><UploadFilled /></el-icon>
      <div class="upload-text">
        <p class="upload-title">将文件拖到此处，或<em>点击上传</em></p>
        <p class="upload-hint">
          <span v-if="accept">支持格式：{{ accept }}</span>
          <span v-if="maxSize">单个文件不超过 {{ formatFileSize(maxSize) }}</span>
        </p>
      </div>
      <input
        ref="fileInputRef"
        type="file"
        :accept="accept"
        :multiple="multiple"
        :disabled="disabled"
        class="upload-input"
        @change="handleFileSelect"
      />
    </div>

    <!-- 文件列表 -->
    <div v-if="fileList.length > 0" class="file-list">
      <div
        v-for="(file, index) in fileList"
        :key="file.uid"
        class="file-item"
        :class="{ 'is-uploading': file.status === 'uploading', 'is-error': file.status === 'error' }"
      >
        <div class="file-info">
          <el-icon class="file-icon">
            <component :is="getFileIcon(file)" />
          </el-icon>
          <div class="file-details">
            <div class="file-name">{{ file.name }}</div>
            <div class="file-meta">
              <span class="file-size">{{ formatFileSize(file.size) }}</span>
              <span v-if="file.hash && showHash" class="file-hash">
                MD5: {{ file.hash.substring(0, 8) }}...
              </span>
            </div>
          </div>
        </div>

        <div class="file-status">
          <!-- 上传进度 -->
          <div v-if="file.status === 'uploading'" class="upload-progress">
            <el-progress
              :percentage="file.progress"
              :status="file.progress === 100 ? 'success' : undefined"
            />
            <div v-if="file.speed" class="upload-stats">
              <span>{{ formatSpeed(file.speed) }}</span>
              <span v-if="file.remainingTime">剩余 {{ formatTime(file.remainingTime) }}</span>
            </div>
          </div>

          <!-- 哈希计算中 -->
          <div v-else-if="file.status === 'hashing'" class="hashing-progress">
            <el-progress :percentage="file.hashProgress || 0" status="warning" />
            <el-text type="warning" size="small">计算文件哈希...</el-text>
          </div>

          <!-- 上传成功 -->
          <div v-else-if="file.status === 'success'" class="upload-success">
            <el-icon color="var(--el-color-success)"><CircleCheck /></el-icon>
            <el-text type="success" size="small">上传成功</el-text>
          </div>

          <!-- 上传失败 -->
          <div v-else-if="file.status === 'error'" class="upload-error">
            <el-icon color="var(--el-color-danger)"><CircleClose /></el-icon>
            <el-text type="danger" size="small">{{ file.error || '上传失败' }}</el-text>
          </div>

          <!-- 等待上传 -->
          <div v-else class="upload-pending">
            <el-text type="info" size="small">等待上传</el-text>
          </div>
        </div>

        <div class="file-actions">
          <el-button
            v-if="file.status === 'pending' || file.status === 'error'"
            type="danger"
            link
            :icon="Delete"
            @click="handleRemove(index)"
          >
            删除
          </el-button>
          <el-button
            v-if="file.status === 'error'"
            type="primary"
            link
            :icon="RefreshRight"
            @click="handleRetry(index)"
          >
            重试
          </el-button>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div v-if="fileList.length > 0" class="upload-actions">
      <el-button
        type="primary"
        :loading="isUploading"
        :disabled="!canUpload"
        @click="handleUpload"
      >
        {{ isUploading ? '上传中...' : '开始上传' }}
      </el-button>
      <el-button
        :disabled="isUploading"
        @click="handleClearAll"
      >
        清空列表
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  UploadFilled,
  Document,
  Picture,
  VideoCamera,
  Headset,
  FolderOpened,
  Files,
  CircleCheck,
  CircleClose,
  Delete,
  RefreshRight
} from '@element-plus/icons-vue'
import {
  formatFileSize,
  formatSpeed,
  formatTime,
  validateFile,
  calculateFileHash,
  inferMaterialType,
  getFileExtension,
  extractFilesFromDragEvent,
  calculateUploadSpeed,
  calculateRemainingTime
} from '@/utils/material-helper'
import { uploadMaterial, initChunkUpload, uploadChunk, completeChunkUpload } from '@/api/material'
import type { MaterialType, MaterialStage } from '@/types/material'

interface FileItem {
  uid: string
  name: string
  size: number
  file: File
  status: 'pending' | 'hashing' | 'uploading' | 'success' | 'error'
  progress: number
  hashProgress?: number
  hash?: string
  speed?: number
  remainingTime?: number
  error?: string
  materialType?: MaterialType
}

interface Props {
  assetId: number
  stage: MaterialStage
  accept?: string
  maxSize?: number
  multiple?: boolean
  disabled?: boolean
  autoUpload?: boolean
  chunkSize?: number
  showHash?: boolean
  enableChunkUpload?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  accept: '',
  maxSize: 100 * 1024 * 1024, // 100MB
  multiple: true,
  disabled: false,
  autoUpload: false,
  chunkSize: 2 * 1024 * 1024, // 2MB
  showHash: true,
  enableChunkUpload: true
})

const emit = defineEmits<{
  success: [file: FileItem, response: any]
  error: [file: FileItem, error: any]
  progress: [file: FileItem, progress: number]
  complete: []
}>()

// ==================== 状态管理 ====================

const fileInputRef = ref<HTMLInputElement>()
const fileList = ref<FileItem[]>([])
const isDragover = ref(false)
const isUploading = ref(false)
const uploadStartTime = ref(0)

// ==================== 计算属性 ====================

const canUpload = computed(() => {
  return fileList.value.some(f => f.status === 'pending' || f.status === 'error')
})

// ==================== 文件选择 ====================

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    addFiles(Array.from(target.files))
    target.value = '' // 清空input，允许重复选择同一文件
  }
}

const handleDrop = (event: DragEvent) => {
  isDragover.value = false
  if (props.disabled) return

  const files = extractFilesFromDragEvent(event)
  if (files.length > 0) {
    addFiles(files)
  }
}

const handleDragover = () => {
  if (!props.disabled) {
    isDragover.value = true
  }
}

const handleDragleave = () => {
  isDragover.value = false
}

// ==================== 文件管理 ====================

const addFiles = (files: File[]) => {
  for (const file of files) {
    // 验证文件
    const validation = validateFile(file, {
      maxSize: props.maxSize,
      allowedTypes: props.accept ? props.accept.split(',').map(t => t.trim().replace('.', '')) : undefined
    })

    if (!validation.valid) {
      ElMessage.error(`${file.name}: ${validation.message}`)
      continue
    }

    // 添加到列表
    const fileItem: FileItem = {
      uid: `${Date.now()}-${Math.random().toString(36).substring(2)}`,
      name: file.name,
      size: file.size,
      file,
      status: 'pending',
      progress: 0,
      materialType: inferMaterialType(file.name)
    }

    fileList.value.push(fileItem)
  }

  // 自动上传
  if (props.autoUpload && fileList.value.some(f => f.status === 'pending')) {
    handleUpload()
  }
}

const handleRemove = (index: number) => {
  fileList.value.splice(index, 1)
}

const handleRetry = (index: number) => {
  const file = fileList.value[index]
  file.status = 'pending'
  file.progress = 0
  file.error = undefined
  uploadFile(file)
}

const handleClearAll = () => {
  fileList.value = fileList.value.filter(f => f.status === 'uploading')
  if (fileList.value.length === 0) {
    fileList.value = []
  }
}

// ==================== 文件上传 ====================

const handleUpload = async () => {
  const pendingFiles = fileList.value.filter(f => f.status === 'pending' || f.status === 'error')
  if (pendingFiles.length === 0) return

  isUploading.value = true
  uploadStartTime.value = Date.now()

  for (const file of pendingFiles) {
    await uploadFile(file)
  }

  isUploading.value = false
  emit('complete')
}

const uploadFile = async (fileItem: FileItem) => {
  try {
    // 1. 计算文件哈希
    if (props.showHash) {
      fileItem.status = 'hashing'
      fileItem.hash = await calculateFileHash(fileItem.file, (progress) => {
        fileItem.hashProgress = progress.percentage
      })
    }

    // 2. 判断是否使用分片上传
    const useChunkUpload = props.enableChunkUpload && fileItem.size > props.chunkSize * 2

    if (useChunkUpload) {
      await uploadFileInChunks(fileItem)
    } else {
      await uploadFileDirectly(fileItem)
    }

    fileItem.status = 'success'
    fileItem.progress = 100
    emit('success', fileItem, null)
  } catch (error: any) {
    fileItem.status = 'error'
    fileItem.error = error.message || '上传失败'
    emit('error', fileItem, error)
  }
}

const uploadFileDirectly = async (fileItem: FileItem) => {
  fileItem.status = 'uploading'
  const startTime = Date.now()

  await uploadMaterial({
    asset_id: props.assetId,
    stage: props.stage,
    material_type: fileItem.materialType || 'other',
    file: fileItem.file,
    onProgress: (progress) => {
      fileItem.progress = progress
      fileItem.speed = calculateUploadSpeed(fileItem.size * progress / 100, startTime)
      fileItem.remainingTime = calculateRemainingTime(
        fileItem.size * progress / 100,
        fileItem.size,
        fileItem.speed
      )
      emit('progress', fileItem, progress)
    }
  })
}

const uploadFileInChunks = async (fileItem: FileItem) => {
  fileItem.status = 'uploading'
  const totalChunks = Math.ceil(fileItem.size / props.chunkSize)
  const startTime = Date.now()

  // 初始化分片上传
  const initRes = await initChunkUpload({
    asset_id: props.assetId,
    stage: props.stage,
    material_type: fileItem.materialType || 'other',
    file_name: fileItem.name,
    file_size: fileItem.size,
    file_hash: fileItem.hash || '',
    total_chunks: totalChunks
  })

  const uploadId = initRes.data.upload_id
  const existingChunks = initRes.data.existing_chunks || []

  // 上传分片
  for (let i = 0; i < totalChunks; i++) {
    if (existingChunks.includes(i)) {
      // 跳过已上传的分片
      continue
    }

    const start = i * props.chunkSize
    const end = Math.min(start + props.chunkSize, fileItem.size)
    const chunk = fileItem.file.slice(start, end)

    await uploadChunk({
      upload_id: uploadId,
      chunk_index: i,
      chunk_data: chunk,
      onProgress: (chunkProgress) => {
        const overallProgress = ((i + chunkProgress / 100) / totalChunks) * 100
        fileItem.progress = Math.round(overallProgress)
        fileItem.speed = calculateUploadSpeed(fileItem.size * overallProgress / 100, startTime)
        fileItem.remainingTime = calculateRemainingTime(
          fileItem.size * overallProgress / 100,
          fileItem.size,
          fileItem.speed
        )
        emit('progress', fileItem, overallProgress)
      }
    })
  }

  // 完成上传
  await completeChunkUpload({
    upload_id: uploadId
  })
}

// ==================== 辅助函数 ====================

const getFileIcon = (file: FileItem) => {
  const ext = getFileExtension(file.name)
  
  if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'].includes(ext)) {
    return Picture
  }
  if (['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'].includes(ext)) {
    return VideoCamera
  }
  if (['mp3', 'wav', 'flac', 'aac', 'ogg'].includes(ext)) {
    return Headset
  }
  if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) {
    return FolderOpened
  }
  if (['doc', 'docx', 'pdf', 'txt'].includes(ext)) {
    return Document
  }
  
  return Files
}

// 暴露方法给父组件
defineExpose({
  addFiles,
  clearAll: handleClearAll,
  upload: handleUpload
})
</script>

<style scoped lang="scss">
.material-upload-container {
  .upload-area {
    position: relative;
    padding: 40px;
    border: 2px dashed var(--el-border-color);
    border-radius: 8px;
    background-color: var(--el-fill-color-lighter);
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      border-color: var(--el-color-primary);
      background-color: var(--el-color-primary-light-9);
    }

    &.is-dragover {
      border-color: var(--el-color-primary);
      background-color: var(--el-color-primary-light-9);
      transform: scale(1.02);
    }

    &.is-disabled {
      cursor: not-allowed;
      opacity: 0.6;
    }

    .upload-icon {
      font-size: 48px;
      color: var(--el-text-color-secondary);
      margin-bottom: 16px;
    }

    .upload-text {
      .upload-title {
        margin: 0 0 8px 0;
        font-size: 16px;
        color: var(--el-text-color-primary);

        em {
          color: var(--el-color-primary);
          font-style: normal;
        }
      }

      .upload-hint {
        margin: 0;
        font-size: 13px;
        color: var(--el-text-color-secondary);

        span {
          margin: 0 8px;
        }
      }
    }

    .upload-input {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      opacity: 0;
      cursor: pointer;

      &:disabled {
        cursor: not-allowed;
      }
    }
  }

  .file-list {
    margin-top: 20px;

    .file-item {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 12px 16px;
      margin-bottom: 8px;
      border: 1px solid var(--el-border-color);
      border-radius: 4px;
      background-color: var(--el-fill-color-blank);
      transition: all 0.3s;

      &:hover {
        background-color: var(--el-fill-color-light);
      }

      &.is-uploading {
        border-color: var(--el-color-primary);
      }

      &.is-error {
        border-color: var(--el-color-danger);
        background-color: var(--el-color-danger-light-9);
      }

      .file-info {
        flex: 1;
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 0;

        .file-icon {
          font-size: 32px;
          color: var(--el-text-color-secondary);
          flex-shrink: 0;
        }

        .file-details {
          flex: 1;
          min-width: 0;

          .file-name {
            font-size: 14px;
            font-weight: 500;
            color: var(--el-text-color-primary);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .file-meta {
            display: flex;
            gap: 12px;
            margin-top: 4px;
            font-size: 12px;
            color: var(--el-text-color-secondary);

            .file-hash {
              font-family: monospace;
            }
          }
        }
      }

      .file-status {
        flex: 0 0 300px;

        .upload-progress,
        .hashing-progress {
          .upload-stats {
            display: flex;
            justify-content: space-between;
            margin-top: 4px;
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
        }

        .upload-success,
        .upload-error,
        .upload-pending {
          display: flex;
          align-items: center;
          gap: 8px;
        }
      }

      .file-actions {
        flex-shrink: 0;
        display: flex;
        gap: 8px;
      }
    }
  }

  .upload-actions {
    margin-top: 20px;
    display: flex;
    gap: 12px;
  }
}
</style>
