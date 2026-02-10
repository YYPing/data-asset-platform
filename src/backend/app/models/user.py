"""
User and Organization models
用户和组织模型

Tables:
- organizations: 组织机构表
- users: 用户表
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.asset import DataAsset, Material, RegistrationCertificate
    from app.models.workflow import WorkflowDefinition, WorkflowInstance, WorkflowNode, ApprovalRecord
    from app.models.assessment import AssessmentRecord
    from app.models.system import Notification, SystemConfig, OperationLog


class Organization(Base, TimestampMixin):
    """
    Organization model - 组织机构表
    
    支持多级组织架构，通过parent_id实现树形结构
    """
    
    __tablename__ = "organizations"
    __table_args__ = (
        # 唯一约束
        Index('idx_organizations_code', 'code', unique=True, postgresql_where='code IS NOT NULL'),
        Index('idx_organizations_parent', 'parent_id'),
        Index('idx_organizations_status', 'status'),
        # 统一社会信用代码唯一约束
        Index('idx_organizations_credit_code', 'unified_credit_code', unique=True, 
              postgresql_where='unified_credit_code IS NOT NULL'),
        # 检查约束
        CheckConstraint("level >= 1 AND level <= 10", name='ck_organizations_level'),
        CheckConstraint("status IN ('active', 'inactive', 'pending')", name='ck_organizations_status'),
        {'comment': '组织机构表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 基本信息
    name: Mapped[str] = mapped_column(
        String(200), 
        nullable=False, 
        comment="组织名称"
    )
    code: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="组织编码"
    )
    unified_credit_code: Mapped[Optional[str]] = mapped_column(
        String(18), 
        nullable=True,
        comment="统一社会信用代码"
    )
    type: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="组织类型：government/enterprise/evaluator/other"
    )
    
    # 层级关系
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        comment="父组织ID"
    )
    level: Mapped[int] = mapped_column(
        Integer, 
        default=1, 
        server_default="1",
        comment="组织层级（1为顶级）"
    )
    
    # 联系信息
    contact_person: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True,
        comment="联系人"
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True,
        comment="联系电话"
    )
    address: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="地址"
    )
    
    # 状态
    status: Mapped[str] = mapped_column(
        String(20), 
        default="active", 
        server_default="active",
        comment="状态：active/inactive/pending"
    )
    
    # ==================== Relationships ====================
    
    # 自引用关系 - 父子组织
    parent: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        remote_side=[id],
        back_populates="children",
        foreign_keys=[parent_id]
    )
    children: Mapped[List["Organization"]] = relationship(
        "Organization",
        back_populates="parent",
        foreign_keys=[parent_id]
    )
    
    # 组织下的用户
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="organization",
        foreign_keys="User.organization_id"
    )
    
    # 组织的数据资产
    data_assets: Mapped[List["DataAsset"]] = relationship(
        "DataAsset",
        back_populates="organization",
        foreign_keys="DataAsset.organization_id"
    )
    
    # 作为评估机构的评估记录
    assessment_records: Mapped[List["AssessmentRecord"]] = relationship(
        "AssessmentRecord",
        back_populates="evaluator_org",
        foreign_keys="AssessmentRecord.evaluator_org_id"
    )


class User(Base, TimestampMixin):
    """
    User model - 用户表
    
    支持多角色、密码策略、登录安全控制
    """
    
    __tablename__ = "users"
    __table_args__ = (
        # 索引
        Index('idx_users_username', 'username', unique=True),
        Index('idx_users_email', 'email', postgresql_where='email IS NOT NULL'),
        Index('idx_users_organization', 'organization_id'),
        Index('idx_users_role', 'role'),
        Index('idx_users_status', 'status'),
        # 检查约束
        CheckConstraint("status IN ('active', 'inactive', 'locked', 'pending')", name='ck_users_status'),
        CheckConstraint("role IN ('admin', 'center_auditor', 'evaluator', 'data_holder', 'viewer')", 
                       name='ck_users_role'),
        CheckConstraint("failed_login_count >= 0", name='ck_users_failed_login'),
        {'comment': '用户表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 认证信息
    username: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="用户名"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
        comment="密码哈希"
    )
    
    # 密码策略
    password_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        comment="密码修改时间"
    )
    password_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="密码过期时间"
    )
    
    # 登录安全
    failed_login_count: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        server_default="0",
        comment="登录失败次数"
    )
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="账户锁定截止时间"
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后登录时间"
    )
    last_login_ip: Mapped[Optional[str]] = mapped_column(
        String(45),  # 支持IPv6
        nullable=True,
        comment="最后登录IP"
    )
    
    # 个人信息
    real_name: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True,
        comment="真实姓名"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True,
        comment="邮箱"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True,
        comment="手机号"
    )
    
    # 角色和组织
    role: Mapped[str] = mapped_column(
        String(30), 
        nullable=False,
        comment="角色：admin/center_auditor/evaluator/data_holder/viewer"
    )
    organization_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        comment="所属组织ID"
    )
    
    # 状态
    status: Mapped[str] = mapped_column(
        String(20), 
        default="active", 
        server_default="active",
        comment="状态：active/inactive/locked/pending"
    )
    
    # ==================== Relationships ====================
    
    # 所属组织
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        back_populates="users",
        foreign_keys=[organization_id]
    )
    
    # 创建的数据资产
    created_assets: Mapped[List["DataAsset"]] = relationship(
        "DataAsset",
        back_populates="creator",
        foreign_keys="DataAsset.created_by"
    )
    
    # 被分配的数据资产
    assigned_assets: Mapped[List["DataAsset"]] = relationship(
        "DataAsset",
        back_populates="assignee",
        foreign_keys="DataAsset.assigned_to"
    )
    
    # 上传的材料
    uploaded_materials: Mapped[List["Material"]] = relationship(
        "Material",
        back_populates="uploader",
        foreign_keys="Material.uploaded_by"
    )
    
    # 审核的材料
    reviewed_materials: Mapped[List["Material"]] = relationship(
        "Material",
        back_populates="reviewer",
        foreign_keys="Material.reviewed_by"
    )
    
    # 更新的工作流定义
    updated_workflow_definitions: Mapped[List["WorkflowDefinition"]] = relationship(
        "WorkflowDefinition",
        back_populates="updater",
        foreign_keys="WorkflowDefinition.updated_by"
    )
    
    # 创建的工作流实例
    created_workflow_instances: Mapped[List["WorkflowInstance"]] = relationship(
        "WorkflowInstance",
        back_populates="creator",
        foreign_keys="WorkflowInstance.created_by"
    )
    
    # 被分配的工作流节点
    assigned_workflow_nodes: Mapped[List["WorkflowNode"]] = relationship(
        "WorkflowNode",
        back_populates="assignee",
        foreign_keys="WorkflowNode.assigned_to"
    )
    
    # 审批记录
    approval_records: Mapped[List["ApprovalRecord"]] = relationship(
        "ApprovalRecord",
        back_populates="operator",
        foreign_keys="ApprovalRecord.operator_id"
    )
    
    # 评估记录
    assessment_records: Mapped[List["AssessmentRecord"]] = relationship(
        "AssessmentRecord",
        back_populates="evaluator",
        foreign_keys="AssessmentRecord.evaluator_id"
    )
    
    # 通知
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        foreign_keys="Notification.user_id"
    )
    
    # 更新的系统配置
    updated_system_configs: Mapped[List["SystemConfig"]] = relationship(
        "SystemConfig",
        back_populates="updater",
        foreign_keys="SystemConfig.updated_by"
    )
    
    # 导入的登记证书（暂时禁用，模型类名不匹配）
    # imported_certificates: Mapped[List["RegistrationCertificate"]] = relationship(
    #     "RegistrationCertificate",
    #     back_populates="importer",
    #     foreign_keys="RegistrationCertificate.imported_by"
    # )
    
    # 操作日志
    operation_logs: Mapped[List["OperationLog"]] = relationship(
        "OperationLog",
        back_populates="user",
        foreign_keys="OperationLog.user_id"
    )
    
    # ==================== Methods ====================
    
    @property
    def is_locked(self) -> bool:
        """Check if user account is locked"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    @property
    def is_password_expired(self) -> bool:
        """Check if password is expired"""
        if self.password_expires_at is None:
            return False
        return datetime.utcnow() > self.password_expires_at
    
    def reset_failed_login(self) -> None:
        """Reset failed login count"""
        self.failed_login_count = 0
        self.locked_until = None
    
    def increment_failed_login(self, lock_minutes: int = 30, max_attempts: int = 5) -> None:
        """Increment failed login count and lock if necessary"""
        self.failed_login_count += 1
        if self.failed_login_count >= max_attempts:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=lock_minutes)
