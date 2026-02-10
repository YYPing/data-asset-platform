/**
 * 资产相关工具函数
 */

import type {
  Asset,
  AssetStatus,
  AssetStage,
  AssetCategory,
  DataClassification,
  SensitivityLevel,
  AssetStatusTransition,
  AssetComparison
} from '@/types/asset'

// ==================== 标签映射 ====================

/**
 * 获取资产状态标签
 */
export function getAssetStatusLabel(status: AssetStatus | undefined): string {
  const map: Record<AssetStatus, string> = {
    draft: '草稿',
    pending: '待审批',
    approved: '已通过',
    rejected: '已拒绝',
    archived: '已归档'
  }
  return status ? map[status] || status : '-'
}

/**
 * 获取资产状态标签类型
 */
export function getAssetStatusType(status: AssetStatus | undefined): 'success' | 'warning' | 'danger' | 'info' | '' {
  const map: Record<AssetStatus, 'success' | 'warning' | 'danger' | 'info' | ''> = {
    draft: 'info',
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    archived: ''
  }
  return status ? map[status] || '' : ''
}

/**
 * 获取资产阶段标签
 */
export function getAssetStageLabel(stage: AssetStage | undefined): string {
  const map: Record<AssetStage, string> = {
    registration: '登记',
    inventory: '盘点',
    evaluation: '评估',
    cataloging: '入表'
  }
  return stage ? map[stage] || stage : '-'
}

/**
 * 获取资产阶段标签类型
 */
export function getAssetStageType(stage: AssetStage | undefined): 'success' | 'warning' | 'danger' | 'info' | '' {
  const map: Record<AssetStage, 'success' | 'warning' | 'danger' | 'info' | ''> = {
    registration: '',
    inventory: 'warning',
    evaluation: 'success',
    cataloging: 'info'
  }
  return stage ? map[stage] || '' : ''
}

/**
 * 获取资产分类标签
 */
export function getAssetCategoryLabel(category: AssetCategory | undefined): string {
  const map: Record<AssetCategory, string> = {
    business: '业务数据',
    technical: '技术数据',
    management: '管理数据'
  }
  return category ? map[category] || category : '-'
}

/**
 * 获取数据分级标签
 */
export function getDataClassificationLabel(classification: DataClassification | undefined): string {
  const map: Record<DataClassification, string> = {
    level1: '一级',
    level2: '二级',
    level3: '三级',
    level4: '四级'
  }
  return classification ? map[classification] || classification : '-'
}

/**
 * 获取敏感级别标签
 */
export function getSensitivityLevelLabel(level: SensitivityLevel | undefined): string {
  const map: Record<SensitivityLevel, string> = {
    public: '公开',
    internal: '内部',
    confidential: '机密',
    top_secret: '绝密'
  }
  return level ? map[level] || level : '-'
}

/**
 * 获取敏感级别标签类型
 */
export function getSensitivityLevelType(level: SensitivityLevel | undefined): 'success' | 'warning' | 'danger' | 'info' | '' {
  const map: Record<SensitivityLevel, 'success' | 'warning' | 'danger' | 'info' | ''> = {
    public: 'success',
    internal: 'info',
    confidential: 'warning',
    top_secret: 'danger'
  }
  return level ? map[level] || '' : ''
}

// ==================== 状态流转 ====================

/**
 * 获取可用的状态流转操作
 */
export function getAvailableTransitions(currentStatus: AssetStatus, userRole: string): AssetStatusTransition[] {
  const allTransitions: AssetStatusTransition[] = [
    {
      from: 'draft',
      to: 'pending',
      action: 'submit',
      label: '提交审批',
      icon: 'Upload',
      type: 'success',
      permission: 'asset:submit'
    },
    {
      from: 'pending',
      to: 'approved',
      action: 'approve',
      label: '通过',
      icon: 'Check',
      type: 'success',
      permission: 'asset:approve'
    },
    {
      from: 'pending',
      to: 'rejected',
      action: 'reject',
      label: '拒绝',
      icon: 'Close',
      type: 'danger',
      permission: 'asset:reject'
    },
    {
      from: 'rejected',
      to: 'draft',
      action: 'revise',
      label: '重新编辑',
      icon: 'Edit',
      type: 'primary',
      permission: 'asset:edit'
    },
    {
      from: 'approved',
      to: 'archived',
      action: 'archive',
      label: '归档',
      icon: 'FolderOpened',
      type: 'info',
      permission: 'asset:archive'
    }
  ]

  return allTransitions.filter(t => t.from === currentStatus)
}

/**
 * 检查是否可以编辑资产
 */
export function canEditAsset(asset: Asset, userRole: string): boolean {
  // 草稿状态可以编辑
  if (asset.status === 'draft') {
    return true
  }
  // 被拒绝的资产可以重新编辑
  if (asset.status === 'rejected') {
    return true
  }
  // 管理员可以编辑任何状态
  if (userRole === 'admin') {
    return true
  }
  return false
}

/**
 * 检查是否可以删除资产
 */
export function canDeleteAsset(asset: Asset, userRole: string): boolean {
  // 只有草稿状态可以删除
  if (asset.status === 'draft') {
    return true
  }
  // 管理员可以删除任何状态
  if (userRole === 'admin') {
    return true
  }
  return false
}

// ==================== 数据格式化 ====================

/**
 * 格式化日期时间
 */
export function formatDateTime(dateStr: string | undefined): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '-'
  
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
 * 格式化日期
 */
export function formatDate(dateStr: string | undefined): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '-'
  
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

/**
 * 格式化金额
 */
export function formatCurrency(value: number | undefined): string {
  if (value === undefined || value === null) return '-'
  return `¥${value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number | undefined): string {
  if (!bytes || bytes === 0) return '0 B'
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${units[i]}`
}

// ==================== 数据验证 ====================

/**
 * 验证资产名称
 */
export function validateAssetName(name: string): boolean {
  return name.length >= 2 && name.length <= 100
}

/**
 * 验证资产编号
 */
export function validateAssetCode(code: string): boolean {
  // 资产编号格式：字母开头，可包含字母、数字、下划线、连字符
  return /^[A-Z][A-Z0-9_-]{3,19}$/.test(code)
}

// ==================== 资产对比 ====================

/**
 * 对比两个资产版本的差异
 */
export function compareAssets(oldAsset: Partial<Asset>, newAsset: Partial<Asset>): AssetComparison[] {
  const fields: Array<{ key: keyof Asset; label: string }> = [
    { key: 'asset_name', label: '资产名称' },
    { key: 'category', label: '资产分类' },
    { key: 'data_classification', label: '数据分级' },
    { key: 'sensitivity_level', label: '敏感级别' },
    { key: 'description', label: '描述' },
    { key: 'data_source', label: '数据来源' },
    { key: 'data_volume', label: '数据量' },
    { key: 'data_format', label: '数据格式' },
    { key: 'update_frequency', label: '更新频率' },
    { key: 'asset_type', label: '资产类型' },
    { key: 'estimated_value', label: '估值' }
  ]

  return fields.map(({ key, label }) => ({
    field: key,
    label,
    old_value: oldAsset[key],
    new_value: newAsset[key],
    changed: oldAsset[key] !== newAsset[key]
  }))
}

/**
 * 获取变更字段数量
 */
export function getChangedFieldsCount(comparisons: AssetComparison[]): number {
  return comparisons.filter(c => c.changed).length
}

// ==================== 导出相关 ====================

/**
 * 生成导出文件名
 */
export function generateExportFileName(prefix: string = 'assets', format: string = 'xlsx'): string {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
  return `${prefix}_${timestamp}.${format}`
}

/**
 * 下载文件
 */
export function downloadFile(url: string, filename: string): void {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// ==================== 搜索和筛选 ====================

/**
 * 高亮搜索关键词
 */
export function highlightKeyword(text: string, keyword: string): string {
  if (!keyword) return text
  const regex = new RegExp(`(${keyword})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

/**
 * 构建查询字符串
 */
export function buildQueryString(params: Record<string, any>): string {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      query.append(key, String(value))
    }
  })
  return query.toString()
}
