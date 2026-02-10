<template>
  <div class="operation-log-container">
    <div class="log-filters">
      <el-form :model="filters" inline>
        <el-form-item label="操作类型">
          <el-select
            v-model="filters.operation_type"
            placeholder="全部"
            clearable
            style="width: 150px"
            @change="handleFilter"
          >
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="提交" value="submit" />
            <el-option label="审批" value="approve" />
            <el-option label="拒绝" value="reject" />
            <el-option label="归档" value="archive" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作人">
          <el-input
            v-model="filters.operator"
            placeholder="请输入操作人"
            clearable
            style="width: 200px"
            @change="handleFilter"
          />
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 300px"
            @change="handleFilter"
          />
        </el-form-item>
      </el-form>
    </div>

    <el-timeline v-loading="loading" class="log-timeline">
      <el-timeline-item
        v-for="log in logs"
        :key="log.id"
        :timestamp="formatDateTime(log.created_at)"
        placement="top"
        :type="getLogType(log.operation_type)"
        :icon="getLogIcon(log.operation_type)"
      >
        <el-card shadow="hover">
          <div class="log-content">
            <div class="log-header">
              <el-tag :type="getOperationTagType(log.operation_type)" size="small">
                {{ getOperationLabel(log.operation_type) }}
              </el-tag>
              <span class="log-operator">
                <el-icon><User /></el-icon>
                {{ log.operator_name || log.operator }}
              </span>
            </div>

            <div class="log-body">
              <div class="log-operation">
                <el-text>{{ log.operation }}</el-text>
              </div>
              <div v-if="log.details" class="log-details">
                <el-text type="info" size="small">{{ log.details }}</el-text>
              </div>
            </div>

            <div v-if="showTechnicalInfo && (log.ip_address || log.user_agent)" class="log-footer">
              <el-divider />
              <div class="log-technical">
                <el-text type="info" size="small">
                  <span v-if="log.ip_address">IP: {{ log.ip_address }}</span>
                  <span v-if="log.user_agent" class="user-agent">
                    {{ formatUserAgent(log.user_agent) }}
                  </span>
                </el-text>
              </div>
            </div>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>

    <el-empty v-if="!loading && logs.length === 0" description="暂无操作日志" />

    <div v-if="logs.length > 0" class="log-pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  User,
  CirclePlus,
  Edit,
  Delete,
  Upload,
  CircleCheck,
  CircleClose,
  FolderOpened
} from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/asset-helper'
import type { AssetOperationLog } from '@/types/asset'

interface Props {
  assetId: number
  showTechnicalInfo?: boolean
  pageSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  showTechnicalInfo: false,
  pageSize: 20
})

// ==================== 状态管理 ====================

const loading = ref(false)
const logs = ref<AssetOperationLog[]>([])

const filters = reactive({
  operation_type: '',
  operator: '',
  dateRange: null as [Date, Date] | null
})

const pagination = reactive({
  page: 1,
  page_size: props.pageSize,
  total: 0
})

// ==================== 生命周期 ====================

onMounted(() => {
  loadLogs()
})

// ==================== 数据加载 ====================

const loadLogs = async () => {
  loading.value = true
  try {
    // TODO: 调用实际的API
    // const params = {
    //   asset_id: props.assetId,
    //   page: pagination.page,
    //   page_size: pagination.page_size,
    //   operation_type: filters.operation_type || undefined,
    //   operator: filters.operator || undefined,
    //   start_date: filters.dateRange?.[0]?.toISOString(),
    //   end_date: filters.dateRange?.[1]?.toISOString()
    // }
    // const res = await getAssetOperationLogs(params)
    // logs.value = res.data.items
    // pagination.total = res.data.total

    // 模拟数据
    logs.value = [
      {
        id: 1,
        asset_id: props.assetId,
        operation: '提交资产审批',
        operation_type: 'submit',
        operator: 'user001',
        operator_name: '张三',
        details: '资产已提交至中心审核员进行审批',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        created_at: '2024-02-10 14:30:00'
      },
      {
        id: 2,
        asset_id: props.assetId,
        operation: '更新资产信息',
        operation_type: 'update',
        operator: 'user001',
        operator_name: '张三',
        details: '更新了资产估值和数据量字段',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        created_at: '2024-02-10 10:15:00'
      },
      {
        id: 3,
        asset_id: props.assetId,
        operation: '创建资产',
        operation_type: 'create',
        operator: 'user001',
        operator_name: '张三',
        details: '创建了新的数据资产',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        created_at: '2024-02-09 09:00:00'
      }
    ]
    pagination.total = logs.value.length
  } catch (error) {
    console.error('Failed to load operation logs:', error)
    ElMessage.error('加载操作日志失败')
  } finally {
    loading.value = false
  }
}

// ==================== 筛选和分页 ====================

const handleFilter = () => {
  pagination.page = 1
  loadLogs()
}

const handleSizeChange = () => {
  pagination.page = 1
  loadLogs()
}

const handleCurrentChange = () => {
  loadLogs()
}

// ==================== 辅助函数 ====================

const getOperationLabel = (type: string): string => {
  const map: Record<string, string> = {
    create: '创建',
    update: '更新',
    delete: '删除',
    submit: '提交',
    approve: '审批',
    reject: '拒绝',
    archive: '归档'
  }
  return map[type] || type
}

const getOperationTagType = (type: string): 'success' | 'warning' | 'danger' | 'info' | '' => {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info' | ''> = {
    create: 'success',
    update: 'info',
    delete: 'danger',
    submit: 'warning',
    approve: 'success',
    reject: 'danger',
    archive: 'info'
  }
  return map[type] || ''
}

const getLogType = (type: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' => {
  const map: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
    create: 'success',
    update: 'primary',
    delete: 'danger',
    submit: 'warning',
    approve: 'success',
    reject: 'danger',
    archive: 'info'
  }
  return map[type] || 'info'
}

const getLogIcon = (type: string): any => {
  const map: Record<string, any> = {
    create: CirclePlus,
    update: Edit,
    delete: Delete,
    submit: Upload,
    approve: CircleCheck,
    reject: CircleClose,
    archive: FolderOpened
  }
  return map[type] || Edit
}

const formatUserAgent = (ua: string): string => {
  // 简化 User-Agent 显示
  if (ua.includes('Chrome')) return 'Chrome'
  if (ua.includes('Firefox')) return 'Firefox'
  if (ua.includes('Safari')) return 'Safari'
  if (ua.includes('Edge')) return 'Edge'
  return 'Unknown'
}
</script>

<style scoped lang="scss">
.operation-log-container {
  padding: 20px;

  .log-filters {
    margin-bottom: 20px;
    padding: 16px;
    background-color: var(--el-fill-color-light);
    border-radius: 4px;
  }

  .log-timeline {
    margin-top: 20px;

    .log-content {
      .log-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;

        .log-operator {
          display: flex;
          align-items: center;
          gap: 4px;
          color: var(--el-text-color-secondary);
          font-size: 14px;
        }
      }

      .log-body {
        .log-operation {
          margin-bottom: 8px;
          font-size: 15px;
          font-weight: 500;
        }

        .log-details {
          color: var(--el-text-color-secondary);
          font-size: 13px;
        }
      }

      .log-footer {
        margin-top: 12px;

        .log-technical {
          display: flex;
          gap: 16px;
          font-size: 12px;

          .user-agent {
            margin-left: 16px;
          }
        }
      }
    }
  }

  .log-pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
