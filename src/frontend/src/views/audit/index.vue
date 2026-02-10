<template>
  <div class="audit-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">今日操作数</div>
            <div class="stat-value">{{ todayCount }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">本周操作数</div>
            <div class="stat-value">{{ weekCount }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">操作类型分布</div>
            <div class="stat-tags">
              <el-tag
                v-for="item in actionStats"
                :key="item.action"
                style="margin-right: 10px"
              >
                {{ getActionLabel(item.action) }}: {{ item.count }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <!-- 筛选栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-select
            v-model="filterAction"
            placeholder="操作类型"
            clearable
            style="width: 150px"
            @change="handleSearch"
          >
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="查看" value="view" />
            <el-option label="导出" value="export" />
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
          </el-select>

          <el-select
            v-model="filterResourceType"
            placeholder="资源类型"
            clearable
            style="width: 150px; margin-left: 10px"
            @change="handleSearch"
          >
            <el-option label="数据资产" value="data_asset" />
            <el-option label="用户" value="user" />
            <el-option label="组织" value="organization" />
            <el-option label="权限" value="permission" />
            <el-option label="系统配置" value="system_config" />
          </el-select>

          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 300px; margin-left: 10px"
            @change="handleSearch"
          />
        </div>

        <el-button type="success" @click="handleExport" :loading="exporting">
          <el-icon><Download /></el-icon>
          导出CSV
        </el-button>
      </div>

      <!-- 日志列表 -->
      <el-table
        v-loading="loading"
        :data="logList"
        stripe
        style="margin-top: 20px"
      >
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column label="操作类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getActionTagType(row.action)">
              {{ getActionLabel(row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="资源类型" width="150">
          <template #default="{ row }">
            <el-tag type="info">
              {{ getResourceTypeLabel(row.resource_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource_id" label="资源ID" width="100" />
        <el-table-column prop="details" label="详情" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP地址" width="140" />
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @current-change="fetchLogs"
        @size-change="fetchLogs"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { auditApi, type AuditLog } from '@/api/system'

// 数据状态
const loading = ref(false)
const exporting = ref(false)
const logList = ref<AuditLog[]>([])
const filterAction = ref('')
const filterResourceType = ref('')
const dateRange = ref<[Date, Date] | null>(null)

// 统计数据
const stats = ref({
  by_action: [] as Array<{ action: string; count: number }>,
  by_day: [] as Array<{ date: string; count: number }>
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 计算今日操作数
const todayCount = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  const todayData = stats.value.by_day.find(item => item.date === today)
  return todayData?.count || 0
})

// 计算本周操作数
const weekCount = computed(() => {
  const now = new Date()
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
  return stats.value.by_day
    .filter(item => new Date(item.date) >= weekAgo)
    .reduce((sum, item) => sum + item.count, 0)
})

// 操作类型统计（取前5个）
const actionStats = computed(() => {
  return stats.value.by_action.slice(0, 5)
})

// 获取审计日志列表
const fetchLogs = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize,
      action: filterAction.value || undefined,
      resource_type: filterResourceType.value || undefined
    }

    if (dateRange.value) {
      params.date_from = dateRange.value[0].toISOString().split('T')[0]
      params.date_to = dateRange.value[1].toISOString().split('T')[0]
    }

    const data = await auditApi.getLogs(params)
    logList.value = data.items
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('获取审计日志失败')
  } finally {
    loading.value = false
  }
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const data = await auditApi.getStats()
    stats.value = data
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchLogs()
}

// 导出日志
const handleExport = async () => {
  exporting.value = true
  try {
    const params: any = {}
    if (dateRange.value) {
      params.date_from = dateRange.value[0].toISOString().split('T')[0]
      params.date_to = dateRange.value[1].toISOString().split('T')[0]
    }

    const data = await auditApi.exportLogs(params)

    // 创建下载链接
    const blob = new Blob([data], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `audit_logs_${new Date().getTime()}.csv`
    link.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
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

// 操作类型标签类型
const getActionTagType = (action: string) => {
  const typeMap: Record<string, any> = {
    create: 'success',
    update: 'warning',
    delete: 'danger',
    view: 'info',
    export: 'primary',
    login: '',
    logout: 'info'
  }
  return typeMap[action] || ''
}

// 操作类型标签文本
const getActionLabel = (action: string) => {
  const labelMap: Record<string, string> = {
    create: '创建',
    update: '更新',
    delete: '删除',
    view: '查看',
    export: '导出',
    login: '登录',
    logout: '登出'
  }
  return labelMap[action] || action
}

// 资源类型标签文本
const getResourceTypeLabel = (resourceType: string) => {
  const labelMap: Record<string, string> = {
    data_asset: '数据资产',
    user: '用户',
    organization: '组织',
    permission: '权限',
    system_config: '系统配置'
  }
  return labelMap[resourceType] || resourceType
}

onMounted(() => {
  fetchLogs()
  fetchStats()
})
</script>

<style scoped lang="scss">
.audit-container {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;

  &-left {
    display: flex;
    align-items: center;
  }
}

.stat-card {
  .stat-label {
    font-size: 14px;
    color: #909399;
    margin-bottom: 10px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: bold;
    color: #303133;
  }

  .stat-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>
