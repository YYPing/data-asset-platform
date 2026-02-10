"""
数据资产 API 路由
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status, Request
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
    AssetSubmitResponse,
    AssetVersionCreate,
    AssetVersionResponse,
    AssetVersionListResponse,
    AssetSearchRequest,
    AssetSearchResponse,
    AssetApproveRequest,
    AssetRejectRequest,
    AssetRegisterRequest,
    AssetCancelRequest,
    AssetStatusTransitionResponse
)
from app.services.asset import AssetService
from app.utils.audit import AuditLogger

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
    request: Request,
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
    
    # 记录审计日志
    await AuditLogger.log_asset_create(
        db=db,
        user_id=current_user.id,
        asset_id=asset.id,
        asset_code=asset.asset_code,
        request=request
    )
    
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
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新资产
    
    - 仅 draft 和 correction 状态可编辑
    - holder角色只能编辑本组织资产
    - 支持部分字段更新
    """
    # 获取更新前的资产信息
    old_asset = await AssetService.get_asset_by_id(db, asset_id, current_user)
    
    # 更新资产
    asset = await AssetService.update_asset(db, asset_id, asset_data, current_user)
    
    # 记录审计日志
    changes = asset_data.model_dump(exclude_unset=True)
    await AuditLogger.log_asset_update(
        db=db,
        user_id=current_user.id,
        asset_id=asset.id,
        asset_code=asset.asset_code,
        changes=changes,
        request=request
    )
    
    return success_response(
        AssetResponse.model_validate(asset).model_dump(),
        message="Asset updated successfully"
    )


@router.delete("/{asset_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_asset(
    asset_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除资产（软删除）
    
    - 仅 draft 状态可删除
    - holder角色只能删除本组织资产
    - 软删除：设置 deleted_at 时间戳
    """
    # 获取资产信息
    asset = await AssetService.get_asset_by_id(db, asset_id, current_user)
    asset_code = asset.asset_code
    
    # 删除资产
    await AssetService.delete_asset(db, asset_id, current_user)
    
    # 记录审计日志
    await AuditLogger.log_asset_delete(
        db=db,
        user_id=current_user.id,
        asset_id=asset_id,
        asset_code=asset_code,
        request=request
    )
    
    return success_response(
        {"id": asset_id},
        message="Asset deleted successfully"
    )


@router.post("/{asset_id}/submit", response_model=dict)
async def submit_asset(
    asset_id: int,
    request: Request,
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
    
    # 记录审计日志
    await AuditLogger.log_asset_submit(
        db=db,
        user_id=current_user.id,
        asset_id=asset.id,
        asset_code=asset.asset_code,
        request=request
    )
    
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


# ==================== 版本控制相关端点 ====================

@router.post("/{asset_id}/versions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_asset_version(
    asset_id: int,
    version_data: AssetVersionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建资产新版本
    
    - 复制当前资产为新版本
    - 保留历史版本
    - 版本号自动递增
    """
    new_version = await AssetService.create_version(
        db=db,
        asset_id=asset_id,
        current_user=current_user,
        comment=version_data.comment,
        request=request
    )
    
    return success_response(
        AssetVersionResponse.model_validate(new_version).model_dump(),
        message="Asset version created successfully"
    )


@router.get("/{asset_id}/versions", response_model=dict)
async def get_asset_versions(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取资产版本历史
    
    - 返回该资产的所有版本
    - 按版本号降序排列
    """
    versions = await AssetService.get_version_history(db, asset_id, current_user)
    
    response_data = AssetVersionListResponse(
        items=[AssetVersionResponse.model_validate(v) for v in versions],
        total=len(versions)
    )
    
    return success_response(response_data.model_dump())


@router.post("/{asset_id}/versions/{version_id}/rollback", response_model=dict)
async def rollback_asset_version(
    asset_id: int,
    version_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    回滚到指定版本
    
    - 创建新版本，内容复制自目标版本
    - 不删除任何历史版本
    """
    new_version = await AssetService.rollback_to_version(
        db=db,
        asset_id=asset_id,
        target_version_id=version_id,
        current_user=current_user,
        request=request
    )
    
    return success_response(
        AssetVersionResponse.model_validate(new_version).model_dump(),
        message="Asset rolled back successfully"
    )


# ==================== 状态流转相关端点 ====================

@router.post("/{asset_id}/approve", response_model=dict)
async def approve_asset(
    asset_id: int,
    approve_data: AssetApproveRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    审核通过资产
    
    - 仅 submitted 状态可审核
    - 状态变更为 approved
    - 需要审核员或管理员权限
    """
    old_status = "submitted"
    asset = await AssetService.approve_asset(
        db=db,
        asset_id=asset_id,
        current_user=current_user,
        comment=approve_data.comment,
        request=request
    )
    
    response_data = AssetStatusTransitionResponse(
        id=asset.id,
        asset_code=asset.asset_code,
        old_status=old_status,
        new_status=asset.status,
        message="Asset approved successfully",
        timestamp=datetime.utcnow()
    )
    
    return success_response(
        response_data.model_dump(),
        message="Asset approved successfully"
    )


@router.post("/{asset_id}/reject", response_model=dict)
async def reject_asset(
    asset_id: int,
    reject_data: AssetRejectRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    审核驳回资产
    
    - 仅 submitted 状态可驳回
    - 状态变更为 rejected
    - 需要审核员或管理员权限
    - 必须提供驳回原因
    """
    old_status = "submitted"
    asset = await AssetService.reject_asset(
        db=db,
        asset_id=asset_id,
        current_user=current_user,
        reason=reject_data.reason,
        request=request
    )
    
    response_data = AssetStatusTransitionResponse(
        id=asset.id,
        asset_code=asset.asset_code,
        old_status=old_status,
        new_status=asset.status,
        message=f"Asset rejected: {reject_data.reason}",
        timestamp=datetime.utcnow()
    )
    
    return success_response(
        response_data.model_dump(),
        message="Asset rejected"
    )


@router.post("/{asset_id}/register", response_model=dict)
async def register_asset(
    asset_id: int,
    register_data: AssetRegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    完成资产登记
    
    - 仅 approved 状态可登记
    - 状态变更为 registered
    - 需要管理员权限
    """
    old_status = "approved"
    asset = await AssetService.register_asset(
        db=db,
        asset_id=asset_id,
        current_user=current_user,
        comment=register_data.comment,
        request=request
    )
    
    response_data = AssetStatusTransitionResponse(
        id=asset.id,
        asset_code=asset.asset_code,
        old_status=old_status,
        new_status=asset.status,
        message="Asset registered successfully",
        timestamp=datetime.utcnow()
    )
    
    return success_response(
        response_data.model_dump(),
        message="Asset registered successfully"
    )


@router.post("/{asset_id}/cancel", response_model=dict)
async def cancel_asset(
    asset_id: int,
    cancel_data: AssetCancelRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    注销资产
    
    - 仅 registered 状态可注销
    - 状态变更为 cancelled
    - 需要管理员权限
    - 必须提供注销原因
    """
    old_status = "registered"
    asset = await AssetService.cancel_asset(
        db=db,
        asset_id=asset_id,
        current_user=current_user,
        reason=cancel_data.reason,
        request=request
    )
    
    response_data = AssetStatusTransitionResponse(
        id=asset.id,
        asset_code=asset.asset_code,
        old_status=old_status,
        new_status=asset.status,
        message=f"Asset cancelled: {cancel_data.reason}",
        timestamp=datetime.utcnow()
    )
    
    return success_response(
        response_data.model_dump(),
        message="Asset cancelled"
    )


# ==================== 高级搜索端点 ====================

@router.post("/search/advanced", response_model=dict)
async def advanced_search_assets(
    search_params: AssetSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    高级搜索资产
    
    - 支持中文分词全文搜索（使用zhparser）
    - 支持多维度筛选（状态、阶段、分类、敏感级别等）
    - 支持日期范围筛选
    - 自动应用组织权限过滤
    """
    start_time = datetime.utcnow()
    
    assets, total = await AssetService.advanced_search(
        db=db,
        search_params=search_params,
        current_user=current_user
    )
    
    end_time = datetime.utcnow()
    search_time_ms = (end_time - start_time).total_seconds() * 1000
    
    response_data = AssetSearchResponse(
        items=[AssetResponse.model_validate(asset) for asset in assets],
        total=total,
        page=search_params.page,
        page_size=search_params.page_size,
        search_time_ms=round(search_time_ms, 2)
    )
    
    return success_response(response_data.model_dump())
