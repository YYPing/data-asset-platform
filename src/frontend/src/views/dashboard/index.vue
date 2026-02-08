<template>
  <div class="dashboard-container">
    <el-card class="welcome-card" shadow="hover">
      <div class="welcome-content">
        <h2 class="welcome-title">欢迎回来，{{ userStore.realName || userStore.username }}！</h2>
        <p class="welcome-subtitle">{{ getRoleLabel(userStore.role) }} · {{ userStore.organization }}</p>
      </div>
    </el-card>

    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6" v-for="stat in roleStats" :key="stat.title">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: stat.color }">
              <el-icon :size="32">
                <component :is="stat.icon" />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-title">{{ stat.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-row">
      <el-col :xs="24" :md="16">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">数据趋势</span>
            </div>
          </template>
          <div class="chart-placeholder">
            <el-empty description="图表数据加载中..." />
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="8">
        <el-card class="notice-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">最新通知</span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(notice, index) in notices"
              :key="index"
              :timestamp="notice.time"
              placement="top"
            >
              <div class="notice-item">{{ notice.content }}</div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="quick-actions-row">
      <el-col :span="24">
        <el-card class="actions-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">快捷操作</span>
            </div>
          </template>
          <div class="actions-grid">
            <div
              v-for="action in roleActions"
              :key="action.title"
              class="action-item"
              @click="handleAction(action.path)"
            >
              <el-icon :size="40" :color="action.color">
                <component :is="action.icon" />
              </el-icon>
              <div class="action-title">{{ action.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 获取角色标签
const getRoleLabel = (role: string): string => {
  const roleMap: Record<string, string> = {
    holder_admin: '持有方管理员',
    holder_user: '持有方用户',
    center_admin: '登记中心管理员',
    center_user: '登记中心用户',
    evaluator: '评估机构',
    auditor: '审计人员',
    sys_admin: '系统管理员',
  }
  return roleMap[role] || role
}

// 根据角色显示不同的统计数据
const roleStats = computed(() => {
  const role = userStore.role
  const statsMap: Record<string, any[]> = {
    holder_admin: [
      { title: '资产总数', value: '128', icon: 'Box', color: '#1890ff' },
      { title: '待提交材料', value: '5', icon: 'Document', color: '#52c41a' },
      { title: '审批中', value: '12', icon: 'Clock', color: '#faad14' },
      { title: '已登记', value: '98', icon: 'CircleCheck', color: '#13c2c2' },
    ],
    holder_user: [
      { title: '我的资产', value: '45', icon: 'Box', color: '#1890ff' },
      { title: '待处理', value: '3', icon: 'Document', color: '#52c41a' },
      { title: '审批中', value: '8', icon: 'Clock', color: '#faad14' },
      { title: '已完成', value: '32', icon: 'CircleCheck', color: '#13c2c2' },
    ],
    center_admin: [
      { title: '待审批', value: '23', icon: 'CircleCheck', color: '#1890ff' },
      { title: '待评估', value: '15', icon: 'DataAnalysis', color: '#52c41a' },
      { title: '本月登记', value: '67', icon: 'Box', color: '#faad14' },
      { title: '总资产数', value: '1,234', icon: 'TrendCharts', color: '#13c2c2' },
    ],
    center_user: [
      { title: '待处理', value: '18', icon: 'CircleCheck', color: '#1890ff' },
      { title: '处理中', value: '12', icon: 'Clock', color: '#52c41a' },
      { title: '本月完成', value: '45', icon: 'Box', color: '#faad14' },
      { title: '总计', value: '234', icon: 'TrendCharts', color: '#13c2c2' },
    ],
    evaluator: [
      { title: '待评估', value: '8', icon: 'DataAnalysis', color: '#1890ff' },
      { title: '评估中', value: '5', icon: 'Clock', color: '#52c41a' },
      { title: '本月完成', value: '23', icon: 'CircleCheck', color: '#faad14' },
      { title: '总计', value: '156', icon: 'TrendCharts', color: '#13c2c2' },
    ],
    auditor: [
      { title: '审计项目', value: '12', icon: 'List', color: '#1890ff' },
      { title: '异常记录', value: '3', icon: 'Warning', color: '#ff4d4f' },
      { title: '本月审计', value: '45', icon: 'Document', color: '#faad14' },
      { title: '总记录', value: '2,345', icon: 'TrendCharts', color: '#13c2c2' },
    ],
    sys_admin: [
      { title: '用户总数', value: '89', icon: 'User', color: '#1890ff' },
      { title: '在线用户', value: '23', icon: 'UserFilled', color: '#52c41a' },
      { title: '系统告警', value: '2', icon: 'Warning', color: '#ff4d4f' },
      { title: '数据字典', value: '156', icon: 'Collection', color: '#13c2c2' },
    ],
  }
  return statsMap[role] || statsMap.holder_user
})

// 根据角色显示不同的快捷操作
const roleActions = computed(() => {
  const role = userStore.role
  const actionsMap: Record<string, any[]> = {
    holder_admin: [
      { title: '新增资产', icon: 'Plus', color: '#1890ff', path: '/assets' },
      { title: '上传材料', icon: 'Upload', color: '#52c41a', path: '/materials' },
      { title: '查看审批', icon: 'View', color: '#faad14', path: '/workflow' },
    ],
    holder_user: [
      { title: '新增资产', icon: 'Plus', color: '#1890ff', path: '/assets' },
      { title: '上传材料', icon: 'Upload', color: '#52c41a', path: '/materials' },
    ],
    center_admin: [
      { title: '审批管理', icon: 'CircleCheck', color: '#1890ff', path: '/workflow' },
      { title: '评估管理', icon: 'DataAnalysis', color: '#52c41a', path: '/assessment' },
      { title: '统计分析', icon: 'TrendCharts', color: '#faad14', path: '/statistics' },
    ],
    center_user: [
      { title: '审批管理', icon: 'CircleCheck', color: '#1890ff', path: '/workflow' },
      { title: '资产查询', icon: 'Search', color: '#52c41a', path: '/assets' },
    ],
    evaluator: [
      { title: '待评估列表', icon: 'List', color: '#1890ff', path: '/assessment' },
      { title: '评估报告', icon: 'Document', color: '#52c41a', path: '/assessment' },
    ],
    auditor: [
      { title: '审计日志', icon: 'List', color: '#1890ff', path: '/audit' },
      { title: '统计分析', icon: 'TrendCharts', color: '#52c41a', path: '/statistics' },
    ],
    sys_admin: [
      { title: '用户管理', icon: 'User', color: '#1890ff', path: '/system/users' },
      { title: '角色管理', icon: 'UserFilled', color: '#52c41a', path: '/system/roles' },
      { title: '系统配置', icon: 'Setting', color: '#faad14', path: '/system/config' },
    ],
  }
  return actionsMap[role] || actionsMap.holder_user
})

// 通知列表（示例数据）
const notices = [
  { time: '2026-02-08 10:30', content: '系统将于今晚22:00进行维护升级' },
  { time: '2026-02-07 15:20', content: '新版本功能培训将于下周三举行' },
  { time: '2026-02-06 09:15', content: '本月数据资产登记工作总结会议通知' },
  { time: '2026-02-05 14:00', content: '评估标准更新，请及时查看' },
]

// 处理快捷操作点击
const handleAction = (path: string) => {
  router.push(path)
}
</script>

<style scoped>
.dashboard-container {
  width: 100%;
}

.welcome-card {
  margin-bottom: 20px;
}

.welcome-content {
  padding: 20px 0;
}

.welcome-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.welcome-subtitle {
  font-size: 14px;
  color: #666;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.stat-title {
  font-size: 14px;
  color: #666;
}

.content-row {
  margin-bottom: 20px;
}

.chart-card,
.notice-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notice-item {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

.quick-actions-row {
  margin-bottom: 20px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 20px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-item:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.2);
  transform: translateY(-2px);
}

.action-title {
  margin-top: 12px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

@media (max-width: 768px) {
  .actions-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 12px;
  }

  .action-item {
    padding: 16px;
  }
}
</style>
