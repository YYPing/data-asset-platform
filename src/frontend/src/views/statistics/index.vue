<template>
  <div class="statistics-container">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409eff">
              <el-icon :size="32"><DataAnalysis /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">资产总数</div>
              <div class="stat-value">{{ overview.total }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67c23a">
              <el-icon :size="32"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">已确权</div>
              <div class="stat-value">{{ overview.by_status?.confirmed || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #e6a23c">
              <el-icon :size="32"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">待审批</div>
              <div class="stat-value">{{ overview.pending_approval }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #f56c6c">
              <el-icon :size="32"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">本月新增</div>
              <div class="stat-value">{{ overview.monthly_new }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势图区域 -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>资产趋势分析</span>
        </div>
      </template>
      <div class="chart-placeholder">
        <el-icon :size="64" color="#909399"><TrendCharts /></el-icon>
        <div class="placeholder-text">此处接入 ECharts 趋势图</div>
        <div class="placeholder-hint">
          数据已准备：{{ trendData.length }} 个月的趋势数据
        </div>
        <el-button type="primary" text @click="showTrendData">查看原始数据</el-button>
      </div>
    </el-card>

    <!-- 组织排名和分类分布 -->
    <el-row :gutter="20">
      <!-- 组织排名 -->
      <el-col :span="12">
        <el-card v-loading="loadingOrg">
          <template #header>
            <div class="card-header">
              <span>组织资产排名</span>
              <el-tag type="info">TOP {{ orgStats.length }}</el-tag>
            </div>
          </template>
          <el-table :data="orgStats" stripe max-height="400">
            <el-table-column type="index" label="排名" width="70" align="center">
              <template #default="{ $index }">
                <el-tag
                  v-if="$index < 3"
                  :type="['danger', 'warning', 'success'][$index]"
                  effect="dark"
                  size="small"
                >
                  {{ $index + 1 }}
                </el-tag>
                <span v-else>{{ $index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="org_name" label="组织名称" min-width="150" show-overflow-tooltip />
            <el-table-column prop="total" label="资产总数" width="100" align="right">
              <template #default="{ row }">
                <el-text type="primary" style="font-weight: 600">{{ row.total }}</el-text>
              </template>
            </el-table-column>
            <el-table-column prop="confirmed" label="已确权" width="100" align="right">
              <template #default="{ row }">
                <el-text type="success">{{ row.confirmed }}</el-text>
              </template>
            </el-table-column>
            <el-table-column label="确权率" width="100" align="right">
              <template #default="{ row }">
                <el-progress
                  :percentage="Math.round((row.confirmed / row.total) * 100)"
                  :stroke-width="8"
                  :show-text="true"
                  :format="(percentage: number) => `${percentage}%`"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 分类分布 -->
      <el-col :span="12">
        <el-card v-loading="loadingCategory">
          <template #header>
            <div class="card-header">
              <span>资产分类分布</span>
              <el-tag type="info">{{ categoryStats.length }} 个分类</el-tag>
            </div>
          </template>
          <el-table :data="categoryStats" stripe max-height="400">
            <el-table-column type="index" label="序号" width="70" align="center" />
            <el-table-column prop="category" label="分类名称" min-width="200" show-overflow-tooltip />
            <el-table-column prop="count" label="数量" width="120" align="right">
              <template #default="{ row }">
                <el-text type="primary" style="font-weight: 600">{{ row.count }}</el-text>
              </template>
            </el-table-column>
            <el-table-column label="占比" width="150" align="right">
              <template #default="{ row }">
                <el-progress
                  :percentage="Math.round((row.count / totalCategoryCount) * 100)"
                  :stroke-width="8"
                  :show-text="true"
                  :format="(percentage: number) => `${percentage}%`"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势数据弹窗 -->
    <el-dialog v-model="trendDialogVisible" title="趋势数据" width="600px">
      <el-table :data="trendData" stripe max-height="400">
        <el-table-column prop="month" label="月份" width="150" />
        <el-table-column prop="count" label="资产数量" align="right" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis,
  CircleCheck,
  Clock,
  TrendCharts
} from '@element-plus/icons-vue'
import {
  statisticsApi,
  type StatisticsOverview,
  type TrendItem,
  type OrganizationStats,
  type CategoryStats
} from '@/api/system'

// 数据状态
const loadingOrg = ref(false)
const loadingCategory = ref(false)
const trendDialogVisible = ref(false)

// 概览数据
const overview = reactive<StatisticsOverview>({
  total: 0,
  by_status: {},
  by_stage: {},
  monthly_new: 0,
  pending_approval: 0
})

// 趋势数据
const trendData = ref<TrendItem[]>([])

// 组织统计
const orgStats = ref<OrganizationStats[]>([])

// 分类统计
const categoryStats = ref<CategoryStats[]>([])

// 分类总数
const totalCategoryCount = computed(() => {
  return categoryStats.value.reduce((sum, item) => sum + item.count, 0)
})

// 获取概览数据
const fetchOverview = async () => {
  try {
    const { data } = await statisticsApi.getOverview()
    Object.assign(overview, data)
  } catch (error) {
    ElMessage.error('获取概览数据失败')
  }
}

// 获取趋势数据
const fetchTrend = async () => {
  try {
    const { data } = await statisticsApi.getTrend()
    trendData.value = data
  } catch (error) {
    ElMessage.error('获取趋势数据失败')
  }
}

// 获取组织统计
const fetchOrgStats = async () => {
  loadingOrg.value = true
  try {
    const { data } = await statisticsApi.getByOrganization()
    orgStats.value = data
  } catch (error) {
    ElMessage.error('获取组织统计失败')
  } finally {
    loadingOrg.value = false
  }
}

// 获取分类统计
const fetchCategoryStats = async () => {
  loadingCategory.value = true
  try {
    const { data } = await statisticsApi.getByCategory()
    categoryStats.value = data
  } catch (error) {
    ElMessage.error('获取分类统计失败')
  } finally {
    loadingCategory.value = false
  }
}

// 显示趋势数据
const showTrendData = () => {
  trendDialogVisible.value = true
}

onMounted(() => {
  fetchOverview()
  fetchTrend()
  fetchOrgStats()
  fetchCategoryStats()
})
</script>

<style scoped lang="scss">
.statistics-container {
  padding: 20px;
}

.stat-card {
  .stat-content {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .stat-icon {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    flex-shrink: 0;
  }

  .stat-info {
    flex: 1;
  }

  .stat-label {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 32px;
    font-weight: bold;
    color: #303133;
    line-height: 1;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.chart-placeholder {
  height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 8px;
  border: 2px dashed #dcdfe6;

  .placeholder-text {
    margin-top: 20px;
    font-size: 18px;
    font-weight: 600;
    color: #606266;
  }

  .placeholder-hint {
    margin-top: 10px;
    font-size: 14px;
    color: #909399;
    margin-bottom: 20px;
  }
}

:deep(.el-progress__text) {
  font-size: 12px !important;
  min-width: 40px;
}
</style>
