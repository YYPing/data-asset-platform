"""
登记证书管理 - FastAPI路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.certificate import (
    CertificateImport,
    CertificateUpdate,
    CertificateResponse,
    CertificateVerifyResponse,
    CertificateListResponse,
    ApiResponse
)
from app.services.certificate import CertificateService


router = APIRouter(prefix="", tags=["证书管理"])


@router.post("/import", response_model=ApiResponse, summary="导入证书")
async def import_certificate(
    file: UploadFile = File(..., description="证书文件（PDF/JPG/PNG）"),
    asset_id: int = Form(..., description="资产ID"),
    certificate_no: str = Form(..., description="证书编号"),
    issuing_authority: str = Form(..., description="颁发机构"),
    issue_date: date = Form(..., description="颁发日期 (YYYY-MM-DD)"),
    expiry_date: Optional[date] = Form(None, description="有效期 (YYYY-MM-DD)"),
    notes: Optional[str] = Form(None, description="备注"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    导入登记证书
    
    - **file**: 证书文件，支持PDF、JPG、PNG格式
    - **asset_id**: 关联的数据资产ID
    - **certificate_no**: 证书编号
    - **issuing_authority**: 颁发机构
    - **issue_date**: 颁发日期
    - **expiry_date**: 有效期（可选）
    - **notes**: 备注信息（可选）
    
    系统会自动：
    - 计算文件SHA256哈希值用于防篡改
    - 上传文件到MinIO存储
    - 根据有效期自动设置证书状态
    """
    service = CertificateService(db)
    
    cert_data = CertificateImport(
        asset_id=asset_id,
        certificate_no=certificate_no,
        issuing_authority=issuing_authority,
        issue_date=issue_date,
        expiry_date=expiry_date,
        notes=notes
    )
    
    certificate = await service.import_certificate(
        file=file,
        cert_data=cert_data,
        user_id=current_user["id"]
    )
    
    response_data = service.enrich_certificate_response(certificate)
    
    return ApiResponse(
        code=200,
        message="证书导入成功",
        data=response_data
    )


@router.get("/{asset_id}", response_model=ApiResponse, summary="查询资产的所有证书")
async def get_certificates_by_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    查询指定资产的所有证书记录
    
    - **asset_id**: 资产ID
    
    返回该资产的所有有效证书（不包括已撤销的证书），按导入时间倒序排列
    """
    service = CertificateService(db)
    certificates = await service.get_certificates_by_asset(asset_id)
    
    response_data = [
        service.enrich_certificate_response(cert)
        for cert in certificates
    ]
    
    return ApiResponse(
        code=200,
        message="查询成功",
        data=response_data
    )


@router.get("/{id}/verify", response_model=ApiResponse, summary="验证证书完整性")
async def verify_certificate(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    验证证书文件完整性（防篡改校验）
    
    - **id**: 证书ID
    
    通过对比存储的SHA256哈希值与当前文件的哈希值，检测证书是否被篡改
    """
    service = CertificateService(db)
    verify_result = await service.verify_certificate(id)
    
    return ApiResponse(
        code=200,
        message="验证完成",
        data=verify_result
    )


@router.put("/{id}", response_model=ApiResponse, summary="更新证书信息")
async def update_certificate(
    id: int,
    update_data: CertificateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    更新证书信息
    
    - **id**: 证书ID
    - **update_data**: 更新的字段（仅更新提供的字段）
    
    可更新：证书编号、颁发机构、颁发日期、有效期、备注、状态
    
    注意：更新有效期时会自动重新计算证书状态
    """
    service = CertificateService(db)
    certificate = await service.update_certificate(id, update_data)
    
    response_data = service.enrich_certificate_response(certificate)
    
    return ApiResponse(
        code=200,
        message="更新成功",
        data=response_data
    )


@router.get("/expiring", response_model=ApiResponse, summary="即将过期证书列表")
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
    
    返回按有效期升序排列的证书列表，用于提醒功能
    """
    service = CertificateService(db)
    certificates, total = await service.get_expiring_certificates(days, page, page_size)
    
    items = [
        service.enrich_certificate_response(cert)
        for cert in certificates
    ]
    
    response_data = {
        "total": total,
        "items": items,
        "page": page,
        "page_size": page_size
    }
    
    return ApiResponse(
        code=200,
        message="查询成功",
        data=response_data
    )


@router.delete("/{id}", response_model=ApiResponse, summary="删除证书")
async def delete_certificate(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    删除证书（软删除）
    
    - **id**: 证书ID
    
    注意：这是软删除操作，证书状态会被标记为 'revoked'（已撤销），
    但文件和记录仍保留在系统中，不会真正删除
    """
    service = CertificateService(db)
    certificate = await service.delete_certificate(id)
    
    response_data = service.enrich_certificate_response(certificate)
    
    return ApiResponse(
        code=200,
        message="证书已撤销",
        data=response_data
    )
