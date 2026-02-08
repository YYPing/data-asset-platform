<template>
  <div class="asset-detail-container">
    <el-page-header @back="handleBack" content="资产详情" />

    <div v-loading="loading" class="detail-content">
      <!-- 基本信息 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">基本信息</span>
            <div class="card-actions">
              <el-button
                v-if="assetData?.status === 'draft'"
                type="primary"
                :icon="Edit"
                @click="handleEdit"
              >
                编辑
              </el-button>
              <el-button
                v-if="assetData?.status === 'draft'"
                type="success"
                :icon="Upload"
                @click="handleSubmit"
              >
                提交审批
              </el-button>
            </div>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="资产编号">
            {{ assetData?.asset_code || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="资产名称">
            {{ assetData?.asset_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="所属组织">
            {{ assetData?.organization_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="资产分类">
            {{ getCategoryLabel(assetData?.category) }}
          </el-descriptions-item>
          <el-descriptions-item label="数据分级">
            {{ assetData?.data_classification || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="敏感级别">
            {{ assetData?.sensitivity_level || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="资产类型">
            {{ assetData?.asset_type || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="估值">
            {{ assetData?.estimated_value ? `¥${assetData.estimated_value.toLocaleString()}` : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="数据来源">
            {{ assetData?.data_source || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="数据量">
            {{ assetData?.data_volume || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="数据格式">
            {{ assetData?.data_format || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="更新频率">
            {{ assetData?.update_frequency || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="当前阶段">
            <el-tag :type="getStageTagType(assetData?.current_stage)">
              {{ getStageLabel(assetData?.current_stage) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(assetData?.status)">
              {{ getStatusLabel(assetData?.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="版本号">
            {{ assetData?.version || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(assetData?.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(assetData?.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ assetData?.description || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 材料列表 -->
      <el-card class="materials-card" shadow="never">
        <template #header>
          <span class="card-title">材料清单</span>
        </template>

        <el-tabs v-model="activeStage" @tab-change="handleStageChange">
          <el-tab-pane
            v-for="stage in stages"
            :key="stage.value"
            :label="stage.label"
            :name="stage.value"
          >
            <div v-loading="materialsLoading" class="materials-content">
              <!-- 材料清单 -->
              <div v-if="currentChecklist" class="checklist-section">
                <h4>必需材料</h4>
                <el-table :data="currentChecklist.required_materials" border>
                  <el-table-column prop="name" label="材料名称" />
                  <el-table-column label="是否必需" width="100">
                    <template #default="{ row }">
                      <el-tag :type="row.is_required ? 'danger' : 'info'" size="small">
                        {{ row.is_required ? '必需' : '可选' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="上传状态" width="100">
                    <template #default="{ row }">
                      <el-tag :type="row.uploaded ? 'success' : 'warning'" size="small">
                        {{ row.uploaded ? '已上传' : '未上传' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>

              <!-- 已上传文件 -->
              <div class="uploaded-files-section">
                <h4>已上传文件</h4>
                <el-table
                  v-if="currentMaterials.length > 0"
                  :data="currentMaterials"
                  border
                >
                  <el-table-column prop="material_name" label="文件名称" />
                  <el-table-column prop="material_type" label="文件类型" width="120" />
                  <el-table-column label="文件大小" width="120">
                    <template #default="{ row }">
                      {{ formatFileSize(row.file_size) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="uploaded_by" label="上传人" width="120" />
                  <el-table-column label="上传时间" width="180">
                    <template #default="{ row }">
                      {{ formatDate(row.uploaded_at) }}
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="100">
                    <template #default="{ row }">
                      <el-button type="primary" link @click="handleDownload(row)">
                        下载
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
                <el-empty
                  v-else
                  description="暂无上传文件"
                  :image-size="100"
                />
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>

      <!-- 审批历史 -->
      <el-card class="approval-card" shadow="never">
        <template #header>
          <span class="card-title">审批历史</span>
        </template>
        <el-timeline>
          <el-timeline-item
            timestamp="2024-01-15 10:30"
            placement="top"
            type="success"
          >
            <el-card>
              <h4>资产创建</h4>
              <p>创建人：张三</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item
            timestamp="2024-01-16 14:20"
            placement="top"
            type="primary"
          >
            <el-card>
              <h4>提交审批</h4>
              <p>提交人：张三</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item
            timestamp="待审批"
            placement="top"
            type="info"
            hollow
          >
            <el-card>
              <p>等待审批中...</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Upload } from '@element-plus/icons-vue'
import {
  getAssetDetail,
  getMaterialList,
  getMaterialChecklist,
  submitAsset,
  type Asset,
  type Material,
  type MaterialChecklist
} from '@/api/asset'

const route = useRoute()
const router = useRouter()

// ==================== 状态管理 ====================

const loading = ref(false)
const materialsLoading = ref(false)
const assetData = ref<Asset | null>(null)
const allMaterials = ref<Material[]>([])
const activeStage = ref('registration')
const currentChecklist = ref<MaterialChecklist | null>(null)

const stages = [
  { label: '登记', value: 'registration' },
  { label: '盘点', value: 'inventory' },
  { label: '评估', value: 'evaluation' },
  { label: '入表', value: 'cataloging' }
]

// ==================== 计算属性 ====================

const assetId = computed(() => {
  return Number(route.params.id)
})

const currentMaterials = computed(() => {
  return allMaterials.value.filter(m => m.stage === activeStage.value)
})

// ==================== 生命周期 ====================

onMounted(() => {
  loadAssetDetail()
  loadMaterials()
})

// ==================== 数据加载 ====================

const loadAssetDetail = async () => {
  loading.value = true
  try {
    const res = await getAssetDetail(assetId.value)
    assetData.value = res
    if (res.current_stage) {
      activeStage.value = res.current_stage
    }
  } catch (error) {
    ElMessage.error('加载资产详情失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadMaterials = async () => {
  try {
    const res = await getMaterialList(assetId.value)
    allMaterials.value = res
  } catch (error) {
    console.error('加载材料列表失败', error)
  }
}

const loadMaterialChecklist = async (stage: string) => {
  materialsLoading.value = true
  try {
    const res = await getMaterialChecklist(stage)
    currentChecklist.value = res
  } catch (error) {
    console.error('加载材料清单失败', error)
  } finally {
    materialsLoading.value = false
  }
}

// ==================== 事件处理 ====================

const handleBack = () => {
  router.push('/assets')
}

const handleEdit = () => {
  router.push(`/assets/${assetId.value}/edit`)
}

const handleSubmit = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要提交资产"${assetData.value?.asset_name}"进行审批吗？`,
      '提交确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    loading.value = true
    await submitAsset(assetId.value)
    ElMessage.success('提交成功')
    loadAssetDetail()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '提交失败')
      console.error(error)
    }
  } finally {
    loading.value = false
  }
}

const handleStageChange = (stage: string | number) => {
  loadMaterialChecklist(stage as string)
}

const handleDownload = (material: Material) => {
  // 实现文件下载逻辑
  window.open(material.file_path, '_blank')
}

// ==================== 辅助函数 ====================

const getCategoryLabel = (category?: string) => {
  if (!category) return '-'
  const map: Record<string, string> = {
    business: '业务数据',
    technical: '技术数据',
    management: '管理数据'
  }
  return map[category] || category
}

const getStageLabel = (stage?: string) => {
  if (!stage) return '-'
  const map: Record<string, string> = {
    registration: '登记',
    inventory: '盘点',
    evaluation: '评估',
    cataloging: '入表'
  }
  return map[stage] || stage
}

const getStageTagType = (stage?: string) => {
  if (!stage) return ''
  const map: Record<string, any> = {
    registration: '',
    inventory: 'warning',
    evaluation: 'success',
    cataloging: 'info'
  }
  return map[stage] || ''
}

const getStatusLabel = (status?: string) => {
  if (!status) return '-'
  const map: Record<string, string> = {
    draft: '草稿',
    pending: '待审批',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return map[status] || status
}

const getStatusTagType = (status?: string) => {
  if (!status) return ''
  const map: Record<string, any> = {
    draft: 'info',
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return map[status] || ''
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 初始加载材料清单
loadMaterialChecklist(activeStage.value)
</script>

<style scoped lang="scss">
.asset-detail-container {
  padding: 20px;

  .el-page-header {
    margin-bottom: 20px;
  }

  .detail-content {
    .info-card,
    .materials-card,
    .approval-card {
      margin-bottom: 20px;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .card-title {
        font-size: 16px;
        font-weight: bold;
      }
    }

    .card-title {
      font-size: 16px;
      font-weight: bold;
    }

    .materials-content {
      .checklist-section,
      .uploaded-files-section {
        margin-bottom: 20px;

        h4 {
          margin-bottom: 10px;
          font-size: 14px;
          color: #606266;
        }
      }
    }
  }
}
</style>
