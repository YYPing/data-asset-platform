"""
统计分析路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.core.permissions import require_roles
from app.models.user import User
from app.services.statistics import StatisticsService
from app.schemas.statistics import (
    StatisticsResponse,
    OverviewStats,
    TrendStats,
    OrganizationStatsResponse,
    CategoryStatsResponse,
    AssessmentStats,
    WorkflowStats,
)

router = APIRouter(prefix="/statistics", tags=["statistics"])


def _get_organization_filter(current_user: User) -> Optional[int]:
    """
    根据用户角色获取组织过滤条件
    
    center_admin, center_user, auditor: 可查看全局统计，返回None
    holder: 只能查看本组织，返回organization_id
    """
    if current_user.role in ['center_admin', 'center_user', 'auditor']:
        return None
    elif current_user.role == 'holder':
        return current_user.organization_id
    else:
        raise HTTPException(status_code=403, detail="无权限访问统计数据")


@router.get("/overview", response_model=StatisticsResponse)
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取总览统计
    
    - 资产总数
    - 各状态数量
    - 各阶段数量
    - 本月新增
    - 待审批数
    """
    organization_id = _get_organization_filter(current_user)
    service = StatisticsService(db)
    data = await service.get_overview(organization_id)
    
    return StatisticsResponse(
        code=200,
        message="success",
        data=data.model_dump()
    )


@router.get("/trend", response_model=StatisticsResponse)
async def get_trend(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取趋势统计
    
    按月统计资产注册数量，最近12个月
    """
    organization_id = _get_organization_filter(current_user)
    service = StatisticsService(db)
    data = await service.get_trend(organization_id)
    
    return StatisticsResponse(
        code=200,
        message="success",
        data=data.model_dump()
    )


@router.get("/by-organization", response_model=StatisticsResponse)
async def get_by_organization(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    按组织统计
    
    - 各组织资产数量
    - 已确权数
    - 总估值
    """
    organization_id = _get_organization_filter(current_user)
    service = StatisticsService(db)
    data = await service.get_by_organization(organization_id)
    
    return StatisticsResponse(
        code=200,
        message="success",
        data=[item.model_dump() for item in data]
    )


@router.get("/by-category", response_model=StatisticsResponse)
async def get_by_category(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    按分类统计
    
    - 各分类资产数量
    - 占比
    """
    organization_id = _get_organization_filter(current_user)
    service = StatisticsService(db)
    data = await service.get_by_category(organization_id)
    
    return StatisticsResponse(
        code=200,
        message="success",
        data=[item.model_dump() for item in data]
    )


@router.get("/assessment", response_model=StatisticsResponse)
async def get_assessment_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    评估统计
    
    - 合规通过率
    - 平均评分
    - 风险分布
    """
    organization_id = _get_organization_filter(current_user)
    service = StatisticsService(db)
    data = await service.get_assessment_stats(organization_id)
    
    return StatisticsResponse(
        code=200,
        message="success",
        data=data.model_dump()
    )


@router.get("/workflow", response_model=StatisticsResponse)
async def get_workflow_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    审批统计
    
    - 平均审批时长
    - 通过率
    - 驳回率
    - 超时率
    """
    organization_id = _get_organization_filter(current_user)
    service = StatisticsService(db)
    data = await service.get_workflow_stats(organization_id)
    
    return StatisticsResponse(
        code=200,
        message="success",
        data=data.model_dump()
    )
