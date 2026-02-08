"""
Workflow API Schemas
数据资产管理平台 - 工作流审批相关的Pydantic模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ==================== Request Models ====================

class ApproveRequest(BaseModel):
    """审批通过请求"""
    comment: Optional[str] = Field(None, description="审批意见（可选）")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "comment": "资产信息完整，同意通过"
        }
    })


class RejectRequest(BaseModel):
    """驳回请求"""
    comment: str = Field(..., description="驳回原因（必填）", min_length=1)
    reject_to_node: Optional[str] = Field(None, description="驳回到指定节点ID（可选，默认驳回到上一节点）")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "comment": "资产描述不够详细，请补充完善",
            "reject_to_node": "node_001"
        }
    })


class CorrectionRequest(BaseModel):
    """补正提交请求"""
    comment: Optional[str] = Field(None, description="补正说明")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "comment": "已补充完善资产描述和使用场景"
        }
    })


# ==================== Response Models ====================

class WorkflowNodeStatus(BaseModel):
    """工作流节点状态"""
    node_id: str = Field(..., description="节点ID")
    node_name: str = Field(..., description="节点名称")
    node_type: str = Field(..., description="节点类型（start/approval/end等）")
    status: str = Field(..., description="节点状态（pending/approved/rejected/skipped）")
    assignee_role: Optional[str] = Field(None, description="处理人角色")
    assignee_name: Optional[str] = Field(None, description="处理人姓名")
    start_time: Optional[datetime] = Field(None, description="节点开始时间")
    end_time: Optional[datetime] = Field(None, description="节点完成时间")
    comment: Optional[str] = Field(None, description="处理意见")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowStatus(BaseModel):
    """工作流状态"""
    workflow_id: str = Field(..., description="工作流实例ID")
    asset_id: str = Field(..., description="资产ID")
    asset_name: str = Field(..., description="资产名称")
    definition_name: str = Field(..., description="流程定义名称")
    status: str = Field(..., description="流程状态（running/completed/rejected/cancelled）")
    current_node_id: Optional[str] = Field(None, description="当前节点ID")
    current_node_name: Optional[str] = Field(None, description="当前节点名称")
    progress: float = Field(..., description="流程进度（0-100）", ge=0, le=100)
    start_time: datetime = Field(..., description="流程启动时间")
    end_time: Optional[datetime] = Field(None, description="流程结束时间")
    nodes: List[WorkflowNodeStatus] = Field(default_factory=list, description="所有节点状态")
    
    model_config = ConfigDict(from_attributes=True)


class PendingTask(BaseModel):
    """待办任务"""
    task_id: str = Field(..., description="任务ID（节点ID）")
    workflow_id: str = Field(..., description="工作流实例ID")
    asset_id: str = Field(..., description="资产ID")
    asset_name: str = Field(..., description="资产名称")
    node_name: str = Field(..., description="节点名称")
    node_type: str = Field(..., description="节点类型")
    submitter: str = Field(..., description="提交人")
    submit_time: datetime = Field(..., description="提交时间")
    waiting_time: int = Field(..., description="等待时长（秒）")
    priority: str = Field(default="normal", description="优先级（low/normal/high/urgent）")
    
    model_config = ConfigDict(from_attributes=True)


class ApprovalHistoryItem(BaseModel):
    """审批历史记录项"""
    record_id: str = Field(..., description="记录ID")
    node_id: str = Field(..., description="节点ID")
    node_name: str = Field(..., description="节点名称")
    action: str = Field(..., description="操作类型（submit/approve/reject/correct）")
    operator: str = Field(..., description="操作人")
    operator_role: str = Field(..., description="操作人角色")
    comment: Optional[str] = Field(None, description="操作意见")
    timestamp: datetime = Field(..., description="操作时间")
    duration: Optional[int] = Field(None, description="处理耗时（秒）")
    
    model_config = ConfigDict(from_attributes=True)


class ApprovalHistory(BaseModel):
    """审批历史（时间线）"""
    asset_id: str = Field(..., description="资产ID")
    asset_name: str = Field(..., description="资产名称")
    workflow_id: str = Field(..., description="工作流实例ID")
    total_duration: Optional[int] = Field(None, description="总耗时（秒）")
    records: List[ApprovalHistoryItem] = Field(default_factory=list, description="历史记录列表")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowDefinitionInfo(BaseModel):
    """工作流定义信息"""
    definition_id: str = Field(..., description="定义ID")
    name: str = Field(..., description="流程名称")
    description: Optional[str] = Field(None, description="流程描述")
    version: str = Field(..., description="版本号")
    status: str = Field(..., description="状态（active/inactive）")
    node_count: int = Field(..., description="节点数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Common Response Wrapper ====================

class ApiResponse(BaseModel):
    """统一API响应格式"""
    code: int = Field(default=200, description="响应码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "code": 200,
            "message": "success",
            "data": {}
        }
    })
