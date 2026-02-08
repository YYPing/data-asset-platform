<template>
  <div class="center-screen">
    <!-- 顶部标题栏 -->
    <header class="screen-header">
      <div class="header-left">
        <div class="logo">📊</div>
        <h1 class="title">数据资产登记中心监控大屏</h1>
      </div>
      <div class="header-right">
        <span class="current-time">{{ currentTime }}</span>
      </div>
    </header>

    <!-- 第二行：4个核心指标 -->
    <section class="stats-row">
      <div class="stat-card" v-for="item in coreStats" :key="item.label">
        <div class="stat-icon" :style="{ background: item.gradient }">
          <span>{{ item.icon }}</span>
        </div>
        <div class="stat-info">
          <div class="stat-number" :style="{ color: item.color }">
            {{ animatedNumbers[item.key] ?? 0 }}
          </div>
          <div class="stat-label">{{ item.label }}</div>
          <div class="stat-sub" v-if="item.sub">{{ item.sub }}</div>
        </div>
      </div>
    </section>

    <!-- 第三行：3列布局 -->
    <section class="main-content">
      <!-- 左：组织资产排名 -->
      <div class="panel panel-left">
        <div class="panel-header">
          <span class="panel-title">📈 各组织资产排名</span>
        </div>
        <div class="panel-body">
          <div class="chart-placeholder">
            <p>此处接入 ECharts 横向柱状图</p>
          </div>
          <div class="org-table">
            <div class="org-row org-header">
              <span class="org-rank">排名</span>
              <span class="org-name">组织名称</span>
              <span class="org-total">资产数</span>
              <span class="org-confirmed">已确权</span>
              <span class="org-value">总估值(万)</span>
            </div>
            <div
              class="org-row"
              v-for="(org, index) in orgStats"
              :key="org.org_name"
            >
              <span class="org-rank">
                <span :class="['rank-badge', index < 3 ? 'top' : '']">
                  {{ index + 1 }}
                </span>
              </span>
              <span class="org-name">{{ org.org_name }}</span>
              <span class="org-total">{{ org.total }}</span>
              <span class="org-confirmed">{{ org.confirmed }}</span>
              <span class="org-value">{{ formatValue(org.total_value) }}</span>
            </div>
            <div v-if="orgStats.length === 0" class="empty-tip">暂无数据</div>
          </div>
        </div>
      </div>

      <!-- 中：审批效率面板 -->
      <div class="panel panel-center">
        <div class="panel-header">
          <span class="panel-title">⚡ 审批效率监控</span>
        </div>
        <div class="panel-body">
          <div class="efficiency-grid">
            <div class="efficiency-item">
              <div class="gauge-circle" :style="gaugeStyle(workflowStats.approval_rate)">
                <span class="gauge-value">{{ workflowStats.approval_rate }}%</span>
              </div>
              <div class="efficiency-label">通过率</div>
            </div>
            <div class="efficiency-item">
              <div class="gauge-circle reject" :style="gaugeStyle(workflowStats.reject_rate)">
                <span class="gauge-value">{{ workflowStats.reject_rate }}%</span>
              </div>
              <div class="efficiency-label">驳回率</div>
            </div>
            <div class="efficiency-item">
              <div class="gauge-circle timeout" :style="gaugeStyle(workflowStats.timeout_rate)">
                <span class="gauge-value">{{ workflowStats.timeout_rate }}%</span>
              </div>
              <div class="efficiency-label">超时率</div>
            </div>
            <div class="efficiency-item">
              <div class="duration-display">
                <span class="duration-number">{{ workflowStats.avg_duration_hours }}</span>
                <span class="duration-unit">小时</span>
              </div>
              <div class="efficiency-label">平均审批时长</div>
            </div>
          </div>
          <!-- 评估统计 -->
          <div class="assess-section">
            <h3 class="section-subtitle">评估概况</h3>
            <div class="assess-grid">
              <div class="assess-item">
                <span class="assess-value">{{ assessStats.compliance_pass_rate }}%</span>
                <span class="assess-label">合规通过率</span>
              </div>
              <div class="assess-item">
                <span class="assess-value">{{ assessStats.avg_score }}</span>
                <span class="assess-label">平均评分</span>
              </div>
              <div class="assess-item risk-high">
                <span class="assess-value">{{ assessStats.risk_distribution?.high ?? 0 }}</span>
                <span class="assess-label">高风险</span>
              </div>
              <div class="assess-item risk-medium">
                <span class="assess-value">{{ assessStats.risk_distribution?.medium ?? 0 }}</span>
                <span class="assess-label">中风险</span>
              </div>
              <div class="assess-item risk-low">
                <span class="assess-value">{{ assessStats.risk_distribution?.low ?? 0 }}</span>
                <span class="assess-label">低风险</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右：风险预警列表 -->
      <div class="panel panel-right">
        <div class="panel-header">
          <span class="panel-title">🚨 风险预警</span>
          <span class="warning-count">{{ warnings.length }} 条</span>
        </div>
        <div class="panel-body">
          <div class="warning-list" ref="warningListRef">
            <div
              class="warning-item"
              v-for="(warn, index) in warnings"
              :key="index"
              :class="warn.level"
            >
              <div class="warning-icon">
                {{ warn.level === 'high' ? '🔴' : warn.level === 'medium' ? '🟡' : '🟠' }}
              </div>
              <div class="warning-content">
                <div class="warning-title">{{ warn.title }}</div>
                <div class="warning-desc">{{ warn.desc }}</div>
                <div class="warning-time">{{ warn.time }}</div>
              </div>
            </div>
            <div v-if="warnings.length === 0" class="empty-tip">暂无预警</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import request from '@/api/request'

// ─── 时钟 ───────────────────────────────────────────
const currentTime = ref('')
let clockTimer: ReturnType<typeof setInterval>

function updateClock() {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false,
  })
}

// ─── 数据 ───────────────────────────────────────────
interface OverviewData {
  total: number
  by_status: Record<string, number>
  by_stage: Record<string, number>
  monthly_new: number
  pending_approval: number
}

interface OrgStat {
  org_name: string
  total: number
  confirmed: number
  total_value: number
}

interface WorkflowStat {
  avg_duration_hours: number
  approval_rate: number
  reject_rate: number
  timeout_rate: number
}

interface AssessStat {
  compliance_pass_rate: number
  avg_score: number
  risk_distribution: Record<string, number>
}

interface Warning {
  level: 'high' | 'medium' | 'low'
  title: string
  desc: string
  time: string
}

const overview = ref<OverviewData>({
  total: 0, by_status: {}, by_stage: {}, monthly_new: 0, pending_approval: 0,
})
const orgStats = ref<OrgStat[]>([])
const workflowStats = ref<WorkflowStat>({
  avg_duration_hours: 0, approval_rate: 0, reject_rate: 0, timeout_rate: 0,
})
const assessStats = ref<AssessStat>({
  compliance_pass_rate: 0, avg_score: 0, risk_distribution: {},
})
const warnings = ref<Warning[]>([])

// ─── 数字动画 ────────────────────────────────────────
const animatedNumbers = reactive<Record<string, number>>({
  total: 0, confirmed: 0, pending: 0, monthly: 0,
})

function animateNumber(key: string, target: number, duration = 1500) {
  const start = animatedNumbers[key] || 0
  const diff = target - start
  const startTime = Date.now()
  function step() {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    animatedNumbers[key] = Math.round(start + diff * eased)
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

// ─── 核心指标卡片 ────────────────────────────────────
const coreStats = ref([
  {
    key: 'total', label: '资产总量', icon: '📦',
    color: '#00d4ff', gradient: 'linear-gradient(135deg, #0066cc, #00d4ff)',
    sub: '',
  },
  {
    key: 'confirmed', label: '已确权资产', icon: '✅',
    color: '#00e676', gradient: 'linear-gradient(135deg, #00875a, #00e676)',
    sub: '',
  },
  {
    key: 'pending', label: '待审批数量', icon: '⏳',
    color: '#ffab00', gradient: 'linear-gradient(135deg, #cc7700, #ffab00)',
    sub: '',
  },
  {
    key: 'monthly', label: '本月新增', icon: '📈',
    color: '#e040fb', gradient: 'linear-gradient(135deg, #9c27b0, #e040fb)',
    sub: '',
  },
])

// ─── 仪表盘样式 ──────────────────────────────────────
function gaugeStyle(value: number) {
  const deg = (value / 100) * 360
  return {
    background: `conic-gradient(var(--border-glow) ${deg}deg, rgba(255,255,255,0.05) ${deg}deg)`,
  }
}

function formatValue(val: number): string {
  if (!val) return '0'
  return (val / 10000).toFixed(1)
}

// ─── 数据加载 ────────────────────────────────────────
async function loadData() {
  try {
    const [overviewRes, orgRes, wfRes, assessRes] = await Promise.allSettled([
      request.get('/api/v1/statistics/overview'),
      request.get('/api/v1/statistics/by-organization'),
      request.get('/api/v1/statistics/workflow'),
      request.get('/api/v1/statistics/assessment'),
    ])

    if (overviewRes.status === 'fulfilled' && overviewRes.value?.data?.data) {
      const d = overviewRes.value.data.data
      overview.value = d
      const confirmed = (d.by_stage?.confirmation ?? 0) + (d.by_stage?.valuation ?? 0) +
        (d.by_stage?.accounting ?? 0) + (d.by_stage?.operation ?? 0)
      animateNumber('total', d.total)
      animateNumber('confirmed', confirmed)
      animateNumber('pending', d.pending_approval)
      animateNumber('monthly', d.monthly_new)
      coreStats.value[1].sub = `确权率 ${d.total > 0 ? ((confirmed / d.total) * 100).toFixed(1) : 0}%`
    }

    if (orgRes.status === 'fulfilled' && orgRes.value?.data?.data) {
      orgStats.value = orgRes.value.data.data.slice(0, 10)
    }

    if (wfRes.status === 'fulfilled' && wfRes.value?.data?.data) {
      workflowStats.value = wfRes.value.data.data
    }

    if (assessRes.status === 'fulfilled' && assessRes.value?.data?.data) {
      assessStats.value = assessRes.value.data.data
    }

    // 生成预警数据
    generateWarnings()
  } catch (e) {
    console.error('加载大屏数据失败:', e)
  }
}

function generateWarnings() {
  const list: Warning[] = []
  const risk = assessStats.value.risk_distribution || {}
  if ((risk.high ?? 0) > 0) {
    list.push({
      level: 'high', title: '高风险资产预警',
      desc: `当前有 ${risk.high} 项资产被评估为高风险，请及时处理`,
      time: new Date().toLocaleTimeString('zh-CN'),
    })
  }
  if (workflowStats.value.timeout_rate > 10) {
    list.push({
      level: 'medium', title: '审批超时预警',
      desc: `当前审批超时率 ${workflowStats.value.timeout_rate}%，超过10%阈值`,
      time: new Date().toLocaleTimeString('zh-CN'),
    })
  }
  if (overview.value.pending_approval > 20) {
    list.push({
      level: 'medium', title: '待审批积压',
      desc: `当前有 ${overview.value.pending_approval} 项待审批，建议加快处理`,
      time: new Date().toLocaleTimeString('zh-CN'),
    })
  }
  if (workflowStats.value.reject_rate > 30) {
    list.push({
      level: 'low', title: '驳回率偏高',
      desc: `当前驳回率 ${workflowStats.value.reject_rate}%，建议加强申报指导`,
      time: new Date().toLocaleTimeString('zh-CN'),
    })
  }
  warnings.value = list
}

// ─── 滚动动画 ────────────────────────────────────────
const warningListRef = ref<HTMLElement>()
let scrollTimer: ReturnType<typeof setInterval>

function startScroll() {
  scrollTimer = setInterval(() => {
    const el = warningListRef.value
    if (!el) return
    if (el.scrollTop + el.clientHeight >= el.scrollHeight - 10) {
      el.scrollTop = 0
    } else {
      el.scrollTop += 1
    }
  }, 50)
}

// ─── 生命周期 ────────────────────────────────────────
let refreshTimer: ReturnType<typeof setInterval>

onMounted(() => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
  loadData()
  refreshTimer = setInterval(loadData, 60000)
  setTimeout(startScroll, 2000)
})

onUnmounted(() => {
  clearInterval(clockTimer)
  clearInterval(refreshTimer)
  clearInterval(scrollTimer)
})
</script>

<style scoped>
:root {
  --bg-primary: #0a1628;
  --bg-card: #0d2137;
  --border-glow: #1890ff;
  --text-primary: #e0e6ed;
  --text-number: #00d4ff;
  --text-secondary: #7a8ba0;
}

.center-screen {
  width: 100vw;
  height: 100vh;
  background: var(--bg-primary, #0a1628);
  color: var(--text-primary, #e0e6ed);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* ─── 顶部 ─── */
.screen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  background: linear-gradient(180deg, rgba(24, 144, 255, 0.15), transparent);
  border-bottom: 1px solid rgba(24, 144, 255, 0.2);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo {
  font-size: 32px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  background: linear-gradient(90deg, #00d4ff, #1890ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 4px;
}

.current-time {
  font-size: 18px;
  color: var(--text-secondary, #7a8ba0);
  font-variant-numeric: tabular-nums;
}

/* ─── 核心指标行 ─── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 20px 32px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: var(--bg-card, #0d2137);
  border: 1px solid rgba(24, 144, 255, 0.3);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.2);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary, #7a8ba0);
  margin-top: 2px;
}

.stat-sub {
  font-size: 12px;
  color: #00e676;
  margin-top: 2px;
}

/* ─── 主内容区 ─── */
.main-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
  padding: 0 32px 20px;
  min-height: 0;
}

.panel {
  background: var(--bg-card, #0d2137);
  border: 1px solid rgba(24, 144, 255, 0.3);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid rgba(24, 144, 255, 0.15);
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
}

.warning-count {
  font-size: 13px;
  color: #ff5252;
  background: rgba(255, 82, 82, 0.15);
  padding: 2px 10px;
  border-radius: 10px;
}

.panel-body {
  flex: 1;
  padding: 16px 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* ─── 组织排名 ─── */
.chart-placeholder {
  height: 120px;
  border: 1px dashed rgba(24, 144, 255, 0.3);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary, #7a8ba0);
  font-size: 13px;
  margin-bottom: 12px;
  flex-shrink: 0;
}

.org-table {
  flex: 1;
  overflow-y: auto;
}

.org-row {
  display: grid;
  grid-template-columns: 50px 1fr 60px 60px 80px;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 13px;
}

.org-header {
  color: var(--text-secondary, #7a8ba0);
  font-weight: 600;
  font-size: 12px;
}

.rank-badge {
  display: inline-flex;
  width: 24px;
  height: 24px;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.05);
}

.rank-badge.top {
  background: linear-gradient(135deg, #ffab00, #ff6d00);
  color: #fff;
}

.org-value {
  color: var(--text-number, #00d4ff);
  text-align: right;
}

.org-total, .org-confirmed {
  text-align: center;
}

/* ─── 审批效率 ─── */
.efficiency-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.efficiency-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.gauge-circle {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.gauge-circle::after {
  content: '';
  position: absolute;
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: var(--bg-card, #0d2137);
}

.gauge-value {
  position: relative;
  z-index: 1;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-number, #00d4ff);
}

.gauge-circle.reject .gauge-value { color: #ff5252; }
.gauge-circle.timeout .gauge-value { color: #ffab00; }

.efficiency-label {
  font-size: 13px;
  color: var(--text-secondary, #7a8ba0);
}

.duration-display {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.duration-number {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-number, #00d4ff);
}

.duration-unit {
  font-size: 14px;
  color: var(--text-secondary, #7a8ba0);
}

/* ─── 评估概况 ─── */
.assess-section {
  border-top: 1px solid rgba(24, 144, 255, 0.15);
  padding-top: 16px;
}

.section-subtitle {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary, #e0e6ed);
}

.assess-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.assess-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 4px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}

.assess-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-number, #00d4ff);
}

.assess-label {
  font-size: 11px;
  color: var(--text-secondary, #7a8ba0);
}

.risk-high .assess-value { color: #ff5252; }
.risk-medium .assess-value { color: #ffab00; }
.risk-low .assess-value { color: #00e676; }

/* ─── 风险预警 ─── */
.warning-list {
  flex: 1;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.warning-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  margin-bottom: 10px;
  border-radius: 8px;
  border-left: 3px solid;
  background: rgba(255, 255, 255, 0.03);
}

.warning-item.high {
  border-left-color: #ff5252;
  background: rgba(255, 82, 82, 0.08);
}

.warning-item.medium {
  border-left-color: #ffab00;
  background: rgba(255, 171, 0, 0.08);
}

.warning-item.low {
  border-left-color: #ff6d00;
  background: rgba(255, 109, 0, 0.06);
}

.warning-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.warning-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.warning-desc {
  font-size: 12px;
  color: var(--text-secondary, #7a8ba0);
  line-height: 1.5;
}

.warning-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  margin-top: 4px;
}

.empty-tip {
  text-align: center;
  color: var(--text-secondary, #7a8ba0);
  padding: 40px 0;
  font-size: 14px;
}

/* ─── 滚动条 ─── */
.panel-body::-webkit-scrollbar,
.org-table::-webkit-scrollbar,
.warning-list::-webkit-scrollbar {
  width: 4px;
}

.panel-body::-webkit-scrollbar-thumb,
.org-table::-webkit-scrollbar-thumb,
.warning-list::-webkit-scrollbar-thumb {
  background: rgba(24, 144, 255, 0.3);
  border-radius: 2px;
}
</style>
