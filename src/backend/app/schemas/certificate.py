"""
登记证书管理 - Pydantic Schema
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CertificateBase(BaseModel):
    """证书基础模型"""
    certificate_no: str = Field(..., description="证书编号")
    issuing_authority: str = Field(..., description="颁发机构")
    issue_date: date = Field(..., description="颁发日期")
    expiry_date: Optional[date] = Field(None, description="有效期")
    notes: Optional[str] = Field(None, description="备注")


class CertificateImport(CertificateBase):
    """证书导入请求"""
    asset_id: int = Field(..., description="资产ID")


class CertificateUpdate(BaseModel):
    """证书更新请求"""
    certificate_no: Optional[str] = Field(None, description="证书编号")
    issuing_authority: Optional[str] = Field(None, description="颁发机构")
    issue_date: Optional[date] = Field(None, description="颁发日期")
    expiry_date: Optional[date] = Field(None, description="有效期")
    notes: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, description="状态: valid/expiring/expired/revoked")


class CertificateResponse(CertificateBase):
    """证书响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    asset_id: int
    file_path: str = Field(..., description="文件路径")
    file_hash: str = Field(..., description="SHA256哈希值")
    status: str = Field(..., description="状态")
    imported_by: int = Field(..., description="导入人ID")
    imported_at: datetime = Field(..., description="导入时间")
    days_until_expiry: Optional[int] = Field(None, description="距离过期天数")


class CertificateVerifyResponse(BaseModel):
    """证书验证响应"""
    is_valid: bool = Field(..., description="是否有效")
    stored_hash: str = Field(..., description="存储的哈希值")
    current_hash: Optional[str] = Field(None, description="当前文件哈希值")
    message: str = Field(..., description="验证消息")


class CertificateListResponse(BaseModel):
    """证书列表响应"""
    total: int = Field(..., description="总数")
    items: list[CertificateResponse] = Field(..., description="证书列表")
    page: int = Field(1, description="当前页")
    page_size: int = Field(20, description="每页数量")


class ApiResponse(BaseModel):
    """统一API响应格式"""
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="消息")
    data: Optional[dict | list | CertificateResponse | CertificateListResponse | CertificateVerifyResponse] = None
