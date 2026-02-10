"""
材料管理 API 路由 - 增强版
包含完整的材料CRUD、文件上传（分片上传）、哈希验证、版本管理和审核流程
"""
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.material import (
    MaterialCreate, MaterialUpdate, MaterialResponse, MaterialListResponse,
    MaterialQuery, MaterialUploadRequest, MaterialUploadResponse,
    ChunkUploadRequest, ChunkUploadResponse,
    CompleteUploadRequest, CompleteUploadResponse,
    MaterialHashRequest, MaterialHashResponse,
    MaterialVerifyRequest, MaterialVerifyResponse,
    MaterialVersionCreate, MaterialVersionResponse, MaterialVersionListResponse,
    MaterialSubmitRequest, MaterialApproveRequest, MaterialRejectRequest,
    MaterialReviewResponse, MaterialDownloadResponse
)
from app.services.material_enhanced import material_service

router = APIRouter(prefix="", tags=["materials"])


# ==================== CRUD 操作 ====================

@router.get("", response_model=MaterialListResponse)
async def list_materials(
    page: int = 1,
    page_size: int = 20,
    asset_id: Optional[int] = None,
    stage: Optional[str] = None,
    status: Optional[str] = None,
    material_type: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取材料列表（分页、筛选）
    
    - **page**: 页码（从1开始）
    - **page_size**: 每页记录数（1-100）
    - **asset_id**: 资产ID筛选（可选）
    - **stage**: 阶段筛选（可选）
    - **status**: 状态筛选（可选）
    - **material_type**: 材料类型筛选（可选）
    - **keyword**: 搜索关键词（材料名称，可选）
    """
    query = MaterialQuery(
        page=page,
        page_size=page_size,
        asset_id=asset_id,
        stage=stage,
        status=status,
        material_type=material_type,
        keyword=keyword
    )
    
    materials, total = await material_service.list_materials(db, query)
    
    return MaterialListResponse(
        total=total,
        items=[MaterialResponse.model_validate(m) for m in materials],
        page=query.page,
        page_size=query.page_size
    )


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取材料详情
    
    - **material_id**: 材料ID
    """
    material = await material_service.get_material(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="材料不存在")
    
    return MaterialResponse.model_validate(material)


@router.post("", response_model=MaterialResponse, status_code=201)
async def create_material(
    material_data: MaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    创建材料记录
    
    - **asset_id**: 关联资产ID
    - **material_name**: 材料名称
    - **material_type**: 材料类型（可选）
    - **stage**: 所属阶段
    - **file_path**: 文件路径（可选）
    - **file_size**: 文件大小（字节，可选）
    - **file_format**: 文件格式（可选）
    - **file_hash**: 文件哈希（SHA-256）
    - **is_required**: 是否必需（默认false）
    """
    material = await material_service.create_material(
        db=db,
        material_data=material_data,
        user_id=current_user["id"]
    )
    
    return MaterialResponse.model_validate(material)


@router.put("/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: int,
    material_data: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    更新材料信息
    
    - **material_id**: 材料ID
    - **material_name**: 材料名称（可选）
    - **material_type**: 材料类型（可选）
    - **stage**: 所属阶段（可选）
    - **is_required**: 是否必需（可选）
    - **status**: 状态（可选）
    """
    material = await material_service.update_material(
        db=db,
        material_id=material_id,
        material_data=material_data
    )
    
    return MaterialResponse.model_validate(material)


@router.delete("/{material_id}", status_code=204)
async def delete_material(
    material_id: int,
    soft_delete: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    删除材料（软删除或硬删除）
    
    - **material_id**: 材料ID
    - **soft_delete**: 是否软删除（默认true，软删除只更新状态为archived）
    """
    await material_service.delete_material(
        db=db,
        material_id=material_id,
        soft_delete=soft_delete
    )
    
    return None


# ==================== 文件上传（分片上传、断点续传）====================

@router.post("/upload", response_model=MaterialUploadResponse, status_code=201)
async def initiate_upload(
    upload_request: MaterialUploadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    初始化文件上传（创建上传会话）
    
    - **asset_id**: 关联资产ID
    - **material_name**: 材料名称
    - **material_type**: 材料类型（可选）
    - **stage**: 所属阶段
    - **is_required**: 是否必需（默认false）
    - **file_name**: 文件名
    - **file_size**: 文件大小（字节，最大1GB）
    
    返回上传会话信息，包括会话ID、分片数量等
    """
    return await material_service.initiate_upload(
        db=db,
        upload_request=upload_request,
        user_id=current_user["id"]
    )


@router.post("/{session_id}/upload-chunk", response_model=ChunkUploadResponse)
async def upload_chunk(
    session_id: str,
    chunk_index: int = Form(..., description="分片索引（从0开始）"),
    chunk_data: UploadFile = File(..., description="分片数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    上传文件分片
    
    - **session_id**: 上传会话ID（从 initiate_upload 获取）
    - **chunk_index**: 分片索引（从0开始）
    - **chunk_data**: 分片数据（文件）
    
    返回上传进度信息
    """
    # 读取分片数据
    data = await chunk_data.read()
    
    return await material_service.upload_chunk(
        session_id=session_id,
        chunk_index=chunk_index,
        chunk_data=data
    )


@router.post("/{session_id}/complete-upload", response_model=CompleteUploadResponse)
async def complete_upload(
    session_id: str,
    material_name: str = Form(..., description="材料名称"),
    material_type: Optional[str] = Form(None, description="材料类型"),
    stage: str = Form(..., description="所属阶段"),
    is_required: bool = Form(False, description="是否必需"),
    verify_hash: Optional[str] = Form(None, description="验证哈希值（可选）"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    完成文件上传（合并分片并创建材料记录）
    
    - **session_id**: 上传会话ID
    - **material_name**: 材料名称
    - **material_type**: 材料类型（可选）
    - **stage**: 所属阶段
    - **is_required**: 是否必需（默认false）
    - **verify_hash**: 验证哈希值（可选，用于验证文件完整性）
    
    返回创建的材料信息
    """
    return await material_service.complete_upload(
        db=db,
        session_id=session_id,
        material_name=material_name,
        material_type=material_type,
        stage=stage,
        is_required=is_required,
        user_id=current_user["id"],
        verify_hash=verify_hash
    )


@router.delete("/{session_id}/cancel-upload", status_code=204)
async def cancel_upload(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    取消文件上传
    
    - **session_id**: 上传会话ID
    
    删除所有临时分片文件
    """
    await material_service.cancel_upload(session_id)
    return None


# ==================== 文件下载 ====================

@router.get("/{material_id}/download", response_model=MaterialDownloadResponse)
async def download_material(
    material_id: int,
    expires_in: int = 3600,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    生成材料下载URL（预签名URL）
    
    - **material_id**: 材料ID
    - **expires_in**: URL有效期（秒，默认3600即1小时）
    
    返回预签名下载URL
    """
    return await material_service.download_material(
        db=db,
        material_id=material_id,
        expires_in=expires_in
    )


# ==================== 哈希计算和验证 ====================

@router.get("/{material_id}/hash", response_model=MaterialHashResponse)
async def get_material_hash(
    material_id: int,
    algorithm: str = "sha256",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取材料哈希值
    
    - **material_id**: 材料ID
    - **algorithm**: 哈希算法（sha256/md5/sha1，默认sha256）
    
    返回文件哈希值
    """
    return await material_service.get_material_hash(
        db=db,
        material_id=material_id,
        algorithm=algorithm
    )


@router.post("/{material_id}/verify", response_model=MaterialVerifyResponse)
async def verify_material(
    material_id: int,
    verify_request: MaterialVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    验证材料完整性
    
    - **material_id**: 材料ID
    - **expected_hash**: 期望的哈希值
    - **algorithm**: 哈希算法（sha256/md5/sha1，默认sha256）
    
    返回验证结果
    """
    return await material_service.verify_material(
        db=db,
        material_id=material_id,
        expected_hash=verify_request.expected_hash,
        algorithm=verify_request.algorithm
    )


# ==================== 版本管理 ====================

@router.post("/{material_id}/versions", response_model=MaterialResponse, status_code=201)
async def create_version(
    material_id: int,
    version_data: MaterialVersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    创建材料新版本
    
    - **material_id**: 材料ID
    - **file_hash**: 新版本文件哈希（SHA-256）
    - **file_path**: 新版本文件路径（可选）
    - **file_size**: 新版本文件大小（可选）
    - **change_description**: 变更说明（可选）
    
    返回新版本材料信息
    """
    material = await material_service.create_version(
        db=db,
        material_id=material_id,
        version_data=version_data,
        user_id=current_user["id"]
    )
    
    return MaterialResponse.model_validate(material)


@router.get("/{material_id}/versions", response_model=MaterialVersionListResponse)
async def get_version_history(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取材料版本历史
    
    - **material_id**: 材料ID
    
    返回所有版本列表
    """
    return await material_service.get_version_history(
        db=db,
        material_id=material_id
    )


# ==================== 审核流程 ====================

@router.post("/{material_id}/submit", response_model=MaterialReviewResponse)
async def submit_for_review(
    material_id: int,
    submit_request: MaterialSubmitRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    提交材料审核
    
    - **material_id**: 材料ID
    - **comment**: 提交说明（可选）
    
    将材料提交审核
    """
    return await material_service.submit_for_review(
        db=db,
        material_id=material_id,
        comment=submit_request.comment
    )


@router.post("/{material_id}/approve", response_model=MaterialReviewResponse)
async def approve_material(
    material_id: int,
    approve_request: MaterialApproveRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    审核通过材料
    
    - **material_id**: 材料ID
    - **comment**: 审核意见（可选）
    
    审核通过材料
    """
    return await material_service.approve_material(
        db=db,
        material_id=material_id,
        reviewer_id=current_user["id"],
        comment=approve_request.comment
    )


@router.post("/{material_id}/reject", response_model=MaterialReviewResponse)
async def reject_material(
    material_id: int,
    reject_request: MaterialRejectRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    审核驳回材料
    
    - **material_id**: 材料ID
    - **comment**: 驳回原因（必填）
    
    审核驳回材料
    """
    return await material_service.reject_material(
        db=db,
        material_id=material_id,
        reviewer_id=current_user["id"],
        comment=reject_request.comment
    )
