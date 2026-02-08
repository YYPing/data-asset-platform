import request from '@/api/request'

// ==================== 类型定义 ====================

export interface WorkflowNode {
  id: string
  name: string
  status: 'pending' | 'processing' | 'approved' | 'rejected'
  assigned_to: string
  comment?: string
}

export interface WorkflowStatus {
  current_node: string
  nodes: WorkflowNode[]
  progress_percent: number
}

export interface PendingWorkflowItem {
  node_id: string
  asset_id: string
  asset_name: string
  node_name: string
  role: string
  deadline: string
  started_at: string
}

export interface WorkflowHistory {
  action: string
  node_name: string
  operator_name: string
  comment: string
  operated_at: string
}

export interface AssessmentRecord {
  id: string
  asset_id: string
  assessment_type: 'compliance' | 'valuation'
  score: number
  risk_level?: 'high' | 'medium' | 'low'
  method?: string
  result_summary: string
  status: string
  created_at: string
  updated_at: string
}

export interface PendingAssessment {
  id: string
  asset_id: string
  asset_name: string
  assessment_type: 'compliance' | 'valuation'
  status: string
}

export interface ComplianceAssessmentData {
  score: number
  risk_level: 'high' | 'medium' | 'low'
  result_summary: string
}

export interface ValuationAssessmentData {
  method: string
  score: number
  result_summary: string
}

// ==================== 工作流API ====================

/**
 * 启动工作流
 */
export function startWorkflow(assetId: string) {
  return request<{ workflow_id: string; status: string }>({
    url: `/api/v1/workflow/start/${assetId}`,
    method: 'post'
  })
}

/**
 * 获取工作流状态
 */
export function getWorkflowStatus(assetId: string) {
  return request<WorkflowStatus>({
    url: `/api/v1/workflow/${assetId}/status`,
    method: 'get'
  })
}

/**
 * 审批通过
 */
export function approveWorkflow(nodeId: string, comment: string) {
  return request<{ success: boolean }>({
    url: `/api/v1/workflow/approve/${nodeId}`,
    method: 'post',
    data: { comment }
  })
}

/**
 * 审批驳回
 */
export function rejectWorkflow(nodeId: string, comment: string, rejectToNode?: string) {
  return request<{ success: boolean }>({
    url: `/api/v1/workflow/reject/${nodeId}`,
    method: 'post',
    data: {
      comment,
      reject_to_node: rejectToNode
    }
  })
}

/**
 * 获取待办列表
 */
export function getPendingWorkflows() {
  return request<{ items: PendingWorkflowItem[]; total: number }>({
    url: '/api/v1/workflow/pending',
    method: 'get'
  })
}

/**
 * 获取审批历史
 */
export function getWorkflowHistory(assetId: string) {
  return request<WorkflowHistory[]>({
    url: `/api/v1/workflow/history/${assetId}`,
    method: 'get'
  })
}

// ==================== 评估API ====================

/**
 * 提交合规评估
 */
export function submitComplianceAssessment(assetId: string, data: ComplianceAssessmentData) {
  return request<AssessmentRecord>({
    url: `/api/v1/assessment/compliance/${assetId}`,
    method: 'post',
    data
  })
}

/**
 * 提交价值评估
 */
export function submitValuationAssessment(assetId: string, data: ValuationAssessmentData) {
  return request<AssessmentRecord>({
    url: `/api/v1/assessment/valuation/${assetId}`,
    method: 'post',
    data
  })
}

/**
 * 获取资产评估记录
 */
export function getAssessmentRecords(assetId: string) {
  return request<AssessmentRecord[]>({
    url: `/api/v1/assessment/${assetId}`,
    method: 'get'
  })
}

/**
 * 获取待评估列表
 */
export function getPendingAssessments() {
  return request<PendingAssessment[]>({
    url: '/api/v1/assessment/pending',
    method: 'get'
  })
}

/**
 * 完成评估
 */
export function completeAssessment(id: string) {
  return request<{ success: boolean }>({
    url: `/api/v1/assessment/${id}/complete`,
    method: 'post'
  })
}
