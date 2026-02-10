"""
登记证书管理 - Pydantic Schema（扩展版）
"""
from datetime import date, datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum


# ==================== 枚举类型 ====================

class CertificateTypeEnum(str, Enum):
    """证书类型枚举"""
    REGISTRATION = "registration"  # 数据资产登记证书
    COMPLIANCE = "compliance"  # 合规评估证书
    VALUE_ASSESSMENT = "value_assessment"  # 价值评估证书
    OWNERSHIP = "ownership"  # 权属确认证书
    QUALITY = "quality"  # 质量认证证书


class CertificateStatusEnum(str, Enum):
    """证书状态枚举"""
    VALID = "valid"  # 有效
    EXPIRING = "expiring"  # 即将过期
    EXPIRED = "expired"  # 已过期
    REVOKED = "revoked"  # 已撤销
    PENDING = "pending"  # 待审核


class FileFormatEnum(str, Enum):
    """文件格式枚举"""
    PDF = "pdf"
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    EXCEL = "excel"


class AlertTypeEnum(str, Enum):
    """提醒类型枚举"""
    DAYS_30 = "days_30"  # 提前30天
    DAYS_7 = "days_7"  # 提前7天
    DAYS_1 = "days_1"  # 提前1天
    EXPIRED = "expired"  # 已过期


class AlertMethodEnum(str, Enum):
    """提醒方式枚举"""
    EMAIL = "email"  # 邮件
    SMS = "sms"  # 短信
    INTERNAL = "internal"  # 站内信


# ==================== 基础模型 ====================

class CertificateBase(BaseModel):
    """证书基础模型"""
    certificate_no: str = Field(..., description="证书编号", min_length=6, max_length=100)
    certificate_type: CertificateTypeEnum = Field(
        default=CertificateTypeEnum.REGISTRATION,
        description="证书类型"
    )
    certificate_name: Optional[str] = Field(None, description="证书名称", max_length=200)
    issuing_authority: str = Field(..., description="颁发机构", max_length=200)
    issue_date: date = Field(..., description="颁发日期")
    expiry_date: Optional[date] = Field(None, description="有效期")
    holder_name: Optional[str] = Field(None, description="持有人姓名", max_length=200)
    holder_id_number: Optional[str] = Field(None, description="持有人身份证号/组织机构代码", max_length=100)
    notes: Optional[str] = Field(None, description="备注")
    
    @field_validator('expiry_date')
    @classmethod
    def validate_expiry_date(cls, v, info):
        """验证有效期不能早于颁发日期"""
        if v and 'issue_date' in info.data:
            issue_date = info.data['issue_date']
            if v < issue_date:
                raise ValueError('有效期不能早于颁发日期')
        return v


# ==================== 请求模型 ====================

class CertificateCreate(CertificateBase):
    """证书创建请求"""
    digital_signature: Optional[str] = Field(None, description="数字签名")
    verification_code: Optional[str] = Field(None, description="防伪验证码")
    qr_code_data: Optional[str] = Field(None, description="二维码数据")


class CertificateUpdate(BaseModel):
    """证书更新请求"""
    certificate_no: Optional[str] = Field(None, description="证书编号", min_length=6, max_length=100)
    certificate_type: Optional[CertificateTypeEnum] = Field(None, description="证书类型")
    certificate_name: Optional[str] = Field(None, description="证书名称", max_length=200)
    issuing_authority: Optional[str] = Field(None, description="颁发机构", max_length=200)
    issue_date: Optional[date] = Field(None, description="颁发日期")
    expiry_date: Optional[date] = Field(None, description="有效期")
    holder_name: Optional[str] = Field(None, description="持有人姓名", max_length=200)
    holder_id_number: Optional[str] = Field(None, description="持有人身份证号/组织机构代码", max_length=100)
    status: Optional[CertificateStatusEnum] = Field(None, description="状态")
    notes: Optional[str] = Field(None, description="备注")
    digital_signature: Optional[str] = Field(None, description="数字签名")
    verification_code: Optional[str] = Field(None, description="防伪验证码")
    qr_code_data: Optional[str] = Field(None, description="二维码数据")


class CertificateImportRequest(CertificateBase):
    """证书导入请求（单个文件）"""
    pass


class CertificateBatchImportRequest(BaseModel):
    """证书批量导入请求（Excel）"""
    auto_create: bool = Field(default=True, description="是否自动创建证书记录")
    skip_errors: bool = Field(default=False, description="是否跳过错误行")


class CertificateAssociateRequest(BaseModel):
    """证书关联资产请求"""
    asset_id: int = Field(..., description="资产ID", gt=0)
    notes: Optional[str] = Field(None, description="关联备注")


class CertificateDisassociateRequest(BaseModel):
    """证书解除关联请求"""
    asset_id: int = Field(..., description="资产ID", gt=0)
    notes: Optional[str] = Field(None, description="解除关联备注")


class CertificateRenewalRequest(BaseModel):
    """证书续期请求"""
    new_expiry_date: date = Field(..., description="新的有效期")
    renewal_notes: Optional[str] = Field(None, description="续期说明")


class CertificateVerifyRequest(BaseModel):
    """证书验证请求"""
    verification_method: str = Field(
        default="hash",
        description="验证方法（hash/signature/qrcode/comprehensive）"
    )


# ==================== 响应模型 ====================

class CertificateFileResponse(BaseModel):
    """证书文件响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    certificate_id: int
    file_name: str
    file_path: str
    file_size: int
    file_format: str
    file_hash: str
    mime_type: str
    thumbnail_path: Optional[str] = None
    is_primary: bool
    uploaded_by: Optional[int] = None
    created_at: datetime


class CertificateAssetResponse(BaseModel):
    """证书资产关联响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    certificate_id: int
    asset_id: int
    is_active: bool
    associated_by: Optional[int] = None
    associated_at: datetime
    disassociated_by: Optional[int] = None
    disassociated_at: Optional[datetime] = None
    notes: Optional[str] = None


class CertificateValidationResponse(BaseModel):
    """证书验证记录响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    certificate_id: int
    validation_status: str
    validation_method: str
    is_valid: bool
    validation_message: Optional[str] = None
    stored_hash: Optional[str] = None
    current_hash: Optional[str] = None
    validated_by: Optional[int] = None
    validated_at: datetime


class ExpiryAlertResponse(BaseModel):
    """到期提醒响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    certificate_id: int
    alert_type: str
    alert_method: str
    recipient_user_id: Optional[int] = None
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    is_sent: bool
    sent_at: Optional[datetime] = None
    send_success: Optional[bool] = None
    send_message: Optional[str] = None
    alert_title: str
    alert_content: str
    created_at: datetime


class CertificateResponse(CertificateBase):
    """证书响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: CertificateStatusEnum
    digital_signature: Optional[str] = None
    verification_code: Optional[str] = None
    qr_code_data: Optional[str] = None
    imported_by: Optional[int] = None
    imported_at: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    # 计算字段
    days_until_expiry: Optional[int] = None
    is_expired: bool = False
    is_valid: bool = True
    
    # 关联数据
    files: List[CertificateFileResponse] = []
    asset_associations: List[CertificateAssetResponse] = []


class CertificateDetailResponse(CertificateResponse):
    """证书详情响应（包含更多关联数据）"""
    validations: List[CertificateValidationResponse] = []
    expiry_alerts: List[ExpiryAlertResponse] = []


class CertificateImportResponse(BaseModel):
    """证书导入响应"""
    success: bool = Field(..., description="是否成功")
    certificate_id: Optional[int] = Field(None, description="证书ID")
    certificate: Optional[CertificateResponse] = Field(None, description="证书信息")
    message: str = Field(..., description="消息")
    parsed_info: Optional[Dict[str, Any]] = Field(None, description="解析出的信息")


class CertificateBatchImportResponse(BaseModel):
    """证书批量导入响应"""
    total: int = Field(..., description="总数")
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    success_items: List[CertificateImportResponse] = Field(default_factory=list, description="成功项")
    failed_items: List[Dict[str, Any]] = Field(default_factory=list, description="失败项")
    message: str = Field(..., description="消息")


class CertificateVerifyResponse(BaseModel):
    """证书验证响应"""
    is_valid: bool = Field(..., description="是否有效")
    validation_method: str = Field(..., description="验证方法")
    validations: List[Dict[str, Any]] = Field(default_factory=list, description="验证详情")
    errors: List[str] = Field(default_factory=list, description="错误列表")
    warnings: List[str] = Field(default_factory=list, description="警告列表")
    summary: str = Field(..., description="验证总结")
    stored_hash: Optional[str] = Field(None, description="存储的哈希值")
    current_hash: Optional[str] = Field(None, description="当前文件哈希值")
    message: str = Field(..., description="验证消息")


class CertificateListResponse(BaseModel):
    """证书列表响应"""
    total: int = Field(..., description="总数")
    items: List[CertificateResponse] = Field(..., description="证书列表")
    page: int = Field(1, description="当前页", ge=1)
    page_size: int = Field(20, description="每页数量", ge=1, le=100)
    total_pages: int = Field(..., description="总页数", ge=0)


class CertificateExpiryAlert(BaseModel):
    """证书到期提醒"""
    certificate_id: int = Field(..., description="证书ID")
    certificate_no: str = Field(..., description="证书编号")
    certificate_name: Optional[str] = Field(None, description="证书名称")
    expiry_date: date = Field(..., description="有效期")
    days_until_expiry: int = Field(..., description="距离过期天数")
    alert_level: str = Field(..., description="提醒级别（info/warning/danger/critical）")
    message: str = Field(..., description="提醒消息")


class CertificateStatistics(BaseModel):
    """证书统计信息"""
    total_count: int = Field(..., description="总数")
    valid_count: int = Field(..., description="有效数量")
    expiring_count: int = Field(..., description="即将过期数量")
    expired_count: int = Field(..., description="已过期数量")
    revoked_count: int = Field(..., description="已撤销数量")
    by_type: Dict[str, int] = Field(default_factory=dict, description="按类型统计")
    by_status: Dict[str, int] = Field(default_factory=dict, description="按状态统计")


class ApiResponse(BaseModel):
    """统一API响应格式"""
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="消息")
    data: Optional[Any] = None


# ==================== 查询参数模型 ====================

class CertificateQueryParams(BaseModel):
    """证书查询参数"""
    certificate_no: Optional[str] = Field(None, description="证书编号（模糊查询）")
    certificate_type: Optional[CertificateTypeEnum] = Field(None, description="证书类型")
    status: Optional[CertificateStatusEnum] = Field(None, description="状态")
    issuing_authority: Optional[str] = Field(None, description="颁发机构（模糊查询）")
    holder_name: Optional[str] = Field(None, description="持有人姓名（模糊查询）")
    issue_date_start: Optional[date] = Field(None, description="颁发日期开始")
    issue_date_end: Optional[date] = Field(None, description="颁发日期结束")
    expiry_date_start: Optional[date] = Field(None, description="有效期开始")
    expiry_date_end: Optional[date] = Field(None, description="有效期结束")
    days_until_expiry_max: Optional[int] = Field(None, description="距离过期最大天数", ge=0)
    page: int = Field(1, description="页码", ge=1)
    page_size: int = Field(20, description="每页数量", ge=1, le=100)
    order_by: str = Field("created_at", description="排序字段")
    order_desc: bool = Field(True, description="是否降序")
