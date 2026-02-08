<template>
  <div class="asset-form-container">
    <el-page-header @back="handleBack" :content="pageTitle" />

    <div class="form-content">
      <el-card shadow="never">
        <el-form
          ref="formRef"
          v-loading="loading"
          :model="formData"
          :rules="formRules"
          label-width="120px"
        >
          <!-- 基本信息 -->
          <el-divider content-position="left">基本信息</el-divider>

          <el-form-item label="资产名称" prop="asset_name">
            <el-input
              v-model="formData.asset_name"
              placeholder="请输入资产名称"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="资产分类" prop="category">
            <el-select
              v-model="formData.category"
              placeholder="请选择资产分类"
              style="width: 100%"
            >
              <el-option label="业务数据" value="business" />
              <el-option label="技术数据" value="technical" />
              <el-option label="管理数据" value="management" />
            </el-select>
          </el-form-item>

          <el-form-item label="数据分级" prop="data_classification">
            <el-select
              v-model="formData.data_classification"
              placeholder="请选择数据分级"
              style="width: 100%"
            >
              <el-option label="一级" value="level1" />
              <el-option label="二级" value="level2" />
              <el-option label="三级" value="level3" />
              <el-option label="四级" value="level4" />
            </el-select>
          </el-form-item>

          <el-form-item label="敏感级别" prop="sensitivity_level">
            <el-select
              v-model="formData.sensitivity_level"
              placeholder="请选择敏感级别"
              style="width: 100%"
            >
              <el-option label="公开" value="public" />
              <el-option label="内部" value="internal" />
              <el-option label="机密" value="confidential" />
              <el-option label="绝密" value="top_secret" />
            </el-select>
          </el-form-item>

          <el-form-item label="资产类型" prop="asset_type">
            <el-input
              v-model="formData.asset_type"
              placeholder="请输入资产类型"
            />
          </el-form-item>

          <el-form-item label="估值" prop="estimated_value">
            <el-input-number
              v-model="formData.estimated_value"
              :min="0"
              :precision="2"
              :controls="false"
              placeholder="请输入估值"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="描述" prop="description">
            <el-input
              v-model="formData.description"
              type="textarea"
              :rows="4"
              placeholder="请输入资产描述"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <!-- 数据信息 -->
          <el-divider content-position="left">数据信息</el-divider>

          <el-form-item label="数据来源" prop="data_source">
            <el-input
              v-model="formData.data_source"
              placeholder="请输入数据来源"
            />
          </el-form-item>

          <el-form-item label="数据量" prop="data_volume">
            <el-input
              v-model="formData.data_volume"
              placeholder="例如：100GB、1000万条"
            />
          </el-form-item>

          <el-form-item label="数据格式" prop="data_format">
            <el-input
              v-model="formData.data_format"
              placeholder="例如：JSON、CSV、数据库表"
            />
          </el-form-item>

          <el-form-item label="更新频率" prop="update_frequency">
            <el-select
              v-model="formData.update_frequency"
              placeholder="请选择更新频率"
              style="width: 100%"
            >
              <el-option label="实时" value="realtime" />
              <el-option label="每日" value="daily" />
              <el-option label="每周" value="weekly" />
              <el-option label="每月" value="monthly" />
              <el-option label="按需" value="on_demand" />
            </el-select>
          </el-form-item>

          <!-- 材料上传 -->
          <el-divider content-position="left">材料上传</el-divider>

          <el-form-item label="阶段选择">
            <el-radio-group v-model="uploadStage">
              <el-radio label="registration">登记</el-radio>
              <el-radio label="inventory">盘点</el-radio>
              <el-radio label="evaluation">评估</el-radio>
              <el-radio label="cataloging">入表</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="上传文件">
            <el-upload
              ref="uploadRef"
              :action="uploadAction"
              :headers="uploadHeaders"
              :data="uploadData"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :before-upload="beforeUpload"
              :file-list="fileList"
              :auto-upload="false"
              drag
              multiple
            >
              <el-icon class="el-icon--upload">
                <upload-filled />
              </el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持多文件上传，单个文件不超过50MB
                </div>
              </template>
            </el-upload>
          </el-form-item>

          <!-- 已上传文件列表 -->
          <el-form-item v-if="uploadedFiles.length > 0" label="已上传文件">
            <el-table :data="uploadedFiles" border style="width: 100%">
              <el-table-column prop="material_name" label="文件名" />
              <el-table-column prop="stage" label="阶段" width="100">
                <template #default="{ row }">
                  {{ getStageLabel(row.stage) }}
                </template>
              </el-table-column>
              <el-table-column label="大小" width="120">
                <template #default="{ row }">
                  {{ formatFileSize(row.file_size) }}
                </template>
              </el-table-column>
              <el-table-column label="上传时间" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.uploaded_at) }}
                </template>
              </el-table-column>
            </el-table>
          </el-form-item>

          <!-- 操作按钮 -->
          <el-form-item>
            <el-button
              type="primary"
              :loading="submitLoading"
              @click="handleSaveDraft"
            >
              保存草稿
            </el-button>
            <el-button
              type="success"
              :loading="submitLoading"
              @click="handleSaveAndSubmit"
            >
              保存并提交
            </el-button>
            <el-button @click="handleBack">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules, UploadInstance, UploadUserFile } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import {
  getAssetDetail,
  createAsset,
  updateAsset,
  submitAsset,
  uploadMaterial,
  getMaterialList,
  type AssetFormData,
  type Material
} from '@/api/asset'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// ==================== 状态管理 ====================

const loading = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()

const isEdit = computed(() => route.path.includes('/edit'))
const assetId = computed(() => Number(route.params.id))
const pageTitle = computed(() => isEdit.value ? '编辑资产' : '新建资产')

const formData = reactive<AssetFormData>({
  asset_name: '',
  category: '',
  data_classification: '',
  sensitivity_level: '',
  description: '',
  data_source: '',
  data_volume: '',
  data_format: '',
  update_frequency: '',
  asset_type: '',
  estimated_value: undefined
})

const formRules: FormRules = {
  asset_name: [
    { required: true, message: '请输入资产名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择资产分类', trigger: 'change' }
  ],
  data_classification: [
    { required: true, message: '请选择数据分级', trigger: 'change' }
  ],
  sensitivity_level: [
    { required: true, message: '请选择敏感级别', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入资产描述', trigger: 'blur' }
  ]
}

const uploadStage = ref('registration')
const fileList = ref<UploadUserFile[]>([])
const uploadedFiles = ref<Material[]>([])

const uploadAction = computed(() => {
  return `${import.meta.env.VITE_API_BASE_URL}/api/v1/materials/upload`
})

const uploadHeaders = computed(() => {
  return {
    Authorization: `Bearer ${userStore.token}`
  }
})

const uploadData = computed(() => {
  return {
    asset_id: assetId.value || 0,
    stage: uploadStage.value
  }
})

// ==================== 生命周期 ====================

onMounted(() => {
  if (isEdit.value) {
    loadAssetData()
    loadUploadedFiles()
  }
})

// ==================== 数据加载 ====================

const loadAssetData = async () => {
  loading.value = true
  try {
    const res = await getAssetDetail(assetId.value)
    Object.assign(formData, {
      asset_name: res.asset_name,
      category: res.category,
      data_classification: res.data_classification,
      sensitivity_level: res.sensitivity_level,
      description: res.description,
      data_source: res.data_source,
      data_volume: res.data_volume,
      data_format: res.data_format,
      update_frequency: res.update_frequency,
      asset_type: res.asset_type,
      estimated_value: res.estimated_value
    })
  } catch (error) {
    ElMessage.error('加载资产数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadUploadedFiles = async () => {
  try {
    const res = await getMaterialList(assetId.value)
    uploadedFiles.value = res
  } catch (error) {
    console.error('加载已上传文件失败', error)
  }
}

// ==================== 表单操作 ====================

const handleSaveDraft = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitLoading.value = true

    let savedAssetId = assetId.value

    if (isEdit.value) {
      await updateAsset(assetId.value, formData)
      ElMessage.success('保存成功')
    } else {
      const res = await createAsset(formData)
      savedAssetId = res.id
      ElMessage.success('创建成功')
    }

    // 上传文件
    await uploadFiles(savedAssetId)

    // 跳转到详情页
    router.push(`/assets/${savedAssetId}`)
  } catch (error: any) {
    if (error !== false) {
      ElMessage.error(error.message || '保存失败')
      console.error(error)
    }
  } finally {
    submitLoading.value = false
  }
}

const handleSaveAndSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    await ElMessageBox.confirm(
      '确定要保存并提交审批吗？',
      '提交确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    submitLoading.value = true

    let savedAssetId = assetId.value

    if (isEdit.value) {
      await updateAsset(assetId.value, formData)
    } else {
      const res = await createAsset(formData)
      savedAssetId = res.id
    }

    // 上传文件
    await uploadFiles(savedAssetId)

    // 提交审批
    await submitAsset(savedAssetId)

    ElMessage.success('保存并提交成功')
    router.push(`/assets/${savedAssetId}`)
  } catch (error: any) {
    if (error !== 'cancel' && error !== false) {
      ElMessage.error(error.message || '操作失败')
      console.error(error)
    }
  } finally {
    submitLoading.value = false
  }
}

const handleBack = () => {
  router.back()
}

// ==================== 文件上传 ====================

const beforeUpload = (file: File) => {
  const isLt50M = file.size / 1024 / 1024 < 50

  if (!isLt50M) {
    ElMessage.error('上传文件大小不能超过 50MB!')
    return false
  }

  return true
}

const uploadFiles = async (assetId: number) => {
  if (!uploadRef.value) return

  const files = uploadRef.value.uploadFiles
  if (files.length === 0) return

  try {
    for (const file of files) {
      if (file.raw && file.status !== 'success') {
        const formData = new FormData()
        formData.append('file', file.raw)
        formData.append('asset_id', String(assetId))
        formData.append('material_name', file.name)
        formData.append('material_type', file.raw.type || 'application/octet-stream')
        formData.append('stage', uploadStage.value)

        await uploadMaterial(formData)
      }
    }

    if (files.length > 0) {
      ElMessage.success(`成功上传 ${files.length} 个文件`)
      fileList.value = []
    }
  } catch (error) {
    ElMessage.error('文件上传失败')
    throw error
  }
}

const handleUploadSuccess = (response: any, file: any) => {
  ElMessage.success(`${file.name} 上传成功`)
}

const handleUploadError = (error: any, file: any) => {
  ElMessage.error(`${file.name} 上传失败`)
  console.error(error)
}

// ==================== 辅助函数 ====================

const getStageLabel = (stage: string) => {
  const map: Record<string, string> = {
    registration: '登记',
    inventory: '盘点',
    evaluation: '评估',
    cataloging: '入表'
  }
  return map[stage] || stage
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (dateStr: string) => {
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
</script>

<style scoped lang="scss">
.asset-form-container {
  padding: 20px;

  .el-page-header {
    margin-bottom: 20px;
  }

  .form-content {
    max-width: 800px;

    .el-divider {
      margin: 30px 0 20px;
    }

    .el-upload {
      width: 100%;
    }

    .el-icon--upload {
      font-size: 67px;
      color: #c0c4cc;
      margin: 40px 0 16px;
    }

    .el-upload__text {
      color: #606266;
      font-size: 14px;
      text-align: center;

      em {
        color: #409eff;
        font-style: normal;
      }
    }

    .el-upload__tip {
      color: #909399;
      font-size: 12px;
      margin-top: 7px;
    }
  }
}
</style>
