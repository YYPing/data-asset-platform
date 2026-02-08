"""
通知路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.notification import (
    NotificationResponse,
    NotificationListQuery,
    NotificationListResponse,
    UnreadCountResponse,
    NotificationType,
)
from app.services.notification import NotificationService


router = APIRouter(prefix="/notifications", tags=["通知"])


@router.get("/", response_model=dict)
async def get_my_notifications(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    notification_type: Optional[NotificationType] = Query(None, description="通知类型筛选"),
    is_read: Optional[bool] = Query(None, description="已读状态筛选"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取我的通知列表（分页+筛选）
    """
    query_params = NotificationListQuery(
        page=page,
        page_size=page_size,
        notification_type=notification_type,
        is_read=is_read,
    )
    
    result = await NotificationService.get_user_notifications(
        db=db,
        user_id=current_user.id,
        query_params=query_params,
    )
    
    return {
        "code": 200,
        "message": "success",
        "data": result.model_dump(),
    }


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取未读通知数量
    """
    count = await NotificationService.get_unread_count(
        db=db,
        user_id=current_user.id,
    )
    
    return {
        "code": 200,
        "message": "success",
        "data": {"unread_count": count},
    }


@router.put("/{notification_id}/read", response_model=dict)
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    标记通知为已读
    """
    success = await NotificationService.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="通知不存在")
    
    return {
        "code": 200,
        "message": "标记成功",
        "data": None,
    }


@router.put("/read-all", response_model=dict)
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    标记所有通知为已读
    """
    count = await NotificationService.mark_all_as_read(
        db=db,
        user_id=current_user.id,
    )
    
    return {
        "code": 200,
        "message": f"已标记 {count} 条通知为已读",
        "data": {"count": count},
    }


@router.delete("/{notification_id}", response_model=dict)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除通知
    """
    success = await NotificationService.delete_notification(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="通知不存在")
    
    return {
        "code": 200,
        "message": "删除成功",
        "data": None,
    }


@router.get("/{notification_id}", response_model=dict)
async def get_notification_detail(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取通知详情
    """
    notification = await NotificationService.get_notification_by_id(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
    )
    
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")
    
    return {
        "code": 200,
        "message": "success",
        "data": notification.model_dump(),
    }
