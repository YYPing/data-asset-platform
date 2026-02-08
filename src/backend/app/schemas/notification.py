"""
通知 Pydantic 模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class NotificationType(str, Enum):
    """通知类型枚举"""
    SYSTEM = "system"
    WORKFLOW = "workflow"
    ASSET = "asset"
    CERTIFICATE = "certificate"


class NotificationBase(BaseModel):
    """通知基础模型"""
    title: str = Field(..., max_length=200, description="通知标题")
    content: str = Field(..., description="通知内容")
    notification_type: NotificationType = Field(..., description="通知类型")
    related_type: Optional[str] = Field(None, max_length=50, description="关联资源类型")
    related_id: Optional[str] = Field(None, max_length=100, description="关联资源ID")


class NotificationCreate(NotificationBase):
    """创建通知"""
    user_id: int = Field(..., description="接收用户ID")


class NotificationResponse(NotificationBase):
    """通知响应"""
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True


class NotificationListQuery(BaseModel):
    """通知列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    notification_type: Optional[NotificationType] = Field(None, description="通知类型筛选")
    is_read: Optional[bool] = Field(None, description="已读状态筛选")


class NotificationListResponse(BaseModel):
    """通知列表响应"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页数量")
    items: list[NotificationResponse] = Field(..., description="通知列表")


class UnreadCountResponse(BaseModel):
    """未读数量响应"""
    unread_count: int = Field(..., description="未读通知数量")


class NotificationSendRequest(BaseModel):
    """发送通知请求（内部服务调用）"""
    user_id: int = Field(..., description="接收用户ID")
    title: str = Field(..., max_length=200, description="通知标题")
    content: str = Field(..., description="通知内容")
    notification_type: NotificationType = Field(NotificationType.SYSTEM, description="通知类型")
    related_type: Optional[str] = Field(None, max_length=50, description="关联资源类型")
    related_id: Optional[str] = Field(None, max_length=100, description="关联资源ID")


class NotificationBroadcastRequest(BaseModel):
    """群发通知请求（按角色）"""
    role: str = Field(..., description="目标角色")
    title: str = Field(..., max_length=200, description="通知标题")
    content: str = Field(..., description="通知内容")
    notification_type: NotificationType = Field(NotificationType.SYSTEM, description="通知类型")
