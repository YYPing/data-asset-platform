import request from '@/api/request'

// ==================== 类型定义 ====================

export interface User {
  id: number
  username: string
  real_name: string
  email: string
  phone?: string
  role: string
  organization_id?: number
  organization_name?: string
  status: 'active' | 'inactive'
  created_at: string
  updated_at: string
}

export interface UserListParams {
  page?: number
  page_size?: number
  q?: string
  role?: string
  org_id?: number
}

export interface UserListResponse {
  items: User[]
  total: number
}

export interface CreateUserData {
  username: string
  real_name: string
  email: string
  phone?: string
  role: string
  organization_id?: number
  password: string
}

export interface UpdateUserData {
  real_name?: string
  email?: string
  phone?: string
  role?: string
  status?: 'active' | 'inactive'
}

export interface ResetPasswordResponse {
  new_password: string
}

// 审计日志
export interface AuditLog {
  id: number
  user_id: number
  username: string
  action: string
  resource_type: string
  resource_id?: string
  details?: string
  ip_address: string
  created_at: string
}

export interface AuditLogParams {
  page?: number
  page_size?: number
  action?: string
  resource_type?: string
  date_from?: string
  date_to?: string
}

export interface AuditLogResponse {
  items: AuditLog[]
  total: number
}

export interface AuditStats {
  by_action: Array<{ action: string; count: number }>
  by_day: Array<{ date: string; count: number }>
}

// 通知
export interface Notification {
  id: number
  title: string
  content: string
  type: string
  is_read: boolean
  related_url?: string
  created_at: string
}

export interface NotificationParams {
  page?: number
  page_size?: number
  type?: string
  is_read?: boolean
}

export interface NotificationResponse {
  items: Notification[]
  total: number
}

export interface UnreadCountResponse {
  count: number
}

// 统计
export interface StatisticsOverview {
  total: number
  by_status: Record<string, number>
  by_stage: Record<string, number>
  monthly_new: number
  pending_approval: number
}

export interface TrendItem {
  month: string
  count: number
}

export interface OrganizationStats {
  org_name: string
  total: number
  confirmed: number
  total_value: number
}

export interface CategoryStats {
  category: string
  count: number
}

// ==================== 用户管理 API ====================

export const userApi = {
  // 获取用户列表
  getUsers(params: UserListParams = {}) {
    return request.get<UserListResponse>('/api/v1/users/', { params })
  },

  // 创建用户
  createUser(data: CreateUserData) {
    return request.post<User>('/api/v1/users/', data)
  },

  // 更新用户
  updateUser(id: number, data: UpdateUserData) {
    return request.put<User>(`/api/v1/users/${id}`, data)
  },

  // 删除用户
  deleteUser(id: number) {
    return request.delete(`/api/v1/users/${id}`)
  },

  // 重置密码
  resetPassword(id: number) {
    return request.put<ResetPasswordResponse>(`/api/v1/users/${id}/reset-password`)
  }
}

// ==================== 审计日志 API ====================

export const auditApi = {
  // 获取审计日志列表
  getLogs(params: AuditLogParams = {}) {
    return request.get<AuditLogResponse>('/api/v1/audit/logs', { params })
  },

  // 获取统计数据
  getStats() {
    return request.get<AuditStats>('/api/v1/audit/stats')
  },

  // 导出日志
  exportLogs(params: { date_from?: string; date_to?: string } = {}) {
    return request.get('/api/v1/audit/export', {
      params,
      responseType: 'blob'
    })
  }
}

// ==================== 通知中心 API ====================

export const notificationApi = {
  // 获取通知列表
  getNotifications(params: NotificationParams = {}) {
    return request.get<NotificationResponse>('/api/v1/notifications/', { params })
  },

  // 获取未读数量
  getUnreadCount() {
    return request.get<UnreadCountResponse>('/api/v1/notifications/unread-count')
  },

  // 标记单条已读
  markAsRead(id: number) {
    return request.put(`/api/v1/notifications/${id}/read`)
  },

  // 全部标记已读
  markAllAsRead() {
    return request.put('/api/v1/notifications/read-all')
  }
}

// ==================== 统计分析 API ====================

export const statisticsApi = {
  // 获取概览数据
  getOverview() {
    return request.get<StatisticsOverview>('/api/v1/statistics/overview')
  },

  // 获取趋势数据
  getTrend() {
    return request.get<TrendItem[]>('/api/v1/statistics/trend')
  },

  // 按组织统计
  getByOrganization() {
    return request.get<OrganizationStats[]>('/api/v1/statistics/by-organization')
  },

  // 按分类统计
  getByCategory() {
    return request.get<CategoryStats[]>('/api/v1/statistics/by-category')
  }
}
