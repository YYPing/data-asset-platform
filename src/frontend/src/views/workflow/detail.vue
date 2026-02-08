<template>
  <div class="workflow-detail-page">
    <el-page-header @back="goBack" title="返回">
      <template #content>
        <span class="page-title">审批详情</span>
      </template>
    </el-page-header>

    <div class="content-wrapper">
      <!-- 资产基本信息 -->
      <el-card class="info-card" v-loading="loading">
        <template #header>
          <span class="card-title">资产基本信息</span>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="资产ID">
            {{ assetId }}
          </el-descriptions-item>
          <el-descriptions-item label="资产名称">
            {{ assetInfo.name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="资产类型">
            {{ assetInfo.type || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="当前环节">
            <el-tag :type="getNodeStatusType(workflowStatus?.current_node)">
              {{ getCurrentNodeName() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="审批进度" :span="2">
            <el-progress
              :percentage="workflowStatus?.progress_percent || 0"
              :color="progressColor"
            />
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 审批流程图 -->
      <el-card class="flow-card">
        <template #header>
          <span class="card-title">审批流程</span>
        </template>
        <el-steps
          :active="activeStep"
          :process-status="processStatus"
          align-center
        >
          <el-step
            v-for="(node, index) in workflowStatus?.nodes || []"
            :key="node.id"
            :title="node.name"
            :description="getNodeDescription(node)"
            :status="getStepStatus(node)"
            :icon="getStepIcon(node)"
          />
        </el-steps>
      </el-card>

      <!-- 审批历史时间线 -->
      <el-card class="history-card">
        <template #header>
          <span class="card-title">审批历史</span>
        </template>
        <el-timeline v-if="historyList.length > 0">
          <el-timeline-item
            v-for="(item, index) in historyList"
            :key="index"
            :timestamp="formatDateTime(item.operated_at)"
            placement="top"
            :type="getTimelineType(item.action)"
            :icon="getTimelineIcon(item.action)"
          >
            <el-card>
              <div class="history-item">
                <div class="history-header">
                  <span class="action-tag">
                    <el-tag :type="getActionTagType(item.action)" size="small">
                      {{ item.action }}
                    </el-tag>
                  </span>
                  <span class="node-name">{{ item.node_name }}</span>
                </div>
                <div class="operator">
                  操作人：{{ item.operator_name }}
                </div>
                <div class="comment" v-if="item.comment">
                  意见：{{ item.comment }}
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无审批历史" />
      </el-card>

      <!-- 操作区域 -->
      <el-card class="action-card" v-if="canOperate">
        <template #header>
          <span class="card-title">审批操作</span>
        </template>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
        >
          <el-form-item label="审批意见" prop="comment">
            <el-input
              v-model="form.comment"
              type="textarea"
              :rows="4"
              placeholder="请输入审批意见"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </el-form>

        <div class="action-buttons">
          <el-button
            type="success"
            size="large"
            :icon="Check"
            @click="handleAction('approve')"
            :loading="submitting"
          >
            通过
          </el-button>
          <el-button
            type="danger"
            size="large"
            :icon="Close"
            @click="handleAction('reject')"
            :loading="submitting"
          >
            驳回
          </el-button>
          <el-button
            type="warning"
            size="large"
            :icon="EditPen"
            @click="handleAction('correct')"
            :loading="submitting"
          >
            要求补正
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 驳回弹窗 -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="驳回审批"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="回退环节" required>
          <el-select
            v-model="rejectToNode"
            placeholder="请选择回退环节"
            style="width: 100%"
          >
            <el-option
              v-for="node in availableRejectNodes"
              :key="node.id"
              :label="node.name"
              :value="node.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmReject" :loading="submitting">
          确认驳回
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Check,
  Close,
  EditPen,
  CircleCheck,
  CircleClose,
  Clock,
  Warning
} from '@element-plus/icons-vue'
import {
  getWorkflowStatus,
  getWorkflowHistory,
  approveWorkflow,
  rejectWorkflow,
  type WorkflowStatus,
  type WorkflowHistory,
  type WorkflowNode
} from '@/api/workflow'
import { useUserStore } from '@/stores/user'
import { hasRole } from '@/utils/permission'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// ==================== 数据状态 ====================
const loading = ref(false)
const submitting = ref(false)
const assetId = ref(route.params.asset_id as string)
const workflowStatus = ref<WorkflowStatus | null>(null)
const historyList = ref<WorkflowHistory[]>([])
const rejectDialogVisible = ref(false)
const rejectToNode = ref('')

// 模拟资产信息（实际应从API获取）
const assetInfo = ref({
  name: '客户交易数据集',
  type: '数据库表'
})

// ==================== 表单 ====================
const formRef = ref<FormInstance>()
const form = ref({
  comment: ''
})

const rules: FormRules = {
  comment: [
    { required: true, message: '请输入审批意见', trigger: 'blur' },
    { min: 5, message: '审批意见至少5个字符', trigger: 'blur' }
  ]
}

// ==================== 计算属性 ====================

/**
 * 当前激活的步骤
 */
const activeStep = computed(() => {
  if (!workflowStatus.value) return 0
  const currentIndex = workflowStatus.value.nodes.findIndex(
    node => node.id === workflowStatus.value?.current_node
  )
  return currentIndex >= 0 ? currentIndex : 0
})

/**
 * 流程状态
 */
const processStatus = computed(() => {
  const currentNode = workflowStatus.value?.nodes.find(
    node => node.id === workflowStatus.value?.current_node
  )
  if (currentNode?.status === 'rejected') return 'error'
  if (currentNode?.status === 'approved') return 'success'
  return 'process'
})

/**
 * 进度条颜色
 */
const progressColor = computed(() => {
  const percent = workflowStatus.value?.progress_percent || 0
  if (percent === 100) return '#67c23a'
  if (percent >= 50) return '#409eff'
  return '#e6a23c'
})

/**
 * 是否可以操作
 */
const canOperate = computed(() => {
  if (!workflowStatus.value) return false
  const currentNode = workflowStatus.value.nodes.find(
    node => node.id === workflowStatus.value?.current_node
  )
  if (!currentNode) return false

  // 检查当前用户是否有权限操作
  return (
    currentNode.status === 'processing' &&
    hasRole(currentNode.assigned_to)
  )
})

/**
 * 可回退的节点
 */
const availableRejectNodes = computed(() => {
  if (!workflowStatus.value) return []
  return workflowStatus.value.nodes.filter(
    node => node.status === 'approved'
  )
})

// ==================== 生命周期 ====================
onMounted(() => {
  loadData()
})

// ==================== 方法 ====================

/**
 * 加载数据
 */
async function loadData() {
  loading.value = true
  try {
    await Promise.all([
      loadWorkflowStatus(),
      loadWorkflowHistory()
    ])
  } finally {
    loading.value = false
  }
}

/**
 * 加载工作流状态
 */
async function loadWorkflowStatus() {
  try {
    workflowStatus.value = await getWorkflowStatus(assetId.value)
  } catch (error) {
    ElMessage.error('加载工作流状态失败')
    console.error(error)
  }
}

/**
 * 加载审批历史
 */
async function loadWorkflowHistory() {
  try {
    historyList.value = await getWorkflowHistory(assetId.value)
  } catch (error) {
    ElMessage.error('加载审批历史失败')
    console.error(error)
  }
}

/**
 * 获取当前节点名称
 */
function getCurrentNodeName(): string {
  if (!workflowStatus.value) return '-'
  const currentNode = workflowStatus.value.nodes.find(
    node => node.id === workflowStatus.value?.current_node
  )
  return currentNode?.name || '-'
}

/**
 * 获取节点状态类型
 */
function getNodeStatusType(nodeId?: string): string {
  if (!nodeId || !workflowStatus.value) return 'info'
  const node = workflowStatus.value.nodes.find(n => n.id === nodeId)
  if (!node) return 'info'

  const statusMap: Record<string, string> = {
    pending: 'info',
    processing: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return statusMap[node.status] || 'info'
}

/**
 * 获取节点描述
 */
function getNodeDescription(node: WorkflowNode): string {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    approved: '已通过',
    rejected: '已驳回'
  }
  return statusMap[node.status] || ''
}

/**
 * 获取步骤状态
 */
function getStepStatus(node: WorkflowNode): string {
  const statusMap: Record<string, string> = {
    pending: 'wait',
    processing: 'process',
    approved: 'success',
    rejected: 'error'
  }
  return statusMap[node.status] || 'wait'
}

/**
 * 获取步骤图标
 */
function getStepIcon(node: WorkflowNode) {
  const iconMap: Record<string, any> = {
    pending: Clock,
    processing: Warning,
    approved: CircleCheck,
    rejected: CircleClose
  }
  return iconMap[node.status]
}

/**
 * 获取时间线类型
 */
function getTimelineType(action: string): string {
  if (action.includes('通过') || action.includes('批准')) return 'success'
  if (action.includes('驳回') || action.includes('拒绝')) return 'danger'
  if (action.includes('补正')) return 'warning'
  return 'primary'
}

/**
 * 获取时间线图标
 */
function getTimelineIcon(action: string) {
  if (action.includes('通过') || action.includes('批准')) return CircleCheck
  if (action.includes('驳回') || action.includes('拒绝')) return CircleClose
  if (action.includes('补正')) return EditPen
  return Clock
}

/**
 * 获取操作标签类型
 */
function getActionTagType(action: string): string {
  if (action.includes('通过') || action.includes('批准')) return 'success'
  if (action.includes('驳回') || action.includes('拒绝')) return 'danger'
  if (action.includes('补正')) return 'warning'
  return 'info'
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
    minute: '2-digit',
    second: '2-digit'
  })
}

/**
 * 处理操作
 */
async function handleAction(action: 'approve' | 'reject' | 'correct') {
  if (!formRef.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  if (action === 'reject') {
    // 驳回需要选择回退环节
    rejectDialogVisible.value = true
    return
  }

  // 通过或补正
  const actionText = action === 'approve' ? '通过' : '要求补正'
  try {
    await ElMessageBox.confirm(
      `确认${actionText}该审批吗？`,
      '确认操作',
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
    const currentNode = workflowStatus.value?.nodes.find(
      node => node.id === workflowStatus.value?.current_node
    )
    if (!currentNode) throw new Error('未找到当前节点')

    await approveWorkflow(currentNode.id, form.value.comment)
    ElMessage.success(`${actionText}成功`)
    
    // 刷新数据
    form.value.comment = ''
    await loadData()
  } catch (error) {
    ElMessage.error(`${actionText}失败`)
    console.error(error)
  } finally {
    submitting.value = false
  }
}

/**
 * 确认驳回
 */
async function confirmReject() {
  if (!rejectToNode.value) {
    ElMessage.warning('请选择回退环节')
    return
  }

  submitting.value = true
  try {
    const currentNode = workflowStatus.value?.nodes.find(
      node => node.id === workflowStatus.value?.current_node
    )
    if (!currentNode) throw new Error('未找到当前节点')

    await rejectWorkflow(
      currentNode.id,
      form.value.comment,
      rejectToNode.value
    )
    ElMessage.success('驳回成功')
    
    rejectDialogVisible.value = false
    form.value.comment = ''
    rejectToNode.value = ''
    
    // 刷新数据
    await loadData()
  } catch (error) {
    ElMessage.error('驳回失败')
    console.error(error)
  } finally {
    submitting.value = false
  }
}

/**
 * 返回
 */
function goBack() {
  router.back()
}
</script>

<style scoped lang="scss">
.workflow-detail-page {
  padding: 20px;

  .page-title {
    font-size: 20px;
    font-weight: 600;
  }

  .content-wrapper {
    margin-top: 20px;
    display: flex;
    flex-direction: column;
    gap: 20px;

    .card-title {
      font-size: 16px;
      font-weight: 600;
    }

    .info-card {
      :deep(.el-descriptions__label) {
        width: 120px;
      }
    }

    .flow-card {
      :deep(.el-steps) {
        padding: 20px 0;
      }
    }

    .history-card {
      .history-item {
        .history-header {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 8px;

          .node-name {
            font-weight: 600;
            font-size: 15px;
          }
        }

        .operator {
          color: #606266;
          font-size: 14px;
          margin-bottom: 5px;
        }

        .comment {
          color: #909399;
          font-size: 14px;
          line-height: 1.6;
          padding: 8px;
          background-color: #f5f7fa;
          border-radius: 4px;
          margin-top: 8px;
        }
      }
    }

    .action-card {
      .action-buttons {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 20px;
      }
    }
  }
}
</style>
