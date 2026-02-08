"""
审计日志路由
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.core.permissions import require_roles
from app.models.user import User
from app.schemas.audit import (
    AuditLogResponse,
    AuditLogListQuery,
    AuditLogListResponse,
    AuditStatsResponse,
)
from app.services.audit import AuditService


router = APIRouter(prefix="/audit", tags=["审计日志"])


def _can_view_all_logs(user: User) -> bool:
    """判断用户是否可以查看所有日志"""
    return user.role in ["auditor", "sys_admin"]


@router.get("/logs", response_model=dict)
async def get_audit_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    action: Optional[str] = Query(None, description="操作类型筛选"),
    resource_type: Optional[str] = Query(None, description="资源类型筛选"),
    date_from: Optional[datetime] = Query(None, description="开始日期"),
    date_to: Optional[datetime] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取审计日志列表（分页+筛选）
    
    权限：auditor和sys_admin可查看所有，其他角色只能看自己的
    """
    query_params = AuditLogListQuery(
        page=page,
        page_size=page_size,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        date_from=date_from,
        date_to=date_to,
    )
    
    # 权限控制
    filter_user_id = None if _can_view_all_logs(current_user) else current_user.id
    
    result = await AuditService.get_logs(
        db=db,
        query_params=query_params,
        current_user_id=filter_user_id,
    )
    
    return {
        "code": 200,
        "message": "success",
        "data": result.model_dump(),
    }


@router.get("/logs/{log_id}", response_model=dict)
async def get_audit_log_detail(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取审计日志详情
    
    权限：auditor和sys_admin可查看所有，其他角色只能看自己的
    """
    # 权限控制
    filter_user_id = None if _can_view_all_logs(current_user) else current_user.id
    
    log = await AuditService.get_log_by_id(
        db=db,
        log_id=log_id,
        user_id=filter_user_id,
    )
    
    if not log:
        raise HTTPException(status_code=404, detail="审计日志不存在")
    
    return {
        "code": 200,
        "message": "success",
        "data": log.model_dump(),
    }


@router.get("/stats", response_model=dict)
async def get_audit_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取审计统计
    
    包括：
    - 总日志数
    - 按操作类型统计
    - 按天统计趋势（最近30天）
    
    权限：auditor和sys_admin可查看所有，其他角色只能看自己的
    """
    # 权限控制
    filter_user_id = None if _can_view_all_logs(current_user) else current_user.id
    
    stats = await AuditService.get_stats(
        db=db,
        current_user_id=filter_user_id,
    )
    
    return {
        "code": 200,
        "message": "success",
        "data": stats.model_dump(),
    }


@router.get("/export")
async def export_audit_logs(
    page: int = Query(1, ge=1, description="页码（导出时忽略）"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量（导出时忽略）"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    action: Optional[str] = Query(None, description="操作类型筛选"),
    resource_type: Optional[str] = Query(None, description="资源类型筛选"),
    date_from: Optional[datetime] = Query(None, description="开始日期"),
    date_to: Optional[datetime] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    导出审计日志（CSV格式）
    
    权限：auditor和sys_admin可导出所有，其他角色只能导出自己的
    """
    query_params = AuditLogListQuery(
        page=1,  # 导出时不分页
        page_size=999999,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        date_from=date_from,
        date_to=date_to,
    )
    
    # 权限控制
    filter_user_id = None if _can_view_all_logs(current_user) else current_user.id
    
    # 生成CSV流
    csv_generator = AuditService.export_logs_csv(
        db=db,
        query_params=query_params,
        current_user_id=filter_user_id,
    )
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"audit_logs_{timestamp}.csv"
    
    return StreamingResponse(
        csv_generator,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )
