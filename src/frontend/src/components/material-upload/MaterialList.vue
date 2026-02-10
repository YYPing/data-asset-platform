<template>
  <div class="material-list-container">
    <!-- 筛选栏 -->
    <div v-if="showFilters" class="material-filters">
      <el-form :model="filters" inline>
        <el-form-item label="材料类型">
          <el-select
            v-model="filters.material_type"
            placeholder="全部"
            clearable
            style="width: 150px"
            @change="handleFilter"
          >
            <el-option label="文档" value="document" />
            <el-option label="图片" value="image" />
            <el-option label="视频" value="video" />
            <el-option label="音频" value="audio" />
            <el-option label="压缩包" value="archive" />
            <el-option label="数据文件" value="data" />
            <el-option label="证书" value="certificate" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filters.status"
            placeholder="全部"
            clearable
            style="width: 150px"
            @change="handleFilter"
          >
            <el-option label="已完成" value="completed" />
            <el-option label="上传中" value="uploading" />
            <el-option label="处理中" value="processing" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- 材料列表 -->
    <div v-loading="loading" class="material-grid" :class="{ 'list-view': viewMode === 'list' }">
      <div
        v-for="material in materials"
        :key="material.id"
        class="material-card"
        @click="handlePreview(material)"
      >
        <div class="material-preview">
          <el-image
            v-if="material.material_type === 'image'"
            :src="getPreviewUrl(material)"
            fit="cover"
            class="preview-image"
            lazy
          >
            <template #error>
              <div class="image-error">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
          <div v-else class="preview-icon">
            <el-icon :size="48">
              <component :is="getMaterialIcon(material.material_type)" />
            </el-icon>
          </div>

          <div class="material-overlay">
            <el-button-group>
              <el-button
                v-if="canPreview(material)"
                type="primary"
                :icon="View"
                circle
                @click.stop="handlePreview(material)"
              />
              <el-button
                type="success"
                :icon="Download"
                circle
                @click.stop="handleDownload(material)"
              />
              <el-button
                v-if="canDelete"
                type="danger"
                :icon="Delete"
                circle
                @click.stop="handleDelete(material)"
              />
            </el-button-group>
          </div>
        </div>

        <div class="material-info">
          <div class="material-name" :title="material.material_name">
            {{ material.material_name }}
          </div>
          <div class="material-meta">
            <el-tag :type="getMaterialStatusType(material.status)" size="small">
              {{ getMaterialStatusLabel(material.status) }}
            </el-tag>
            <span class="material-size">{{ formatFileSize(material.file_size) }}</span>
          </div>
          <div v-if="material.uploaded_by_name" class="material-uploader">
            <el-icon><User /></el-icon>
            <span>{{ material.uploaded_by_name }}</span>
          </div>
          <div class="material-time">
            {{ formatDateTime(material.uploaded_at) }}
          </div>
        </div>
      </div>
    </div>

    <el-empty v-if="!loading && materials.length === 0" description="暂无材料" />

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      :title="previewMaterial?.material_name"
      width="80%"
      destroy-on-close
      @close="handleClosePreview"
    >
      <div v-if="previewMaterial" class="preview-container">
        <!-- 图片预览 -->
        <el-image
          v-if="previewMaterial.material_type === 'image'"
          :src="getPreviewUrl(previewMaterial)"
          fit="contain"
          class="preview-content"
        />

        <!-- PDF预览 -->
        <iframe
          v-else-if="getFileExtension(previewMaterial.material_name) === 'pdf'"
          :src="getPreviewUrl(previewMaterial)"
          class="preview-content"
          frameborder="0"
        />

        <!-- 视频预览 -->
        <video
          v-else-if="previewMaterial.material_type === 'video'"
          :src="getPreviewUrl(previewMaterial)"
          controls
          class="preview-content"
        />

        <!-- 音频预览 -->
        <audio
          v-else-if="previewMaterial.material_type === 'audio'"
          :src="getPreviewUrl(previewMaterial)"
          controls
          class="preview-content"
        />

        <!-- 文本预览 -->
        <div
          v-else-if="['txt', 'md'].includes(getFileExtension(previewMaterial.material_name))"
          class="preview-content text-preview"
        >
          <pre>{{ previewContent }}</pre>
        </div>

        <!-- 不支持预览 -->
        <div v-else class="preview-not-supported">
          <el-icon :size="64"><Document /></el-icon>
          <p>该文件类型不支持预览</p>
          <el-button type="primary" @click="handleDownload(previewMaterial)">
            下载文件
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  View,
  Download,
  Delete,
  User,
  Picture,
  Document,
  VideoCamera,
  Headset,
  FolderOpened,
  DataLine,
  Medal,
  Files
} from '@element-plus/icons-vue'
import {
  formatFileSize,
  formatDateTime,
  getMaterialStatusLabel,
  getMaterialStatusType,
  canPreviewFile,
  getPreviewUrl as getPreviewUrlHelper,
  getDownloadUrl,
  getFileExtension
} from '@/utils/material-helper'
import { getAssetMaterials, deleteMaterial, downloadMaterial } from '@/api/material'
import type { Material, MaterialType, MaterialStatus, MaterialStage } from '@/types/material'

interface Props {
  assetId?: number
  stage?: MaterialStage
  materials?: Material[]
  showFilters?: boolean
  viewMode?: 'grid' | 'list'
  canDelete?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showFilters: true,
  viewMode: 'grid',
  canDelete: true
})

const emit = defineEmits<{
  refresh: []
  delete: [material: Material]
}>()

// ==================== 状态管理 ====================

const loading = ref(false)
const materials = ref<Material[]>([])
const previewDialogVisible = ref(false)
const previewMaterial = ref<Material | null>(null)
const previewContent = ref('')

const filters = reactive({
  material_type: '' as MaterialType | '',
  status: '' as MaterialStatus | ''
})

// ==================== 生命周期 ====================

onMounted(() => {
  if (props.materials) {
    materials.value = props.materials
  } else if (props.assetId) {
    loadMaterials()
  }
})

// ==================== 数据加载 ====================

const loadMaterials = async () => {
  if (!props.assetId) return

  loading.value = true
  try {
    const res = await getAssetMaterials(props.assetId, props.stage)
    materials.value = res.data
  } catch (error) {
    console.error('Failed to load materials:', error)
    ElMessage.error('加载材料列表失败')
  } finally {
    loading.value = false
  }
}

// ==================== 筛选 ====================

const handleFilter = () => {
  // 如果使用外部数据，通知父组件刷新
  if (props.materials) {
    emit('refresh')
  } else {
    loadMaterials()
  }
}

// ==================== 材料操作 ====================

const handlePreview = async (material: Material) => {
  if (!canPreview(material)) {
    ElMessage.warning('该文件类型不支持预览')
    return
  }

  previewMaterial.value = material
  previewDialogVisible.value = true

  // 如果是文本文件，加载内容
  const ext = getFileExtension(material.material_name)
  if (['txt', 'md'].includes(ext)) {
    try {
      const response = await fetch(getPreviewUrl(material))
      previewContent.value = await response.text()
    } catch (error) {
      console.error('Failed to load preview content:', error)
      ElMessage.error('加载预览内容失败')
    }
  }
}

const handleClosePreview = () => {
  previewMaterial.value = null
  previewContent.value = ''
}

const handleDownload = (material: Material) => {
  downloadMaterial(material.id, material.material_name)
  ElMessage.success('开始下载')
}

const handleDelete = async (material: Material) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除材料"${material.material_name}"吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error'
      }
    )

    loading.value = true
    await deleteMaterial(material.id)
    ElMessage.success('删除成功')
    
    // 从列表中移除
    const index = materials.value.findIndex(m => m.id === material.id)
    if (index > -1) {
      materials.value.splice(index, 1)
    }

    emit('delete', material)
    emit('refresh')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to delete material:', error)
      ElMessage.error(error.message || '删除失败')
    }
  } finally {
    loading.value = false
  }
}

// ==================== 辅助函数 ====================

const getMaterialIcon = (type: MaterialType) => {
  const iconMap: Record<MaterialType, any> = {
    document: Document,
    image: Picture,
    video: VideoCamera,
    audio: Headset,
    archive: FolderOpened,
    data: DataLine,
    certificate: Medal,
    other: Files
  }
  return iconMap[type] || Files
}

const canPreview = (material: Material): boolean => {
  return canPreviewFile(material)
}

const getPreviewUrl = (material: Material): string => {
  return getPreviewUrlHelper(material) || getDownloadUrl(material)
}

// 暴露方法给父组件
defineExpose({
  refresh: loadMaterials
})
</script>

<style scoped lang="scss">
.material-list-container {
  .material-filters {
    margin-bottom: 20px;
    padding: 16px;
    background-color: var(--el-fill-color-light);
    border-radius: 4px;
  }

  .material-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 20px;

    &.list-view {
      grid-template-columns: 1fr;
    }

    .material-card {
      border: 1px solid var(--el-border-color);
      border-radius: 8px;
      overflow: hidden;
      background-color: var(--el-fill-color-blank);
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);

        .material-overlay {
          opacity: 1;
        }
      }

      .material-preview {
        position: relative;
        width: 100%;
        height: 180px;
        background-color: var(--el-fill-color-light);
        display: flex;
        align-items: center;
        justify-content: center;

        .preview-image {
          width: 100%;
          height: 100%;
        }

        .image-error {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 100%;
          height: 100%;
          font-size: 48px;
          color: var(--el-text-color-placeholder);
        }

        .preview-icon {
          font-size: 48px;
          color: var(--el-text-color-secondary);
        }

        .material-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.6);
          display: flex;
          align-items: center;
          justify-content: center;
          opacity: 0;
          transition: opacity 0.3s;
        }
      }

      .material-info {
        padding: 12px;

        .material-name {
          font-size: 14px;
          font-weight: 500;
          color: var(--el-text-color-primary);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          margin-bottom: 8px;
        }

        .material-meta {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 8px;

          .material-size {
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
        }

        .material-uploader {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          color: var(--el-text-color-secondary);
          margin-bottom: 4px;
        }

        .material-time {
          font-size: 12px;
          color: var(--el-text-color-placeholder);
        }
      }
    }
  }

  .preview-container {
    width: 100%;
    height: 70vh;
    display: flex;
    align-items: center;
    justify-content: center;

    .preview-content {
      max-width: 100%;
      max-height: 100%;
      width: 100%;
      height: 100%;
      object-fit: contain;

      &.text-preview {
        overflow: auto;
        padding: 20px;
        background-color: var(--el-fill-color-light);
        border-radius: 4px;

        pre {
          margin: 0;
          font-family: 'Courier New', monospace;
          font-size: 14px;
          line-height: 1.6;
          white-space: pre-wrap;
          word-wrap: break-word;
        }
      }
    }

    .preview-not-supported {
      text-align: center;

      p {
        margin: 20px 0;
        font-size: 16px;
        color: var(--el-text-color-secondary);
      }
    }
  }
}
</style>
