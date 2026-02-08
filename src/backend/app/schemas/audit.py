"""
审计日志 Pydantic 模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AuditLogBase(BaseModel):
    """审计日志基础模型"""
    action: str = Field(..., description="操作类型")
    resource_type: Optional[str] = Field(None, description="资源类型")
    resource_id: Optional[str] = Field(None, description="资源ID")
    detail: Optional[str] = Field(None, description="操作详情")


class AuditLogCreate(AuditLogBase):
    """创建审计日志"""
    user_id: int = Field(..., description="用户ID")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")


class AuditLogResponse(AuditLogBase):
    """审计日志响应"""
    id: int
    user_id: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    
    # 关联用户信息
    username: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        from_attributes = True


class AuditLogListQuery(BaseModel):
    """审计日志列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    user_id: Optional[int] = Field(None, description="用户ID筛选")
    action: Optional[str] = Field(None, description="操作类型筛选")
    resource_type: Optional[str] = Field(None, description="资源类型筛选")
    date_from: Optional[datetime] = Field(None, description="开始日期")
    date_to: Optional[datetime] = Field(None, description="结束日期")


class AuditLogListResponse(BaseModel):
    """审计日志列表响应"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页数量")
    items: list[AuditLogResponse] = Field(..., description="日志列表")


class AuditStatsActionItem(BaseModel):
    """按操作类型统计项"""
    action: str = Field(..., description="操作类型")
    count: int = Field(..., description="数量")


class AuditStatsTrendItem(BaseModel):
    """按天统计趋势项"""
    date: str = Field(..., description="日期 YYYY-MM-DD")
    count: int = Field(..., description="数量")


class AuditStatsResponse(BaseModel):
    """审计统计响应"""
    total_count: int = Field(..., description="总日志数")
    action_stats: list[AuditStatsActionItem] = Field(..., description="按操作类型统计")
    trend_stats: list[AuditStatsTrendItem] = Field(..., description="按天统计趋势（最近30天）")
