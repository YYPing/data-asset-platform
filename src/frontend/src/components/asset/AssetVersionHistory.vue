<template>
  <div class="version-history-container">
    <el-timeline v-loading="loading">
      <el-timeline-item
        v-for="version in versions"
        :key="version.id"
        :timestamp="formatDateTime(version.created_at)"
        placement="top"
        :type="version.version === currentVersion ? 'primary' : 'info'"
      >
        <el-card shadow="hover">
          <template #header>
            <div class="version-header">
              <div class="version-info">
                <el-tag :type="version.version === currentVersion ? 'primary' : 'info'" size="small">
                  版本 {{ version.version }}
                </el-tag>
                <span class="version-creator">{{ version.created_by }}</span>
              </div>
              <div class="version-actions">
                <el-button
                  v-if="version.version !== currentVersion"
                  type="primary"
                  link
                  size="small"
                  @click="handleCompare(version)"
                >
                  对比差异
                </el-button>
                <el-button
                  v-if="canRevert && version.version !== currentVersion"
                  type="warning"
                  link
                  size="small"
                  @click="handleRevert(version)"
                >
                  恢复此版本
                </el-button>
              </div>
            </div>
          </template>

          <div class="version-content">
            <div v-if="version.changes" class="version-changes">
              <el-text type="info">变更说明：</el-text>
              <p>{{ version.changes }}</p>
            </div>

            <div v-if="expandedVersions.includes(version.id)" class="version-details">
              <el-divider />
              <el-descriptions :column="2" size="small" border>
                <el-descriptions-item
                  v-for="field in getChangedFields(version)"
                  :key="field.key"
                  :label="field.label"
                  :span="field.span || 1"
                >
                  {{ field.value }}
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <div class="version-footer">
              <el-button
                type="primary"
                link
                size="small"
                @click="toggleExpand(version.id)"
              >
                {{ expandedVersions.includes(version.id) ? '收起详情' : '查看详情' }}
              </el-button>
            </div>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>

    <el-empty v-if="!loading && versions.length === 0" description="暂无版本历史" />

    <!-- 版本对比对话框 -->
    <el-dialog
      v-model="compareDialogVisible"
      title="版本对比"
      width="800px"
      destroy-on-close
    >
      <div v-if="comparisonData" class="comparison-container">
        <div class="comparison-header">
          <div class="comparison-version">
            <el-tag type="info">版本 {{ comparisonData.oldVersion }}</el-tag>
          </div>
          <el-icon><Right /></el-icon>
          <div class="comparison-version">
            <el-tag type="primary">版本 {{ comparisonData.newVersion }}</el-tag>
          </div>
        </div>

        <el-table :data="comparisonData.differences" stripe>
          <el-table-column prop="label" label="字段" width="150" />
          <el-table-column label="旧值" min-width="200">
            <template #default="{ row }">
              <span :class="{ 'text-deleted': row.changed }">
                {{ row.old_value || '-' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="新值" min-width="200">
            <template #default="{ row }">
              <span :class="{ 'text-added': row.changed }">
                {{ row.new_value || '-' }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Right } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/asset-helper'
import { compareAssets } from '@/utils/asset-helper'
import type { AssetVersion, Asset, AssetComparison } from '@/types/asset'

interface Props {
  assetId: number
  currentVersion?: number
  canRevert?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  canRevert: false
})

const emit = defineEmits<{
  revert: [version: AssetVersion]
}>()

// ==================== 状态管理 ====================

const loading = ref(false)
const versions = ref<AssetVersion[]>([])
const expandedVersions = ref<number[]>([])
const compareDialogVisible = ref(false)
const comparisonData = ref<{
  oldVersion: number
  newVersion: number
  differences: AssetComparison[]
} | null>(null)

// ==================== 生命周期 ====================

onMounted(() => {
  loadVersionHistory()
})

// ==================== 数据加载 ====================

const loadVersionHistory = async () => {
  loading.value = true
  try {
    // TODO: 调用实际的API
    // const res = await getAssetVersionHistory(props.assetId)
    // versions.value = res.data
    
    // 模拟数据
    versions.value = [
      {
        id: 1,
        asset_id: props.assetId,
        version: 3,
        changes: '更新了资产估值和数据量信息',
        created_by: '张三',
        created_at: '2024-02-10 10:30:00',
        snapshot: {
          estimated_value: 500000,
          data_volume: '10TB'
        }
      },
      {
        id: 2,
        asset_id: props.assetId,
        version: 2,
        changes: '补充了数据来源和更新频率',
        created_by: '李四',
        created_at: '2024-02-09 15:20:00',
        snapshot: {
          data_source: '业务系统A',
          update_frequency: '每日'
        }
      },
      {
        id: 3,
        asset_id: props.assetId,
        version: 1,
        changes: '初始创建',
        created_by: '王五',
        created_at: '2024-02-08 09:00:00',
        snapshot: {}
      }
    ]
  } catch (error) {
    console.error('Failed to load version history:', error)
    ElMessage.error('加载版本历史失败')
  } finally {
    loading.value = false
  }
}

// ==================== 版本操作 ====================

const toggleExpand = (versionId: number) => {
  const index = expandedVersions.value.indexOf(versionId)
  if (index > -1) {
    expandedVersions.value.splice(index, 1)
  } else {
    expandedVersions.value.push(versionId)
  }
}

const getChangedFields = (version: AssetVersion) => {
  if (!version.snapshot) return []
  
  return Object.entries(version.snapshot).map(([key, value]) => ({
    key,
    label: getFieldLabel(key),
    value: formatFieldValue(key, value),
    span: isLongField(key) ? 2 : 1
  }))
}

const getFieldLabel = (key: string): string => {
  const labelMap: Record<string, string> = {
    asset_name: '资产名称',
    category: '资产分类',
    data_classification: '数据分级',
    sensitivity_level: '敏感级别',
    description: '描述',
    data_source: '数据来源',
    data_volume: '数据量',
    data_format: '数据格式',
    update_frequency: '更新频率',
    asset_type: '资产类型',
    estimated_value: '估值'
  }
  return labelMap[key] || key
}

const formatFieldValue = (key: string, value: any): string => {
  if (value === null || value === undefined) return '-'
  
  if (key === 'estimated_value') {
    return `¥${Number(value).toLocaleString()}`
  }
  
  return String(value)
}

const isLongField = (key: string): boolean => {
  return ['description'].includes(key)
}

const handleCompare = (version: AssetVersion) => {
  const currentVersionData = versions.value.find(v => v.version === props.currentVersion)
  if (!currentVersionData) {
    ElMessage.warning('无法获取当前版本数据')
    return
  }

  const differences = compareAssets(version.snapshot, currentVersionData.snapshot)
  
  comparisonData.value = {
    oldVersion: version.version,
    newVersion: props.currentVersion || 0,
    differences: differences.filter(d => d.changed)
  }
  
  compareDialogVisible.value = true
}

const handleRevert = async (version: AssetVersion) => {
  try {
    await ElMessageBox.confirm(
      `确定要恢复到版本 ${version.version} 吗？这将创建一个新版本。`,
      '恢复版本',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    emit('revert', version)
  } catch (error) {
    // 用户取消
  }
}
</script>

<style scoped lang="scss">
.version-history-container {
  padding: 20px;

  .version-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .version-info {
      display: flex;
      align-items: center;
      gap: 12px;

      .version-creator {
        color: var(--el-text-color-secondary);
        font-size: 14px;
      }
    }

    .version-actions {
      display: flex;
      gap: 8px;
    }
  }

  .version-content {
    .version-changes {
      margin-bottom: 12px;

      p {
        margin: 8px 0 0 0;
        color: var(--el-text-color-regular);
      }
    }

    .version-details {
      margin-top: 12px;
    }

    .version-footer {
      margin-top: 12px;
      text-align: right;
    }
  }

  .comparison-container {
    .comparison-header {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 20px;
      margin-bottom: 20px;
      padding: 16px;
      background-color: var(--el-fill-color-light);
      border-radius: 4px;

      .comparison-version {
        font-size: 16px;
        font-weight: 500;
      }
    }

    .text-deleted {
      color: var(--el-color-danger);
      text-decoration: line-through;
    }

    .text-added {
      color: var(--el-color-success);
      font-weight: 500;
    }
  }
}
</style>
