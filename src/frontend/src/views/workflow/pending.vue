<template>
  <div class="pending-workflow-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">我的待审批</span>
          <el-button type="primary" :icon="Refresh" @click="loadData" :loading="loading">
            刷新
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="asset_name" label="资产名称" min-width="200" />
        <el-table-column prop="node_name" label="审批环节" min-width="150" />
        <el-table-column prop="role" label="角色要求" min-width="120" />
        <el-table-column prop="started_at" label="发起时间" min-width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.started_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="deadline" label="截止时间" min-width="180">
          <template #default="{ row }">
            <span :class="{ 'urgent-deadline': isUrgent(row.deadline) }">
              {{ formatDateTime(row.deadline) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="紧急程度" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="isUrgent(row.deadline)" type="danger" effect="dark">
              紧急
            </el-tag>
            <el-tag v-else type="success" effect="plain">
              正常
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleApprove(row)">
              审批
            </el-button>
            <el-button type="info" size="small" @click="viewDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 审批弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="`审批 - ${currentItem?.asset_name}`"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="审批环节">
          <el-input v-model="currentItem!.node_name" disabled />
        </el-form-item>

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

        <el-form-item label="审批结果" prop="action">
          <el-radio-group v-model="form.action">
            <el-radio value="approve">通过</el-radio>
            <el-radio value="reject">驳回</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item
          v-if="form.action === 'reject'"
          label="回退环节"
          prop="rejectToNode"
        >
          <el-select
            v-model="form.rejectToNode"
            placeholder="请选择回退环节"
            style="width: 100%"
          >
            <el-option
              v-for="node in availableNodes"
              :key="node.id"
              :label="node.name"
              :value="node.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitApproval" :loading="submitting">
          提交
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import {
  getPendingWorkflows,
  approveWorkflow,
  rejectWorkflow,
  getWorkflowStatus,
  type PendingWorkflowItem,
  type WorkflowNode
} from '@/api/workflow'

const router = useRouter()

// ==================== 数据状态 ====================
const loading = ref(false)
const submitting = ref(false)
const tableData = ref<PendingWorkflowItem[]>([])
const dialogVisible = ref(false)
const currentItem = ref<PendingWorkflowItem | null>(null)
const availableNodes = ref<WorkflowNode[]>([])

// ==================== 表单 ====================
const formRef = ref<FormInstance>()
const form = reactive({
  comment: '',
  action: 'approve' as 'approve' | 'reject',
  rejectToNode: ''
})

const rules: FormRules = {
  comment: [
    { required: true, message: '请输入审批意见', trigger: 'blur' },
    { min: 5, message: '审批意见至少5个字符', trigger: 'blur' }
  ],
  action: [
    { required: true, message: '请选择审批结果', trigger: 'change' }
  ],
  rejectToNode: [
    { required: true, message: '请选择回退环节', trigger: 'change' }
  ]
}

// ==================== 生命周期 ====================
onMounted(() => {
  loadData()
})

// ==================== 方法 ====================

/**
 * 加载待办列表
 */
async function loadData() {
  loading.value = true
  try {
    const res = await getPendingWorkflows()
    tableData.value = res.items || []
  } catch (error) {
    ElMessage.error('加载待办列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

/**
 * 判断是否紧急（距离截止时间小于24小时）
 */
function isUrgent(deadline: string): boolean {
  const deadlineTime = new Date(deadline).getTime()
  const now = Date.now()
  const hoursLeft = (deadlineTime - now) / (1000 * 60 * 60)
  return hoursLeft < 24 && hoursLeft > 0
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

/**
 * 打开审批弹窗
 */
async function handleApprove(row: PendingWorkflowItem) {
  currentItem.value = row
  dialogVisible.value = true

  // 加载工作流状态，获取可回退的节点
  try {
    const status = await getWorkflowStatus(row.asset_id)
    // 过滤出已完成的节点作为可回退选项
    availableNodes.value = status.nodes.filter(
      node => node.status === 'approved' && node.id !== row.node_id
    )
  } catch (error) {
    console.error('加载工作流状态失败', error)
  }
}

/**
 * 提交审批
 */
async function submitApproval() {
  if (!formRef.value || !currentItem.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    // 二次确认
    const action = form.action === 'approve' ? '通过' : '驳回'
    try {
      await ElMessageBox.confirm(
        `确认${action}该审批吗？`,
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
      if (form.action === 'approve') {
        await approveWorkflow(currentItem.value!.node_id, form.comment)
        ElMessage.success('审批通过成功')
      } else {
        await rejectWorkflow(
          currentItem.value!.node_id,
          form.comment,
          form.rejectToNode
        )
        ElMessage.success('审批驳回成功')
      }

      dialogVisible.value = false
      loadData() // 刷新列表
    } catch (error) {
      ElMessage.error('审批操作失败')
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
  formRef.value?.resetFields()
  form.comment = ''
  form.action = 'approve'
  form.rejectToNode = ''
  currentItem.value = null
}

/**
 * 查看详情
 */
function viewDetail(row: PendingWorkflowItem) {
  router.push(`/workflow/detail/${row.asset_id}`)
}
</script>

<style scoped lang="scss">
.pending-workflow-page {
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

  .urgent-deadline {
    color: #f56c6c;
    font-weight: 600;
  }
}
</style>
