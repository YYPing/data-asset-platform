"""
Certificate Management Models - 证书管理模型

Tables:
- certificates: 证书主表（扩展版）
- certificate_files: 证书文件表
- certificate_assets: 证书资产关联表
- certificate_validations: 证书验证记录表
- expiry_alerts: 到期提醒记录表
"""
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Boolean, Date, Index, CheckConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.asset import DataAsset


class CertificateType(str, enum.Enum):
    """证书类型枚举"""
    REGISTRATION = "registration"  # 数据资产登记证书
    COMPLIANCE = "compliance"  # 合规评估证书
    VALUE_ASSESSMENT = "value_assessment"  # 价值评估证书
    OWNERSHIP = "ownership"  # 权属确认证书
    QUALITY = "quality"  # 质量认证证书


class CertificateStatus(str, enum.Enum):
    """证书状态枚举"""
    VALID = "valid"  # 有效
    EXPIRING = "expiring"  # 即将过期
    EXPIRED = "expired"  # 已过期
    REVOKED = "revoked"  # 已撤销
    PENDING = "pending"  # 待审核


class FileFormat(str, enum.Enum):
    """文件格式枚举"""
    PDF = "pdf"
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    EXCEL = "excel"


class ValidationStatus(str, enum.Enum):
    """验证状态枚举"""
    PASSED = "passed"  # 通过
    FAILED = "failed"  # 失败
    PENDING = "pending"  # 待验证


class AlertType(str, enum.Enum):
    """提醒类型枚举"""
    DAYS_30 = "days_30"  # 提前30天
    DAYS_7 = "days_7"  # 提前7天
    DAYS_1 = "days_1"  # 提前1天
    EXPIRED = "expired"  # 已过期


class AlertMethod(str, enum.Enum):
    """提醒方式枚举"""
    EMAIL = "email"  # 邮件
    SMS = "sms"  # 短信
    INTERNAL = "internal"  # 站内信


class Certificate(Base, TimestampMixin, SoftDeleteMixin):
    """
    Certificate model - 证书主表（扩展版）
    
    支持多种证书类型的完整管理
    """
    
    __tablename__ = "certificates"
    __table_args__ = (
        # 索引
        Index('idx_certificates_number', 'certificate_no'),
        Index('idx_certificates_type', 'certificate_type'),
        Index('idx_certificates_status', 'status'),
        Index('idx_certificates_expiry', 'expiry_date'),
        Index('idx_certificates_issuer', 'issuing_authority'),
        Index('idx_certificates_imported_by', 'imported_by'),
        # 复合索引
        Index('idx_certificates_type_status', 'certificate_type', 'status'),
        Index('idx_certificates_status_expiry', 'status', 'expiry_date'),
        # 软删除过滤索引
        Index('idx_certificates_active', 'id', postgresql_where='deleted_at IS NULL'),
        # 检查约束
        CheckConstraint(
            "expiry_date IS NULL OR expiry_date >= issue_date",
            name='ck_certificates_dates'
        ),
        {'comment': '证书主表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 证书基本信息
    certificate_no: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        comment="证书编号（唯一）"
    )
    certificate_type: Mapped[CertificateType] = mapped_column(
        SQLEnum(CertificateType, name='certificate_type_enum'),
        nullable=False,
        default=CertificateType.REGISTRATION,
        comment="证书类型"
    )
    certificate_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="证书名称"
    )
    
    # 颁发信息
    issuing_authority: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="颁发机构"
    )
    issue_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="颁发日期"
    )
    expiry_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="有效期至"
    )
    
    # 持有人信息
    holder_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="持有人姓名"
    )
    holder_id_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="持有人身份证号/组织机构代码"
    )
    
    # 状态
    status: Mapped[CertificateStatus] = mapped_column(
        SQLEnum(CertificateStatus, name='certificate_status_enum'),
        nullable=False,
        default=CertificateStatus.VALID,
        comment="证书状态"
    )
    
    # 防伪信息
    digital_signature: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="数字签名"
    )
    verification_code: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="防伪验证码"
    )
    qr_code_data: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="二维码数据"
    )
    
    # 导入信息
    imported_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="导入人ID"
    )
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        comment="导入时间"
    )
    
    # 备注
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 扩展字段（JSON格式存储其他信息）
    extra_data: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="扩展数据（JSON格式）"
    )
    
    # ==================== Relationships ====================
    
    # 导入人
    importer: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="imported_certificates",
        foreign_keys=[imported_by]
    )
    
    # 证书文件
    files: Mapped[List["CertificateFile"]] = relationship(
        "CertificateFile",
        back_populates="certificate",
        cascade="all, delete-orphan"
    )
    
    # 资产关联
    asset_associations: Mapped[List["CertificateAsset"]] = relationship(
        "CertificateAsset",
        back_populates="certificate",
        cascade="all, delete-orphan"
    )
    
    # 验证记录
    validations: Mapped[List["CertificateValidation"]] = relationship(
        "CertificateValidation",
        back_populates="certificate",
        cascade="all, delete-orphan"
    )
    
    # 到期提醒
    expiry_alerts: Mapped[List["ExpiryAlert"]] = relationship(
        "ExpiryAlert",
        back_populates="certificate",
        cascade="all, delete-orphan"
    )
    
    # ==================== Properties ====================
    
    @property
    def is_expired(self) -> bool:
        """检查证书是否已过期"""
        if self.expiry_date is None:
            return False
        return date.today() > self.expiry_date
    
    @property
    def is_valid(self) -> bool:
        """检查证书是否有效"""
        return self.status == CertificateStatus.VALID and not self.is_expired
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """距离过期的天数"""
        if self.expiry_date is None:
            return None
        delta = self.expiry_date - date.today()
        return delta.days


class CertificateFile(Base, TimestampMixin):
    """
    Certificate File model - 证书文件表
    
    存储证书的文件信息（支持多个文件）
    """
    
    __tablename__ = "certificate_files"
    __table_args__ = (
        # 索引
        Index('idx_cert_files_certificate', 'certificate_id'),
        Index('idx_cert_files_hash', 'file_hash'),
        Index('idx_cert_files_format', 'file_format'),
        # 检查约束
        CheckConstraint("file_size >= 0", name='ck_cert_files_size'),
        {'comment': '证书文件表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 关联证书
    certificate_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("certificates.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联证书ID"
    )
    
    # 文件信息
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="文件名"
    )
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="文件路径（MinIO）"
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="文件大小（字节）"
    )
    file_format: Mapped[FileFormat] = mapped_column(
        SQLEnum(FileFormat, name='file_format_enum'),
        nullable=False,
        comment="文件格式"
    )
    file_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="文件哈希（SHA-256）"
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="MIME类型"
    )
    
    # 缩略图
    thumbnail_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="缩略图路径"
    )
    
    # 是否为主文件
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        comment="是否为主文件"
    )
    
    # 上传信息
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="上传人ID"
    )
    
    # ==================== Relationships ====================
    
    # 关联证书
    certificate: Mapped["Certificate"] = relationship(
        "Certificate",
        back_populates="files"
    )
    
    # 上传人
    uploader: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[uploaded_by]
    )


class CertificateAsset(Base, TimestampMixin):
    """
    Certificate Asset Association model - 证书资产关联表
    
    一个证书可以关联多个资产
    """
    
    __tablename__ = "certificate_assets"
    __table_args__ = (
        # 索引
        Index('idx_cert_assets_certificate', 'certificate_id'),
        Index('idx_cert_assets_asset', 'asset_id'),
        Index('idx_cert_assets_status', 'is_active'),
        # 复合索引
        Index('idx_cert_assets_cert_asset', 'certificate_id', 'asset_id'),
        # 唯一约束（同一证书和资产只能有一条有效关联）
        Index('idx_cert_assets_unique', 'certificate_id', 'asset_id', 'is_active',
              unique=True, postgresql_where='is_active = true'),
        {'comment': '证书资产关联表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 关联信息
    certificate_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("certificates.id", ondelete="CASCADE"),
        nullable=False,
        comment="证书ID"
    )
    asset_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("data_assets.id", ondelete="CASCADE"),
        nullable=False,
        comment="资产ID"
    )
    
    # 关联状态
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        comment="是否有效"
    )
    
    # 关联信息
    associated_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="关联操作人ID"
    )
    associated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        comment="关联时间"
    )
    
    # 解除关联信息
    disassociated_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="解除关联操作人ID"
    )
    disassociated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="解除关联时间"
    )
    
    # 备注
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # ==================== Relationships ====================
    
    # 关联证书
    certificate: Mapped["Certificate"] = relationship(
        "Certificate",
        back_populates="asset_associations"
    )
    
    # 关联资产
    asset: Mapped["DataAsset"] = relationship(
        "DataAsset",
        foreign_keys=[asset_id]
    )
    
    # 关联操作人
    associator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[associated_by]
    )
    
    # 解除关联操作人
    disassociator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[disassociated_by]
    )


class CertificateValidation(Base, TimestampMixin):
    """
    Certificate Validation model - 证书验证记录表
    
    记录证书的验证历史
    """
    
    __tablename__ = "certificate_validations"
    __table_args__ = (
        # 索引
        Index('idx_cert_validations_certificate', 'certificate_id'),
        Index('idx_cert_validations_status', 'validation_status'),
        Index('idx_cert_validations_validated_by', 'validated_by'),
        Index('idx_cert_validations_time', 'validated_at'),
        {'comment': '证书验证记录表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 关联证书
    certificate_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("certificates.id", ondelete="CASCADE"),
        nullable=False,
        comment="证书ID"
    )
    
    # 验证信息
    validation_status: Mapped[ValidationStatus] = mapped_column(
        SQLEnum(ValidationStatus, name='validation_status_enum'),
        nullable=False,
        comment="验证状态"
    )
    validation_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="验证方法（hash/signature/qrcode/manual）"
    )
    
    # 验证结果
    is_valid: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="是否有效"
    )
    validation_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="验证消息"
    )
    
    # 哈希验证
    stored_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment="存储的哈希值"
    )
    current_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment="当前文件哈希值"
    )
    
    # 验证人
    validated_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="验证人ID"
    )
    validated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        comment="验证时间"
    )
    
    # 验证详情（JSON格式）
    validation_details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="验证详情（JSON格式）"
    )
    
    # ==================== Relationships ====================
    
    # 关联证书
    certificate: Mapped["Certificate"] = relationship(
        "Certificate",
        back_populates="validations"
    )
    
    # 验证人
    validator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[validated_by]
    )


class ExpiryAlert(Base, TimestampMixin):
    """
    Expiry Alert model - 到期提醒记录表
    
    记录证书到期提醒的发送历史
    """
    
    __tablename__ = "expiry_alerts"
    __table_args__ = (
        # 索引
        Index('idx_expiry_alerts_certificate', 'certificate_id'),
        Index('idx_expiry_alerts_type', 'alert_type'),
        Index('idx_expiry_alerts_status', 'is_sent'),
        Index('idx_expiry_alerts_time', 'sent_at'),
        # 复合索引
        Index('idx_expiry_alerts_cert_type', 'certificate_id', 'alert_type'),
        {'comment': '到期提醒记录表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 关联证书
    certificate_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("certificates.id", ondelete="CASCADE"),
        nullable=False,
        comment="证书ID"
    )
    
    # 提醒类型
    alert_type: Mapped[AlertType] = mapped_column(
        SQLEnum(AlertType, name='alert_type_enum'),
        nullable=False,
        comment="提醒类型"
    )
    
    # 提醒方式
    alert_method: Mapped[AlertMethod] = mapped_column(
        SQLEnum(AlertMethod, name='alert_method_enum'),
        nullable=False,
        comment="提醒方式"
    )
    
    # 接收人
    recipient_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="接收人ID"
    )
    recipient_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="接收人邮箱"
    )
    recipient_phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="接收人手机号"
    )
    
    # 发送状态
    is_sent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        comment="是否已发送"
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="发送时间"
    )
    
    # 发送结果
    send_success: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        comment="发送是否成功"
    )
    send_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="发送结果消息"
    )
    
    # 提醒内容
    alert_title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="提醒标题"
    )
    alert_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="提醒内容"
    )
    
    # ==================== Relationships ====================
    
    # 关联证书
    certificate: Mapped["Certificate"] = relationship(
        "Certificate",
        back_populates="expiry_alerts"
    )
    
    # 接收人
    recipient: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[recipient_user_id]
    )
