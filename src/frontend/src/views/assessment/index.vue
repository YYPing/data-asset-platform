<template>
  <div class="assessment-page">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <!-- 待评估列表 -->
      <el-tab-pane label="待评估" name="pending">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="title">待评估列表</span>
              <el-button type="primary" :icon="Refresh" @click="loadPendingList" :loading="loading">
                刷新
              </el-button>
            </div>
          </template>

          <el-table
            v-loading="loading"
            :data="pendingList"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="asset_name" label="资产名称" min-width="200" />
            <el-table-column prop="assessment_type" label="评估类型" width="120">
              <template #default="{ row }">
                <el-tag :type="row.assessment_type === 'compliance' ? 'warning' : 'success'">
                  {{ getAssessmentTypeName(row.assessment_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag type="info">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="openAssessmentDialog(row)">
                  开始评估
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!loading && pendingList.length === 0" description="暂无待评估项" />
        </el-card>
      </el-tab-pane>

      <!-- 已完成列表 -->
      <el-tab-pane label="已完成" name="completed">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="title">已完成评估</span>
              <el-button type="primary" :icon="Refresh" @click="loadCompletedList" :loading="loading">
                刷新
              </el-button>
            </div>
          </template>

          <el-table
            v-loading="loading"
            :data="completedList"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="asset_id" label="资产ID" width="180" />
            <el-table-column prop="assessment_type" label="评估类型" width="120">
              <template #default="{ row }">
                <el-tag :type="row.assessment_type === 'compliance' ? 'warning' : 'success'">
                  {{ getAssessmentTypeName(row.assessment_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="评分" width="100" />
            <el-table-column prop="risk_level" label="风险等级" width="100">
              <template #default="{ row }">
                <el-tag
                  v-if="row.risk_level"
                  :type="getRiskLevelType(row.risk_level)"
                >
                  {{ getRiskLevelName(row.risk_level) }}
                </el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="method" label="评估方法" width="120">
              <template #default="{ row }">
                {{ row.method || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="result_summary" label="评估意见" min-width="200" show-overflow-tooltip />
            <el-table-column prop="created_at" label="评估时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="info" size="small" @click="viewDetail(row)">
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!loading && completedList.length === 0" description="暂无已完成评估" />
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 评估表单弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="`${getAssessmentTypeName(currentAssessment?.assessment_type)} - ${currentAssessment?.asset_name}`"
      width="600px"
      @close="resetForm"
    >
      <!-- 合规评估表单 -->
      <el-form
        v-if="currentAssessment?.assessment_type === 'compliance'"
        ref="complianceFormRef"
        :model="complianceForm"
        :rules="complianceRules"
        label-width="100px"
      >
        <el-form-item label="评分" prop="score">
          <el-slider
            v-model="complianceForm.score"
            :min="0"
            :max="100"
            :step="1"
            show-input
            :marks="{ 0: '0', 50: '50', 100: '100' }"
          />
        </el-form-item>

        <el-form-item label="风险等级" prop="risk_level">
          <el-radio-group v-model="complianceForm.risk_level">
            <el-radio value="low">
              <el-tag type="success">低风险</el-tag>
            </el-radio>
            <el-radio value="medium">
              <el-tag type="warning">中风险</el-tag>
            </el-radio>
            <el-radio value="high">
              <el-tag type="danger">高风险</el-tag>
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="评估意见" prop="result_summary">
          <el-input
            v-model="complianceForm.result_summary"
            type="textarea"
            :rows="6"
            placeholder="请输入合规评估意见，包括合规性分析、风险点、改进建议等"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <!-- 价值评估表单 -->
      <el-form
        v-if="currentAssessment?.assessment_type === 'valuation'"
        ref="valuationFormRef"
        :model="valuationForm"
        :rules="valuationRules"
        label-width="100px"
      >
        <el-form-item label="评估方法" prop="method">
          <el-select
            v-model="valuationForm.method"
            placeholder="请选择评估方法"
            style="width: 100%"
          >
            <el-option label="成本法" value="cost" />
            <el-option label="市场法" value="market" />
            <el-option label="收益法" value="income" />
            <el-option label="综合法" value="comprehensive" />
          </el-select>
        </el-form-item>

        <el-form-item label="评估值" prop="score">
          <el-input-number
            v-model="valuationForm.score"
            :min="0"
            :max="999999999"
            :precision="2"
            :step="1000"
            controls-position="right"
            style="width: 100%"
          />
          <span style="margin-left: 10px; color: #909399;">元</span>
        </el-form-item>

        <el-form-item label="评估意见" prop="result_summary">
          <el-input
            v-model="valuationForm.result_summary"
            type="textarea"
            :rows="6"
            placeholder="请输入价值评估意见，包括评估依据、计算过程、价值分析等"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAssessment" :loading="submitting">
          提交评估
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情查看弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="评估详情"
      width="700px"
    >
      <el-descriptions :column="1" border v-if="currentDetail">
        <el-descriptions-item label="资产ID">
          {{ currentDetail.asset_id }}
        </el-descriptions-item>
        <el-descriptions-item label="评估类型">
          <el-tag :type="currentDetail.assessment_type === 'compliance' ? 'warning' : 'success'">
            {{ getAssessmentTypeName(currentDetail.assessment_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="评分">
          {{ currentDetail.score }}
        </el-descriptions-item>
        <el-descriptions-item label="风险等级" v-if="currentDetail.risk_level">
          <el-tag :type="getRiskLevelType(currentDetail.risk_level)">
            {{ getRiskLevelName(currentDetail.risk_level) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="评估方法" v-if="currentDetail.method">
          {{ getMethodName(currentDetail.method) }}
        </el-descriptions-item>
        <el-descriptions-item label="评估意见">
          <div style="white-space: pre-wrap; line-height: 1.6;">
            {{ currentDetail.result_summary }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="评估时间">
          {{ formatDateTime(currentDetail.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatDateTime(currentDetail.updated_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import {
  getPendingAssessments,
  getAssessmentRecords,
  submitComplianceAssessment,
  submitValuationAssessment,
  completeAssessment,
  type PendingAssessment,
  type AssessmentRecord,
  type ComplianceAssessmentData,
  type ValuationAssessmentData
} from '@/api/workflow'
import { hasRole } from '@/utils/permission'

// ==================== 数据状态 ====================
const loading = ref(false)
const submitting = ref(false)
const activeTab = ref('pending')
const pendingList = ref<PendingAssessment[]>([])
const completedList = ref<AssessmentRecord[]>([])
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const currentAssessment = ref<PendingAssessment | null>(null)
const currentDetail = ref<AssessmentRecord | null>(null)

// ==================== 表单 ====================
const complianceFormRef = ref<FormInstance>()
const valuationFormRef = ref<FormInstance>()

const complianceForm = reactive<ComplianceAssessmentData>({
  score: 80,
  risk_level: 'low',
  result_summary: ''
})

const valuationForm = reactive<ValuationAssessmentData>({
  method: '',
  score: 0,
  result_summary: ''
})

const complianceRules: FormRules = {
  score: [
    { required: true, message: '请设置评分', trigger: 'change' }
  ],
  risk_level: [
    { required: true, message: '请选择风险等级', trigger: 'change' }
  ],
  result_summary: [
    { required: true, message: '请输入评估意见', trigger: 'blur' },
    { min: 20, message: '评估意见至少20个字符', trigger: 'blur' }
  ]
}

const valuationRules: FormRules = {
  method: [
    { required: true, message: '请选择评估方法', trigger: 'change' }
  ],
  score: [
    { required: true, message: '请输入评估值', trigger: 'blur' },
    { type: 'number', min: 0, message: '评估值不能为负数', trigger: 'blur' }
  ],
  result_summary: [
    { required: true, message: '请输入评估意见', trigger: 'blur' },
    { min: 20, message: '评估意见至少20个字符', trigger: 'blur' }
  ]
}

// ==================== 生命周期 ====================
onMounted(() => {
  loadPendingList()
})

// ==================== 方法 ====================

/**
 * 标签页切换
 */
function handleTabChange(tabName: string) {
  if (tabName === 'pending') {
    loadPendingList()
  } else if (tabName === 'completed') {
    loadCompletedList()
  }
}

/**
 * 加载待评估列表
 */
async function loadPendingList() {
  loading.value = true
  try {
    pendingList.value = await getPendingAssessments()
  } catch (error) {
    ElMessage.error('加载待评估列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

/**
 * 加载已完成列表
 */
async function loadCompletedList() {
  loading.value = true
  try {
    // 这里简化处理，实际应该有专门的已完成列表接口
    // 暂时使用空数组，实际项目中需要调用相应API
    completedList.value = []
    ElMessage.info('已完成列表功能待实现')
  } catch (error) {
    ElMessage.error('加载已完成列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

/**
 * 打开评估弹窗
 */
function openAssessmentDialog(assessment: PendingAssessment) {
  currentAssessment.value = assessment
  dialogVisible.value = true
}

/**
 * 提交评估
 */
async function submitAssessment() {
  if (!currentAssessment.value) return

  const isCompliance = currentAssessment.value.assessment_type === 'compliance'
  const formRef = isCompliance ? complianceFormRef.value : valuationFormRef.value

  if (!formRef) return

  await formRef.validate(async (valid) => {
    if (!valid) return

    // 二次确认
    try {
      await ElMessageBox.confirm(
        '确认提交该评估吗？提交后将无法修改。',
        '确认提交',
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      return
    }

    submitting.value = true
    try {
      if (isCompliance) {
        await submitComplianceAssessment(
          currentAssessment.value!.asset_id,
          complianceForm
        )
      } else {
        await submitValuationAssessment(
          currentAssessment.value!.asset_id,
          valuationForm
        )
      }

      // 标记为完成
      await completeAssessment(currentAssessment.value!.id)

      ElMessage.success('评估提交成功')
      dialogVisible.value = false
      loadPendingList() // 刷新列表
    } catch (error) {
      ElMessage.error('评估提交失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

/**
 * 重置表单
 */
function resetForm() {
  complianceFormRef.value?.resetFields()
  valuationFormRef.value?.resetFields()
  
  complianceForm.score = 80
  complianceForm.risk_level = 'low'
  complianceForm.result_summary = ''
  
  valuationForm.method = ''
  valuationForm.score = 0
  valuationForm.result_summary = ''
  
  currentAssessment.value = null
}

/**
 * 查看详情
 */
function viewDetail(record: AssessmentRecord) {
  currentDetail.value = record
  detailDialogVisible.value = true
}

/**
 * 获取评估类型名称
 */
function getAssessmentTypeName(type?: string): string {
  const typeMap: Record<string, string> = {
    compliance: '合规评估',
    valuation: '价值评估'
  }
  return typeMap[type || ''] || '-'
}

/**
 * 获取风险等级名称
 */
function getRiskLevelName(level: string): string {
  const levelMap: Record<string, string> = {
    low: '低风险',
    medium: '中风险',
    high: '高风险'
  }
  return levelMap[level] || '-'
}

/**
 * 获取风险等级类型
 */
function getRiskLevelType(level: string): string {
  const typeMap: Record<string, string> = {
    low: 'success',
    medium: 'warning',
    high: 'danger'
  }
  return typeMap[level] || 'info'
}

/**
 * 获取评估方法名称
 */
function getMethodName(method: string): string {
  const methodMap: Record<string, string> = {
    cost: '成本法',
    market: '市场法',
    income: '收益法',
    comprehensive: '综合法'
  }
  return methodMap[method] || method
}

/**
 * 格式化日期时间
 */
function formatDateTime(dateStr: string): string {
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
.assessment-page {
  padding: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-size: 18px;
      font-weight: 600;
    }
  }

  :deep(.el-tabs__content) {
    padding-top: 20px;
  }

  :deep(.el-slider__marks-text) {
    font-size: 12px;
  }

  :deep(.el-radio) {
    margin-right: 20px;
    
    .el-tag {
      margin-left: 5px;
    }
  }
}
</style>
