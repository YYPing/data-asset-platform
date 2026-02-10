<template>
  <div class="notifications-container">
    <el-card>
      <!-- 顶部操作栏 -->
      <div class="toolbar">
        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
          <el-tab-pane label="全部通知" name="all">
            <template #label>
              全部通知
              <el-badge :value="pagination.total" :max="99" style="margin-left: 10px" />
            </template>
          </el-tab-pane>
          <el-tab-pane label="未读" name="unread">
            <template #label>
              未读
              <el-badge :value="unreadCount" :max="99" type="danger" style="margin-left: 10px" />
            </template>
          </el-tab-pane>
        </el-tabs>

        <el-button
          type="primary"
          :disabled="unreadCount === 0"
          @click="handleMarkAllRead"
        >
          <el-icon><Check /></el-icon>
          全部标记已读
        </el-button>
      </div>

      <!-- 通知列表 -->
      <el-table
        v-loading="loading"
        :data="notificationList"
        stripe
        style="margin-top: 20px"
        @row-click="handleRowClick"
        :row-class-name="getRowClassName"
      >
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-icon v-if="!row.is_read" color="#409eff" :size="20">
              <CircleCheck />
            </el-icon>
            <el-icon v-else color="#c0c4cc" :size="20">
              <CircleCheck />
            </el-icon>
          </template>
        </el-table-column>

        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="title" label="标题" width="250" show-overflow-tooltip />

        <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />

        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_read"
              link
              type="primary"
              size="small"
              @click.stop="handleMarkRead(row)"
            >
              标记已读
            </el-button>
            <el-button
              v-if="row.related_url"
              link
              type="success"
              size="small"
              @click.stop="handleGoToRelated(row)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @current-change="fetchNotifications"
        @size-change="fetchNotifications"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, CircleCheck } from '@element-plus/icons-vue'
import { notificationApi, type Notification } from '@/api/system'

const router = useRouter()

// 数据状态
const loading = ref(false)
const notificationList = ref<Notification[]>([])
const activeTab = ref('all')
const unreadCount = ref(0)

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 获取通知列表
const fetchNotifications = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    if (activeTab.value === 'unread') {
      params.is_read = false
    }

    const data = await notificationApi.getNotifications(params)
    notificationList.value = data.items
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('获取通知列表失败')
  } finally {
    loading.value = false
  }
}

// 获取未读数量
const fetchUnreadCount = async () => {
  try {
    const data = await notificationApi.getUnreadCount()
    unreadCount.value = data.count
  } catch (error) {
    console.error('获取未读数量失败', error)
  }
}

// 切换标签
const handleTabChange = () => {
  pagination.page = 1
  fetchNotifications()
}

// 标记单条已读
const handleMarkRead = async (row: Notification) => {
  try {
    await notificationApi.markAsRead(row.id)
    row.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
    ElMessage.success('已标记为已读')
  } catch (error) {
    ElMessage.error('标记失败')
  }
}

// 全部标记已读
const handleMarkAllRead = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要将所有通知标记为已读吗？',
      '全部标记已读',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    await notificationApi.markAllAsRead()
    ElMessage.success('已全部标记为已读')
    unreadCount.value = 0
    fetchNotifications()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 点击行
const handleRowClick = async (row: Notification) => {
  // 如果未读，先标记已读
  if (!row.is_read) {
    try {
      await notificationApi.markAsRead(row.id)
      row.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (error) {
      console.error('标记已读失败', error)
    }
  }

  // 如果有关联链接，跳转
  if (row.related_url) {
    handleGoToRelated(row)
  }
}

// 跳转到相关页面
const handleGoToRelated = (row: Notification) => {
  if (!row.related_url) return

  // 判断是内部路由还是外部链接
  if (row.related_url.startsWith('http://') || row.related_url.startsWith('https://')) {
    window.open(row.related_url, '_blank')
  } else {
    router.push(row.related_url)
  }
}

// 行样式
const getRowClassName = ({ row }: { row: Notification }) => {
  return row.is_read ? 'read-row' : 'unread-row'
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 1分钟内
  if (diff < 60 * 1000) {
    return '刚刚'
  }
  // 1小时内
  if (diff < 60 * 60 * 1000) {
    return `${Math.floor(diff / (60 * 1000))}分钟前`
  }
  // 24小时内
  if (diff < 24 * 60 * 60 * 1000) {
    return `${Math.floor(diff / (60 * 60 * 1000))}小时前`
  }
  // 7天内
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    return `${Math.floor(diff / (24 * 60 * 60 * 1000))}天前`
  }

  // 超过7天显示完整日期
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 类型标签类型
const getTypeTagType = (type: string) => {
  const typeMap: Record<string, any> = {
    system: 'info',
    approval: 'warning',
    asset: 'primary',
    alert: 'danger',
    message: 'success'
  }
  return typeMap[type] || ''
}

// 类型标签文本
const getTypeLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    system: '系统通知',
    approval: '审批通知',
    asset: '资产通知',
    alert: '告警通知',
    message: '消息通知'
  }
  return labelMap[type] || type
}

onMounted(() => {
  fetchNotifications()
  fetchUnreadCount()
})
</script>

<style scoped lang="scss">
.notifications-container {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;

  :deep(.el-tabs) {
    flex: 1;
  }

  :deep(.el-tabs__header) {
    margin-bottom: 0;
  }
}

:deep(.unread-row) {
  background-color: #f0f9ff;
  font-weight: 500;
  cursor: pointer;

  &:hover {
    background-color: #e6f4ff;
  }
}

:deep(.read-row) {
  cursor: pointer;
  color: #909399;

  &:hover {
    background-color: #f5f7fa;
  }
}
</style>
