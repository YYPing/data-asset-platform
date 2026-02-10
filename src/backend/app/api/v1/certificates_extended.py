"""
证书管理API - 扩展版
完整的证书管理API端点
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException, Path as PathParam
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import math

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.certificate import (
    CertificateCreate, CertificateUpdate, CertificateResponse,
    CertificateDetailResponse, CertificateListResponse,
    CertificateImportResponse, CertificateVerifyResponse,
    CertificateAssociateRequest, CertificateRenewalRequest,
    CertificateQueryParams, ApiResponse, CertificateStatistics
)
from app.services.certificate_extended import CertificateExtendedService


router = APIRouter(prefix="/api/v1/certificates", tags=["证书管理（扩展版）"])


# ==================== 证书CRUD ====================

@router.post("", response_model=ApiResponse, summary="创建证书记录")
async def create_certificate(
    cert_data: CertificateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    创建证书记录（不上传文件）
    
    - **certificate_no**: 证书编号（必填，唯一）
    - **certificate_type**: 证书类型
    - **issuing_authority**: 颁发机构（必填）
    - **issue_date**: 颁发日期（必填）
    - **expiry_date**: 有效期（可选）
    - **holder_name**: 持有人姓名（可选）
    - **notes**: 备注（可选）
    """
    service = CertificateExtendedService(db)
    certificate = await service.create_certificate(cert_data, current_user["id"])
    response_data = service.enrich_certificate_response(certificate)
    
    return ApiResponse(
        code=200,
        message="证书创建成功",
        data=response_data
    )


@router.get("", response_model=ApiResponse, summary="证书列表（分页、筛选）")
async def list_certificates(
    certificate_no: Optional[str] = Query(None, description="证书编号（模糊查询）"),
    certificate_type: Optional[str] = Query(None, description="证书类型"),
    status: Optional[str] = Query(None, description="状态"),
    issuing_authority: Optional[str] = Query(None, description="颁发机构（模糊查询）"),
    holder_name: Optional[str] = Query(None, description="持有人姓名（模糊查询）"),
    issue_date_start: Optional[date] = Query(None, description="颁发日期开始"),
    issue_date_end: Optional[date] = Query(None, description="颁发日期结束"),
    expiry_date_start: Optional[date] = Query(None, description="有效期开始"),
    expiry_date_end: Optional[date] = Query(None, description="有效期结束"),
    days_until_expiry_max: Optional[int] = Query(None, description="距离过期最大天数", ge=0),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: str = Query("created_at", description="排序字段"),
    order_desc: bool = Query(True, description="是否降序"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    查询证书列表，支持多条件筛选和分页
    
    **筛选条件：**
    - 证书编号、类型、状态
    - 颁发机构、持有人姓名（模糊查询）
    - 颁发日期范围、有效期范围
    - 距离过期天数（用于查询即将过期的证书）
    
    **排序：**
    - 支持按任意字段排序
    - 默认按创建时间降序
    """
    service = CertificateExtendedService(db)
    
    query_params = CertificateQueryParams(
        certificate_no=certificate_no,
        certificate_type=certificate_type,
        status=status,
        issuing_authority=issuing_authority,
        holder_name=holder_name,
        issue_date_start=issue_date_start,
        issue_date_end=issue_date_end,
        expiry_date_start=expiry_date_start,
        expiry_date_end=expiry_date_end,
        days_until_expiry_max=days_until_expiry_max,
        page=page,
        page_size=page_size,
        order_by=order_by,
        order_desc=order_desc,
    )
    
    certificates, total = await service.list_certificates(query_params)
    
    items = [service.enrich_certificate_response(cert) for cert in certificates]
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    response_data = {
        "total": total,
        "items": items,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
    
    return ApiResponse(
        code=200,
        message="查询成功",
        data=response_data
    )


@router.get("/{certificate_id}", response_model=ApiResponse, summary="证书详情")
async def get_certificate(
    certificate_id: int = PathParam(..., description="证书ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取证书详细信息
    
    包含：
    - 证书基本信息
    - 关联的文件列表
    - 关联的资产列表
    - 验证历史
    - 到期提醒记录
    """
    service = CertificateExtendedService(db)
    certificate = await service.get_certificate_by_id(certificate_id)
    
    if not certificate:
        raise HTTPException(status_code=404, detail="证书不存在")
    
    response_data = service.enrich_certificate_response(certificate)
    
    return ApiResponse(
        code=200,
        message="查询成功",
        data=response_data
    )


@router.put("/{certificate_id}", response_model=ApiResponse, summary="更新证书信息")
async def update_certificate(
    certificate_id: int = PathParam(..., description="证书ID"),
    update_data: CertificateUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    更新证书信息
    
    可更新字段：
    - 证书编号、类型、名称
    - 颁发机构、颁发日期、有效期
    - 持有人信息
    - 状态、备注
    - 防伪信息（数字签名、验证码、二维码）
    
    **注意：** 更新有效期时会自动重新计算证书状态
    """
    service = CertificateExtendedService(db)
    certificate = await service.update_certificate(certificate_id, update_data)
    response_data = service.enrich_certificate_response(certificate)
    
    return ApiResponse(
        code=200,
        message="更新成功",
        data=response_data
    )


@router.delete("/{certificate_id}", response_model=ApiResponse, summary="删除证书（软删除）")
async def delete_certificate(
    certificate_id: int = PathParam(..., description="证书ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    删除证书（软删除）
    
    **注意：**
    - 这是软删除操作，证书状态会被标记为 'revoked'（已撤销）
    - 文件和记录仍保留在系统中，不会真正删除
    - 软删除的证书不会出现在常规查询中
    """
    service = CertificateExtendedService(db)
    certificate = await service.delete_certificate(certificate_id)
    response_data = service.enrich_certificate_response(certificate)
    
    return ApiResponse(
        code=200,
        message="证书已撤销",
        data=response_data
    )


# ==================== 证书导入 ====================

@router.post("/import", response_model=ApiResponse, summary="导入证书文件（自动解析）")
async def import_certificate(
    file: UploadFile = File(..., description="证书文件（PDF/JPG/PNG/Excel）"),
    auto_parse: bool = Form(True, description="是否自动解析证书内容"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    导入证书文件并自动解析内容
    
    **支持的文件格式：**
    - PDF：提取文本内容
    - 图片（JPG/PNG）：OCR识别文本
    - Excel：批量导入（暂不支持，请使用批量导入接口）
    
    **自动解析内容：**
    - 证书编号
    - 持有人姓名
    - 颁发机构
    - 颁发日期
    - 有效期
    - 身份证号/组织机构代码
    
    **系统会自动：**
    - 计算文件SHA256哈希值用于防篡改
    - 上传文件到MinIO存储
    - 生成缩略图（PDF和图片）
    - 根据有效期自动设置证书状态
    """
    service = CertificateExtendedService(db)
    certificate, parsed_info = await service.import_certificate_with_parsing(
        file=file,
        user_id=current_user["id"],
        auto_parse=auto_parse
    )
    
    response_data = {
        "success": True,
        "certificate_id": certificate.id,
        "certificate": service.enrich_certificate_response(certificate),
        "message": "证书导入成功",
        "parsed_info": parsed_info,
    }
    
    return ApiResponse(
        code=200,
        message="证书导入成功",
        data=response_data
    )


# ==================== 证书验证 ====================

@router.post("/{certificate_id}/verify", response_model=ApiResponse, summary="验证证书有效性")
async def verify_certificate(
    certificate_id: int = PathParam(..., description="证书ID"),
    method: str = Query("comprehensive", description="验证方法（hash/signature/comprehensive）"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    验证证书有效性（防伪验证）
    
    **验证方法：**
    - **hash**: 文件哈希验证（检测文件是否被篡改）
    - **signature**: 数字签名验证
    - **comprehensive**: 综合验证（推荐）
    
    **综合验证包括：**
    1. 证书编号格式验证
    2. 有效期逻辑验证
    3. 文件完整性验证（哈希对比）
    4. 数字签名验证（如果有）
    5. 二维码验证（如果有）
    6. 防伪验证码验证（如果有）
    
    **验证结果：**
    - 验证通过/失败
    - 详细的验证信息
    - 错误和警告列表
    - 验证历史会被记录到数据库
    """
    service = CertificateExtendedService(db)
    validation_result = await service.verify_certificate(
        cert_id=certificate_id,
        user_id=current_user["id"],
        method=method
    )
    
    return ApiResponse(
        code=200,
        message="验证完成",
        data=validation_result
    )


# ==================== 证书预览和下载 ====================

@router.get("/{certificate_id}/preview", summary="证书预览")
async def preview_certificate(
    certificate_id: int = PathParam(..., description="证书ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取证书预览（缩略图）
    
    返回证书的缩略图URL，用于快速预览
    """
    # TODO: 实现预览功能
    raise HTTPException(status_code=501, detail="预览功能开发中")


@router.get("/{certificate_id}/download", summary="下载证书文件")
async def download_certificate(
    certificate_id: int = PathParam(..., description="证书ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    下载证书原始文件
    
    返回证书文件的下载链接或文件流
    """
    # TODO: 实现下载功能
    raise HTTPException(status_code=501, detail="下载功能开发中")


# ==================== 证书续期 ====================

@router.post("/{certificate_id}/renew", response_model=ApiResponse, summary="续期证书")
async def renew_certificate(
    certificate_id: int = PathParam(..., description="证书ID"),
    renewal_data: CertificateRenewalRequest = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    续期证书
    
    - **new_expiry_date**: 新的有效期（必填）
    - **renewal_notes**: 续期说明（可选）
    
    **系统会自动：**
    - 验证新有效期的合法性
    - 更新证书状态
    - 记录续期历史到备注中
    """
    service = CertificateExtendedService(db)
    certificate = await service.renew_certificate(
        cert_id=certificate_id,
        new_expiry_date=renewal_data.new_expiry_date,
        notes=renewal_data.renewal_notes
    )
    
    response_data = service.enrich_certificate_response(certificate)
    
    return ApiResponse(
        code=200,
        message="续期成功",
        data=response_data
    )


# ==================== 即将过期证书 ====================

@router.get("/expiring/list", response_model=ApiResponse, summary="即将过期证书列表")
async def get_expiring_certificates(
    days: int = Query(30, ge=1, le=365, description="提前天数（默认30天）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    查询即将过期的证书列表
    
    - **days**: 提前天数，查询未来N天内到期的证书（默认30天）
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    
    **返回：**
    - 按有效期升序排列的证书列表
    - 包含距离过期天数、提醒级别等信息
    - 用于到期提醒功能
    """
    service = CertificateExtendedService(db)
    certificates, total = await service.get_expiring_certificates(days, page, page_size)
    
    items = [service.enrich_certificate_response(cert) for cert in certificates]
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    response_data = {
        "total": total,
        "items": items,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
    
    return ApiResponse(
        code=200,
        message="查询成功",
        data=response_data
    )


# ==================== 证书关联管理 ====================

@router.post("/{certificate_id}/associate", response_model=ApiResponse, summary="关联证书到资产")
async def associate_certificate_to_asset(
    certificate_id: int = PathParam(..., description="证书ID"),
    request_data: CertificateAssociateRequest = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    关联证书到资产
    
    - **asset_id**: 资产ID（必填）
    - **notes**: 关联备注（可选）
    
    **注意：**
    - 一个证书可以关联多个资产
    - 同一证书和资产只能有一条有效关联
    - 系统会验证证书和资产是否存在
    """
    service = CertificateExtendedService(db)
    association = await service.associate_asset(
        cert_id=certificate_id,
        asset_id=request_data.asset_id,
        user_id=current_user["id"],
        notes=request_data.notes
    )
    
    return ApiResponse(
        code=200,
        message="关联成功",
        data={
            "id": association.id,
            "certificate_id": association.certificate_id,
            "asset_id": association.asset_id,
            "is_active": association.is_active,
            "associated_at": association.associated_at,
        }
    )


@router.post("/{certificate_id}/disassociate", response_model=ApiResponse, summary="解除证书与资产的关联")
async def disassociate_certificate_from_asset(
    certificate_id: int = PathParam(..., description="证书ID"),
    asset_id: int = Query(..., description="资产ID"),
    notes: Optional[str] = Query(None, description="解除关联备注"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    解除证书与资产的关联
    
    - **asset_id**: 资产ID（必填）
    - **notes**: 解除关联备注（可选）
    
    **注意：**
    - 这是软删除操作，关联记录会被标记为无效
    - 历史记录仍保留在系统中
    """
    service = CertificateExtendedService(db)
    association = await service.disassociate_asset(
        cert_id=certificate_id,
        asset_id=asset_id,
        user_id=current_user["id"],
        notes=notes
    )
    
    return ApiResponse(
        code=200,
        message="解除关联成功",
        data={
            "id": association.id,
            "certificate_id": association.certificate_id,
            "asset_id": association.asset_id,
            "is_active": association.is_active,
            "disassociated_at": association.disassociated_at,
        }
    )


@router.get("/{certificate_id}/assets", response_model=ApiResponse, summary="获取证书关联的资产列表")
async def get_certificate_assets(
    certificate_id: int = PathParam(..., description="证书ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取证书关联的所有资产
    
    返回该证书当前有效关联的所有资产列表
    """
    service = CertificateExtendedService(db)
    assets = await service.get_associated_assets(certificate_id)
    
    assets_data = [
        {
            "id": asset.id,
            "asset_code": asset.asset_code,
            "asset_name": asset.asset_name,
            "organization_id": asset.organization_id,
            "status": asset.status,
            "current_stage": asset.current_stage,
        }
        for asset in assets
    ]
    
    return ApiResponse(
        code=200,
        message="查询成功",
        data={
            "total": len(assets_data),
            "items": assets_data,
        }
    )
