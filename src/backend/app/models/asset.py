"""
Data Asset, Material, and Registration Certificate models
数据资产、材料和登记证书模型

Tables:
- data_assets: 数据资产表
- materials: 材料表
- registration_certificates: 登记证书表
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Numeric, BigInteger, Boolean, Date, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User, Organization
    from app.models.workflow import WorkflowInstance, ApprovalRecord
    from app.models.assessment import AssessmentRecord


class DataAsset(Base, TimestampMixin, SoftDeleteMixin):
    """
    Data Asset model - 数据资产表
    
    核心业务表，记录数据资产的全生命周期信息
    支持版本管理、软删除、全文搜索
    """
    
    __tablename__ = "data_assets"
    __table_args__ = (
        # 唯一约束
        Index('idx_data_assets_code', 'asset_code', unique=True),
        # 常用查询索引
        Index('idx_data_assets_organization', 'organization_id'),
        Index('idx_data_assets_status', 'status'),
        Index('idx_data_assets_stage', 'current_stage'),
        Index('idx_data_assets_type', 'asset_type'),
        Index('idx_data_assets_created_by', 'created_by'),
        Index('idx_data_assets_assigned_to', 'assigned_to'),
        # 复合索引 - 常用查询组合
        Index('idx_data_assets_org_status', 'organization_id', 'status'),
        Index('idx_data_assets_stage_status', 'current_stage', 'status'),
        # 全文搜索索引
        Index('idx_data_assets_search', 'search_vector', postgresql_using='gin'),
        # 软删除过滤索引
        Index('idx_data_assets_active', 'id', postgresql_where='deleted_at IS NULL'),
        # 检查约束
        CheckConstraint(
            "status IN ('draft', 'pending', 'approved', 'rejected', 'archived', 'withdrawn')", 
            name='ck_data_assets_status'
        ),
        CheckConstraint(
            "current_stage IN ('registration', 'compliance_assessment', 'value_assessment', "
            "'ownership_confirmation', 'registration_certificate', 'account_entry', "
            "'operation', 'change_management', 'supervision', 'exit')",
            name='ck_data_assets_stage'
        ),
        CheckConstraint(
            "data_classification IN ('public', 'internal', 'confidential', 'secret')",
            name='ck_data_assets_classification'
        ),
        CheckConstraint(
            "sensitivity_level IN ('low', 'medium', 'high')",
            name='ck_data_assets_sensitivity'
        ),
        CheckConstraint("version >= 1", name='ck_data_assets_version'),
        CheckConstraint("estimated_value IS NULL OR estimated_value >= 0", name='ck_data_assets_value'),
        {'comment': '数据资产表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 基本信息
    asset_code: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="资产编码（唯一）"
    )
    asset_name: Mapped[str] = mapped_column(
        String(200), 
        nullable=False,
        comment="资产名称"
    )
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        comment="所属组织ID"
    )
    
    # 分类信息
    category: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="资产类别：basic/business/management/external"
    )
    data_classification: Mapped[str] = mapped_column(
        String(20), 
        default="internal", 
        server_default="internal",
        comment="数据分类：public/internal/confidential/secret"
    )
    sensitivity_level: Mapped[str] = mapped_column(
        String(20), 
        default="low", 
        server_default="low",
        comment="敏感级别：low/medium/high"
    )
    
    # 描述信息
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="资产描述"
    )
    data_source: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="数据来源"
    )
    data_volume: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="数据量"
    )
    data_format: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="数据格式"
    )
    update_frequency: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="更新频率"
    )
    
    # 流程状态
    current_stage: Mapped[str] = mapped_column(
        String(30), 
        default="registration", 
        server_default="registration",
        comment="当前阶段"
    )
    status: Mapped[str] = mapped_column(
        String(20), 
        default="draft", 
        server_default="draft",
        comment="状态：draft/pending/approved/rejected/archived/withdrawn"
    )
    
    # 资产类型和价值
    asset_type: Mapped[Optional[str]] = mapped_column(
        String(30), 
        nullable=True,
        comment="资产类型"
    )
    estimated_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), 
        nullable=True,
        comment="估值（元）"
    )
    
    # 责任人
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="创建人ID"
    )
    assigned_to: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="当前处理人ID"
    )
    
    # 版本管理
    version: Mapped[int] = mapped_column(
        Integer, 
        default=1, 
        server_default="1",
        comment="版本号"
    )
    previous_version_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("data_assets.id", ondelete="SET NULL"),
        nullable=True,
        comment="上一版本ID"
    )
    
    # 全文搜索向量（由触发器自动更新）
    search_vector: Mapped[Optional[str]] = mapped_column(
        TSVECTOR,
        nullable=True,
        comment="全文搜索向量"
    )
    
    # ==================== Relationships ====================
    
    # 所属组织
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="data_assets",
        foreign_keys=[organization_id]
    )
    
    # 创建人
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="created_assets",
        foreign_keys=[created_by]
    )
    
    # 当前处理人
    assignee: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="assigned_assets",
        foreign_keys=[assigned_to]
    )
    
    # 版本关系
    previous_version: Mapped[Optional["DataAsset"]] = relationship(
        "DataAsset",
        remote_side=[id],
        back_populates="next_versions",
        foreign_keys=[previous_version_id]
    )
    next_versions: Mapped[List["DataAsset"]] = relationship(
        "DataAsset",
        back_populates="previous_version",
        foreign_keys=[previous_version_id]
    )
    
    # 关联材料
    materials: Mapped[List["Material"]] = relationship(
        "Material",
        back_populates="asset",
        foreign_keys="Material.asset_id",
        cascade="all, delete-orphan"
    )
    
    # 工作流实例
    workflow_instances: Mapped[List["WorkflowInstance"]] = relationship(
        "WorkflowInstance",
        back_populates="asset",
        foreign_keys="WorkflowInstance.asset_id"
    )
    
    # 审批记录
    approval_records: Mapped[List["ApprovalRecord"]] = relationship(
        "ApprovalRecord",
        back_populates="asset",
        foreign_keys="ApprovalRecord.asset_id"
    )
    
    # 评估记录
    assessment_records: Mapped[List["AssessmentRecord"]] = relationship(
        "AssessmentRecord",
        back_populates="asset",
        foreign_keys="AssessmentRecord.asset_id"
    )
    
    # 登记证书
    registration_certificates: Mapped[List["RegistrationCertificate"]] = relationship(
        "RegistrationCertificate",
        back_populates="asset",
        foreign_keys="RegistrationCertificate.asset_id"
    )


class Material(Base):
    """
    Material model - 材料表
    
    存储数据资产相关的各类材料文件信息
    """
    
    __tablename__ = "materials"
    __table_args__ = (
        # 索引
        Index('idx_materials_asset', 'asset_id'),
        Index('idx_materials_stage', 'stage'),
        Index('idx_materials_status', 'status'),
        Index('idx_materials_uploaded_by', 'uploaded_by'),
        Index('idx_materials_file_hash', 'file_hash'),
        # 复合索引
        Index('idx_materials_asset_stage', 'asset_id', 'stage'),
        # 检查约束
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'archived')",
            name='ck_materials_status'
        ),
        CheckConstraint("version >= 1", name='ck_materials_version'),
        CheckConstraint("file_size IS NULL OR file_size >= 0", name='ck_materials_file_size'),
        {'comment': '材料表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 关联资产
    asset_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("data_assets.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联资产ID"
    )
    
    # 材料信息
    material_name: Mapped[str] = mapped_column(
        String(200), 
        nullable=False,
        comment="材料名称"
    )
    material_type: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="材料类型"
    )
    stage: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="所属阶段"
    )
    
    # 文件信息
    file_path: Mapped[Optional[str]] = mapped_column(
        String(500), 
        nullable=True,
        comment="文件路径"
    )
    file_size: Mapped[Optional[int]] = mapped_column(
        BigInteger, 
        nullable=True,
        comment="文件大小（字节）"
    )
    file_format: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True,
        comment="文件格式"
    )
    file_hash: Mapped[str] = mapped_column(
        String(64), 
        nullable=False,
        comment="文件哈希（SHA-256）"
    )
    
    # 版本和状态
    version: Mapped[int] = mapped_column(
        Integer, 
        default=1, 
        server_default="1",
        comment="版本号"
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        server_default="false",
        comment="是否必需"
    )
    status: Mapped[str] = mapped_column(
        String(20), 
        default="pending", 
        server_default="pending",
        comment="状态：pending/approved/rejected/archived"
    )
    
    # 上传信息
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="上传人ID"
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        comment="上传时间"
    )
    
    # 审核信息
    reviewed_by: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="审核人ID"
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="审核时间"
    )
    review_comment: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="审核意见"
    )
    
    # ==================== Relationships ====================
    
    # 关联资产
    asset: Mapped["DataAsset"] = relationship(
        "DataAsset",
        back_populates="materials",
        foreign_keys=[asset_id]
    )
    
    # 上传人
    uploader: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="uploaded_materials",
        foreign_keys=[uploaded_by]
    )
    
    # 审核人
    reviewer: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="reviewed_materials",
        foreign_keys=[reviewed_by]
    )
    
    # 作为评估报告的评估记录
    assessment_records: Mapped[List["AssessmentRecord"]] = relationship(
        "AssessmentRecord",
        back_populates="report_material",
        foreign_keys="AssessmentRecord.report_material_id"
    )


class RegistrationCertificate(Base):
    """
    Registration Certificate model - 登记证书表
    
    存储数据资产的登记证书信息
    """
    
    __tablename__ = "registration_certificates"
    __table_args__ = (
        # 索引
        Index('idx_reg_certs_asset', 'asset_id'),
        Index('idx_reg_certs_number', 'certificate_no'),
        Index('idx_reg_certs_status', 'status'),
        Index('idx_reg_certs_expiry', 'expiry_date'),
        # 检查约束
        CheckConstraint(
            "status IN ('valid', 'expired', 'revoked', 'pending')",
            name='ck_reg_certs_status'
        ),
        CheckConstraint(
            "expiry_date IS NULL OR expiry_date >= issue_date",
            name='ck_reg_certs_dates'
        ),
        {'comment': '登记证书表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 关联资产
    asset_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("data_assets.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联资产ID"
    )
    
    # 证书信息
    certificate_no: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True,
        comment="证书编号"
    )
    issuing_authority: Mapped[Optional[str]] = mapped_column(
        String(200), 
        nullable=True,
        comment="发证机构"
    )
    issue_date: Mapped[Optional[date]] = mapped_column(
        Date, 
        nullable=True,
        comment="发证日期"
    )
    expiry_date: Mapped[Optional[date]] = mapped_column(
        Date, 
        nullable=True,
        comment="有效期至"
    )
    
    # 文件信息
    file_path: Mapped[str] = mapped_column(
        String(500), 
        nullable=False,
        comment="文件路径"
    )
    file_hash: Mapped[str] = mapped_column(
        String(64), 
        nullable=False,
        comment="文件哈希（SHA-256）"
    )
    
    # 状态
    status: Mapped[str] = mapped_column(
        String(20), 
        default="valid", 
        server_default="valid",
        comment="状态：valid/expired/revoked/pending"
    )
    
    # 导入信息
    imported_by: Mapped[Optional[int]] = mapped_column(
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
    
    # ==================== Relationships ====================
    
    # 关联资产
    asset: Mapped["DataAsset"] = relationship(
        "DataAsset",
        back_populates="registration_certificates",
        foreign_keys=[asset_id]
    )
    
    # 导入人
    importer: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="imported_certificates",
        foreign_keys=[imported_by]
    )
    
    # ==================== Properties ====================
    
    @property
    def is_expired(self) -> bool:
        """Check if certificate is expired"""
        if self.expiry_date is None:
            return False
        return date.today() > self.expiry_date
    
    @property
    def is_valid(self) -> bool:
        """Check if certificate is valid"""
        return self.status == 'valid' and not self.is_expired
