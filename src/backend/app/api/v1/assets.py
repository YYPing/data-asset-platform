"""
数据资产 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetListResponse,
    SearchParams,
    AssetSubmitResponse
)
from app.services.asset import AssetService

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])


def success_response(data, message: str = "success"):
    """统一成功响应格式"""
    return {
        "code": 200,
        "message": message,
        "data": data
    }


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: AssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建数据资产（草稿状态）
    
    - 自动生成资产编码（格式：DA-YYYYMMDD-XXXX）
    - 初始状态为 draft
    - 初始阶段为 registration
    """
    asset = await AssetService.create_asset(db, asset_data, current_user)
    return success_response(
        AssetResponse.model_validate(asset).model_dump(),
        message="Asset created successfully"
    )


@router.get("/", response_model=dict)
async def list_assets(
    q: Optional[str] = Query(None, description="搜索关键词"),
    status_filter: Optional[str] = Query(None, alias="status", description="状态筛选"),
    stage: Optional[str] = Query(None, description="阶段筛选"),
    org_id: Optional[int] = Query(None, description="组织ID筛选"),
    category: Optional[str] = Query(None, description="分类筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取资产列表
    
    - 支持分页
    - 支持关键词搜索（asset_code, asset_name, description, data_source）
    - 支持多维度筛选（状态、阶段、组织、分类）
    - holder角色自动过滤为本组织资产
    """
    params = SearchParams(
        q=q,
        status=status_filter,
        stage=stage,
        org_id=org_id,
        category=category,
        page=page,
        page_size=page_size
    )
    
    assets, total = await AssetService.list_assets(db, params, current_user)
    
    response_data = AssetListResponse(
        items=[AssetResponse.model_validate(asset) for asset in assets],
        total=total,
        page=page,
        page_size=page_size
    )
    
    return success_response(response_data.model_dump())


@router.get("/search", response_model=dict)
async def search_assets(
    q: str = Query(..., description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    全文搜索资产
    
    - 搜索范围：asset_code, asset_name, description, data_source
    - 自动应用组织权限过滤
    """
    assets, total = await AssetService.search_assets(
        db, q, current_user, page, page_size
    )
    
    response_data = AssetListResponse(
        items=[AssetResponse.model_validate(asset) for asset in assets],
        total=total,
        page=page,
        page_size=page_size
    )
    
    return success_response(response_data.model_dump())


@router.get("/{asset_id}", response_model=dict)
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取资产详情
    
    - holder角色只能查看本组织资产
    - 返回完整资产信息
    """
    asset = await AssetService.get_asset_by_id(db, asset_id, current_user)
    return success_response(
        AssetResponse.model_validate(asset).model_dump()
    )


@router.put("/{asset_id}", response_model=dict)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新资产
    
    - 仅 draft 和 correction 状态可编辑
    - holder角色只能编辑本组织资产
    - 支持部分字段更新
    """
    asset = await AssetService.update_asset(db, asset_id, asset_data, current_user)
    return success_response(
        AssetResponse.model_validate(asset).model_dump(),
        message="Asset updated successfully"
    )


@router.delete("/{asset_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除资产（软删除）
    
    - 仅 draft 状态可删除
    - holder角色只能删除本组织资产
    - 软删除：设置 deleted_at 时间戳
    """
    await AssetService.delete_asset(db, asset_id, current_user)
    return success_response(
        {"id": asset_id},
        message="Asset deleted successfully"
    )


@router.post("/{asset_id}/submit", response_model=dict)
async def submit_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交资产审批
    
    - 仅 draft 状态可提交
    - 提交后状态变更为 submitted
    - holder角色只能提交本组织资产
    """
    asset = await AssetService.submit_asset(db, asset_id, current_user)
    
    response_data = AssetSubmitResponse(
        id=asset.id,
        asset_code=asset.asset_code,
        status=asset.status,
        message="Asset submitted for review successfully"
    )
    
    return success_response(
        response_data.model_dump(),
        message="Asset submitted successfully"
    )
