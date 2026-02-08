<template>
  <div class="holder-screen">
    <!-- Header Row -->
    <div class="screen-header">
      <div class="header-left">
        <div class="logo-container">
          <div class="logo-icon">📊</div>
          <h1 class="screen-title">数据资产管理驾驶舱</h1>
        </div>
      </div>
      <div class="header-right">
        <div class="current-time">
          <span class="time-text">{{ currentTime }}</span>
          <span class="date-text">{{ currentDate }}</span>
        </div>
      </div>
    </div>

    <!-- Main Content - Row 2: Three Columns -->
    <div class="content-row row-2">
      <!-- Left: Asset Statistics -->
      <div class="panel-card stats-panel">
        <div class="card-header">
          <h3 class="card-title">我的资产统计</h3>
          <div class="title-decoration"></div>
        </div>
        <div class="card-body">
          <div class="stat-item main-stat">
            <div class="stat-label">资产总数</div>
            <div class="stat-value glow-number">{{ animatedTotal }}</div>
            <div class="stat-unit">个</div>
          </div>
          <div class="stat-grid">
            <div class="stat-item">
              <div class="stat-icon status-draft">📝</div>
              <div class="stat-info">
                <div class="stat-label">草稿</div>
                <div class="stat-value">{{ animatedDraft }}</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon status-pending">⏳</div>
              <div class="stat-info">
                <div class="stat-label">待审批</div>
                <div class="stat-value">{{ animatedPending }}</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon status-approved">✅</div>
              <div class="stat-info">
                <div class="stat-label">已确权</div>
                <div class="stat-value">{{ animatedApproved }}</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon status-rejected">❌</div>
              <div class="stat-info">
                <div class="stat-label">已驳回</div>
                <div class="stat-value">{{ animatedRejected }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Center: Category Distribution & Material Completeness -->
      <div class="panel-card center-panel">
        <div class="card-header">
          <h3 class="card-title">资产分类分布</h3>
          <div class="title-decoration"></div>
        </div>
        <div class="card-body">
          <div class="chart-placeholder">
            <div class="chart-icon">📊</div>
            <div class="chart-text">接入 ECharts 饼图</div>
            <div class="chart-hint">显示各类别资产占比</div>
          </div>
        </div>
        
        <div class="card-header mt-20">
          <h3 class="card-title">材料完整度</h3>
          <div class="title-decoration"></div>
        </div>
        <div class="card-body">
          <div class="progress-list">
            <div v-for="item in materialCompleteness" :key="item.name" class="progress-item">
              <div class="progress-header">
                <span class="progress-label">{{ item.name }}</span>
                <span class="progress-value">{{ item.percentage }}%</span>
              </div>
              <div class="progress-bar-container">
                <div 
                  class="progress-bar-fill" 
                  :style="{ width: item.percentage + '%', backgroundColor: item.color }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Recent Activities -->
      <div class="panel-card activities-panel">
        <div class="card-header">
          <h3 class="card-title">最近动态</h3>
          <div class="title-decoration"></div>
        </div>
        <div class="card-body">
          <div class="activity-list">
            <div 
              v-for="(activity, index) in recentActivities" 
              :key="index" 
              class="activity-item"
              :style="{ animationDelay: index * 0.1 + 's' }"
            >
              <div class="activity-time">{{ activity.time }}</div>
              <div class="activity-content">
                <div class="activity-icon" :class="activity.type">{{ activity.icon }}</div>
                <div class="activity-text">
                  <div class="activity-title">{{ activity.title }}</div>
                  <div class="activity-desc">{{ activity.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Row - Row 3: Two Columns -->
    <div class="content-row row-3">
      <!-- Left: Registration Trend -->
      <div class="panel-card trend-panel">
        <div class="card-header">
          <h3 class="card-title">资产注册趋势</h3>
          <div class="title-decoration"></div>
        </div>
        <div class="card-body">
          <div class="chart-placeholder large">
            <div class="chart-icon">📈</div>
            <div class="chart-text">接入 ECharts 折线图</div>
            <div class="chart-hint">显示近12个月资产注册趋势</div>
          </div>
        </div>
      </div>

      <!-- Right: Todo List -->
      <div class="panel-card todo-panel">
        <div class="card-header">
          <h3 class="card-title">待办事项</h3>
          <div class="title-decoration"></div>
          <span class="todo-count">{{ todoList.length }}</span>
        </div>
        <div class="card-body">
          <div class="todo-list">
            <div 
              v-for="(todo, index) in todoList" 
              :key="index" 
              class="todo-item"
              :class="'priority-' + todo.priority"
            >
              <div class="todo-priority">
                <span class="priority-badge">{{ todo.priorityText }}</span>
              </div>
              <div class="todo-content">
                <div class="todo-title">{{ todo.title }}</div>
                <div class="todo-meta">
                  <span class="todo-asset">{{ todo.assetName }}</span>
                  <span class="todo-deadline">截止: {{ todo.deadline }}</span>
                </div>
              </div>
              <div class="todo-action">
                <el-button type="primary" size="small" text>处理</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

// Time display
const currentTime = ref('')
const currentDate = ref('')

// Animated numbers
const animatedTotal = ref(0)
const animatedDraft = ref(0)
const animatedPending = ref(0)
const animatedApproved = ref(0)
const animatedRejected = ref(0)

// Target values
const targetTotal = ref(0)
const targetDraft = ref(0)
const targetPending = ref(0)
const targetApproved = ref(0)
const targetRejected = ref(0)

// Material completeness data
const materialCompleteness = ref([
  { name: '基本信息', percentage: 95, color: '#52c41a' },
  { name: '权属证明', percentage: 78, color: '#1890ff' },
  { name: '技术文档', percentage: 62, color: '#faad14' },
  { name: '评估报告', percentage: 45, color: '#ff4d4f' }
])

// Recent activities
const recentActivities = ref([
  { time: '10:23', icon: '✅', type: 'success', title: '资产审批通过', description: '数据资产-客户画像数据集 已通过审批' },
  { time: '09:45', icon: '📝', type: 'info', title: '材料已上传', description: '上传了权属证明文件' },
  { time: '09:12', icon: '🔄', type: 'warning', title: '资产待补正', description: '数据资产-交易流水数据 需要补充材料' },
  { time: '昨天', icon: '✅', type: 'success', title: '资产登记完成', description: '数据资产-用户行为数据 登记成功' },
  { time: '昨天', icon: '📤', type: 'info', title: '提交审批', description: '数据资产-风控模型数据 已提交审批' },
  { time: '2天前', icon: '✏️', type: 'info', title: '创建草稿', description: '创建了新的资产登记草稿' },
  { time: '2天前', icon: '❌', type: 'error', title: '审批驳回', description: '数据资产-营销数据集 被驳回，需修改' },
  { time: '3天前', icon: '✅', type: 'success', title: '确权完成', description: '数据资产-产品目录数据 确权成功' },
  { time: '3天前', icon: '📝', type: 'info', title: '材料更新', description: '更新了技术文档' },
  { time: '4天前', icon: '🔄', type: 'warning', title: '待办提醒', description: '有3个资产需要补充材料' }
])

// Todo list
const todoList = ref([
  { 
    priority: 'high', 
    priorityText: '紧急', 
    title: '补充权属证明材料', 
    assetName: '客户画像数据集',
    deadline: '今天 18:00'
  },
  { 
    priority: 'high', 
    priorityText: '紧急', 
    title: '修改资产描述信息', 
    assetName: '交易流水数据',
    deadline: '明天 12:00'
  },
  { 
    priority: 'medium', 
    priorityText: '普通', 
    title: '上传技术文档', 
    assetName: '用户行为数据',
    deadline: '2月10日'
  },
  { 
    priority: 'medium', 
    priorityText: '普通', 
    title: '完善评估报告', 
    assetName: '风控模型数据',
    deadline: '2月11日'
  },
  { 
    priority: 'low', 
    priorityText: '低', 
    title: '更新资产标签', 
    assetName: '营销数据集',
    deadline: '2月15日'
  }
])

// Update time
const updateTime = () => {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  currentTime.value = `${hours}:${minutes}:${seconds}`
  
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  const weekday = weekdays[now.getDay()]
  currentDate.value = `${year}年${month}月${day}日 ${weekday}`
}

// Animate number counting
const animateNumber = (current: any, target: number, duration: number = 2000) => {
  const start = current.value
  const range = target - start
  const increment = range / (duration / 16)
  const startTime = Date.now()
  
  const timer = setInterval(() => {
    const elapsed = Date.now() - startTime
    if (elapsed >= duration) {
      current.value = target
      clearInterval(timer)
    } else {
      current.value = Math.floor(start + increment * (elapsed / 16))
    }
  }, 16)
}

// Fetch data from API
const fetchOverviewData = async () => {
  try {
    const response = await axios.get('/api/v1/statistics/overview')
    const data = response.data
    
    targetTotal.value = data.total || 156
    targetDraft.value = data.by_status?.draft || 12
    targetPending.value = data.by_status?.pending || 8
    targetApproved.value = data.by_status?.approved || 128
    targetRejected.value = data.by_status?.rejected || 8
    
    // Trigger animations
    animateNumber(animatedTotal, targetTotal.value)
    animateNumber(animatedDraft, targetDraft.value)
    animateNumber(animatedPending, targetPending.value)
    animateNumber(animatedApproved, targetApproved.value)
    animateNumber(animatedRejected, targetRejected.value)
  } catch (error) {
    console.error('Failed to fetch overview data:', error)
    // Use mock data
    targetTotal.value = 156
    targetDraft.value = 12
    targetPending.value = 8
    targetApproved.value = 128
    targetRejected.value = 8
    
    animateNumber(animatedTotal, targetTotal.value)
    animateNumber(animatedDraft, targetDraft.value)
    animateNumber(animatedPending, targetPending.value)
    animateNumber(animatedApproved, targetApproved.value)
    animateNumber(animatedRejected, targetRejected.value)
  }
}

let timeInterval: any = null

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  fetchOverviewData()
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.holder-screen {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #0a1628 0%, #0d1b2a 50%, #0a1628 100%);
  padding: 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: hidden;
  --bg-primary: #0a1628;
  --bg-card: #0d2137;
  --border-glow: #1890ff;
  --text-primary: #e0e6ed;
  --text-number: #00d4ff;
}

/* Header */
.screen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 80px;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo-icon {
  font-size: 48px;
  filter: drop-shadow(0 0 10px rgba(24, 144, 255, 0.6));
}

.screen-title {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  text-shadow: 0 0 20px rgba(24, 144, 255, 0.5);
  letter-spacing: 2px;
}

.header-right {
  display: flex;
  align-items: center;
}

.current-time {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.time-text {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-number);
  font-family: 'Courier New', monospace;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.6);
}

.date-text {
  font-size: 16px;
  color: var(--text-primary);
  opacity: 0.8;
}

/* Content Rows */
.content-row {
  display: flex;
  gap: 20px;
  flex: 1;
  min-height: 0;
}

.row-2 {
  flex: 1.2;
}

.row-3 {
  flex: 1;
}

/* Panel Cards */
.panel-card {
  background: var(--bg-card);
  border: 1px solid rgba(24, 144, 255, 0.3);
  border-radius: 8px;
  backdrop-filter: blur(10px);
  padding: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), 0 0 40px rgba(24, 144, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.panel-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--border-glow), transparent);
  animation: borderGlow 3s ease-in-out infinite;
}

@keyframes borderGlow {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  position: relative;
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.title-decoration {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, var(--border-glow), transparent);
  opacity: 0.5;
}

.card-body {
  flex: 1;
  overflow: auto;
}

.card-body::-webkit-scrollbar {
  width: 6px;
}

.card-body::-webkit-scrollbar-thumb {
  background: rgba(24, 144, 255, 0.3);
  border-radius: 3px;
}

/* Stats Panel */
.stats-panel {
  flex: 1;
}

.stat-item {
  text-align: center;
}

.main-stat {
  margin-bottom: 30px;
  padding: 20px;
  background: rgba(24, 144, 255, 0.05);
  border-radius: 8px;
}

.main-stat .stat-label {
  font-size: 18px;
  color: var(--text-primary);
  opacity: 0.8;
  margin-bottom: 10px;
}

.main-stat .stat-value {
  font-size: 64px;
  font-weight: 700;
  color: var(--text-number);
  font-family: 'Arial', sans-serif;
  line-height: 1;
}

.glow-number {
  text-shadow: 0 0 20px rgba(0, 212, 255, 0.8), 0 0 40px rgba(0, 212, 255, 0.4);
  animation: numberPulse 2s ease-in-out infinite;
}

@keyframes numberPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.main-stat .stat-unit {
  font-size: 20px;
  color: var(--text-primary);
  opacity: 0.6;
  margin-top: 5px;
}

.stat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.stat-grid .stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(24, 144, 255, 0.2);
  border-radius: 6px;
  transition: all 0.3s ease;
}

.stat-grid .stat-item:hover {
  background: rgba(24, 144, 255, 0.1);
  border-color: var(--border-glow);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 32px;
  filter: drop-shadow(0 0 8px rgba(24, 144, 255, 0.5));
}

.stat-info {
  flex: 1;
  text-align: left;
}

.stat-grid .stat-label {
  font-size: 14px;
  color: var(--text-primary);
  opacity: 0.7;
  margin-bottom: 5px;
}

.stat-grid .stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-number);
  font-family: 'Arial', sans-serif;
}

/* Center Panel */
.center-panel {
  flex: 1;
}

.mt-20 {
  margin-top: 20px;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  background: rgba(24, 144, 255, 0.05);
  border: 2px dashed rgba(24, 144, 255, 0.3);
  border-radius: 8px;
}

.chart-placeholder.large {
  height: 100%;
  min-height: 300px;
}

.chart-icon {
  font-size: 48px;
  margin-bottom: 10px;
  opacity: 0.6;
}

.chart-text {
  font-size: 18px;
  color: var(--text-primary);
  opacity: 0.8;
  margin-bottom: 5px;
}

.chart-hint {
  font-size: 14px;
  color: var(--text-primary);
  opacity: 0.5;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.progress-item {
  padding: 10px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.progress-label {
  font-size: 14px;
  color: var(--text-primary);
}

.progress-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-number);
}

.progress-bar-container {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 1s ease-out;
  box-shadow: 0 0 10px currentColor;
}

/* Activities Panel */
.activities-panel {
  flex: 1;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-left: 3px solid var(--border-glow);
  border-radius: 4px;
  transition: all 0.3s ease;
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.activity-item:hover {
  background: rgba(24, 144, 255, 0.1);
  transform: translateX(5px);
}

.activity-time {
  font-size: 12px;
  color: var(--text-primary);
  opacity: 0.5;
  margin-bottom: 8px;
}

.activity-content {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.activity-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.activity-text {
  flex: 1;
}

.activity-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.activity-desc {
  font-size: 13px;
  color: var(--text-primary);
  opacity: 0.7;
}

/* Trend Panel */
.trend-panel {
  flex: 1.5;
}

/* Todo Panel */
.todo-panel {
  flex: 1;
}

.todo-count {
  background: var(--border-glow);
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  margin-left: auto;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(24, 144, 255, 0.2);
  border-radius: 6px;
  transition: all 0.3s ease;
}

.todo-item:hover {
  background: rgba(24, 144, 255, 0.1);
  border-color: var(--border-glow);
  transform: translateY(-2px);
}

.todo-item.priority-high {
  border-left: 3px solid #ff4d4f;
}

.todo-item.priority-medium {
  border-left: 3px solid #faad14;
}

.todo-item.priority-low {
  border-left: 3px solid #52c41a;
}

.priority-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.priority-high .priority-badge {
  background: rgba(255, 77, 79, 0.2);
  color: #ff4d4f;
}

.priority-medium .priority-badge {
  background: rgba(250, 173, 20, 0.2);
  color: #faad14;
}

.priority-low .priority-badge {
  background: rgba(82, 196, 26, 0.2);
  color: #52c41a;
}

.todo-content {
  flex: 1;
}

.todo-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.todo-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: var(--text-primary);
  opacity: 0.6;
}

.todo-action {
  flex-shrink: 0;
}
</style>
