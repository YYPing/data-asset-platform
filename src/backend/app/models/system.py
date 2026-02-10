"""
System models: AuditLog, Permission, RolePermission, DataDictionary, Notification, SystemConfig, AsyncJob, OperationLog
系统模型

Tables:
- audit_logs: 审计日志表（分区表）
- permissions: 权限表
- role_permissions: 角色权限关联表
- data_dictionaries: 数据字典表
- notifications: 通知表
- system_configs: 系统配置表
- async_jobs: 异步任务表
- operation_logs: 操作日志表
"""
from datetime import datetime
from typing import Optional, Dict, Any, List, TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Boolean, BigInteger, Index, CheckConstraint, UniqueConstraint
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(Base):
    """
    Audit Log model - 审计日志表（按时间分区）
    
    记录系统所有重要操作的审计日志
    使用PostgreSQL范围分区，按created_at字段分区
    """
    
    __tablename__ = "audit_logs"
    __table_args__ = (
        # 索引
        Index('idx_audit_logs_user', 'user_id'),
        Index('idx_audit_logs_action', 'action'),
        Index('idx_audit_logs_resource', 'resource_type'),
        Index('idx_audit_logs_resource_id', 'resource_id'),
        Index('idx_audit_logs_result', 'result'),
        # 复合索引
        Index('idx_audit_logs_resource_action', 'resource_type', 'action'),
        Index('idx_audit_logs_user_action', 'user_id', 'action'),
        # 分区配置
        {
            'postgresql_partition_by': 'RANGE (created_at)',
            'comment': '审计日志表（按时间分区）'
        }
    )
    
    # 复合主键（分区表需要包含分区键）
    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True,
        comment="主键ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        primary_key=True,
        server_default="CURRENT_TIMESTAMP",
        comment="创建时间（分区键）"
    )
    
    # 用户信息（不使用外键，因为是分区表）
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        nullable=True,
        comment="用户ID"
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="用户名（冗余存储）"
    )
    
    # 操作信息
    action: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="操作类型：create/read/update/delete/login/logout/export等"
    )
    resource_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="资源类型：user/asset/workflow等"
    )
    resource_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        nullable=True,
        comment="资源ID"
    )
    
    # 详细信息
    detail: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, 
        nullable=True,
        comment="操作详情（JSON格式）"
    )
    
    # 客户端信息
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # 支持IPv6
        nullable=True,
        comment="客户端IP"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="User-Agent"
    )
    
    # 结果
    result: Mapped[str] = mapped_column(
        String(10), 
        default="success", 
        server_default="success",
        comment="操作结果：success/failure"
    )


class Permission(Base):
    """
    Permission model - 权限表
    
    定义系统中的所有权限
    """
    
    __tablename__ = "permissions"
    __table_args__ = (
        # 索引
        Index('idx_permissions_code', 'code', unique=True),
        Index('idx_permissions_resource', 'resource'),
        Index('idx_permissions_action', 'action'),
        {'comment': '权限表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 权限信息
    code: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="权限编码（唯一）"
    )
    name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="权限名称"
    )
    resource: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="资源类型"
    )
    action: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True,
        comment="操作类型：read/write/delete/admin"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="描述"
    )
    
    # ==================== Relationships ====================
    
    # 角色权限关联
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="permission",
        foreign_keys="RolePermission.permission_id",
        cascade="all, delete-orphan"
    )


class RolePermission(Base):
    """
    Role Permission model - 角色权限关联表
    
    定义角色和权限的多对多关系
    """
    
    __tablename__ = "role_permissions"
    __table_args__ = (
        # 唯一约束
        UniqueConstraint('role', 'permission_id', name='uq_role_permissions'),
        # 索引
        Index('idx_role_permissions_role', 'role'),
        Index('idx_role_permissions_permission', 'permission_id'),
        # 检查约束
        CheckConstraint(
            "role IN ('admin', 'center_auditor', 'evaluator', 'data_holder', 'viewer')",
            name='ck_role_permissions_role'
        ),
        {'comment': '角色权限关联表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 角色和权限
    role: Mapped[str] = mapped_column(
        String(30), 
        nullable=False,
        comment="角色：admin/center_auditor/evaluator/data_holder/viewer"
    )
    permission_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        comment="权限ID"
    )
    
    # ==================== Relationships ====================
    
    # 权限
    permission: Mapped["Permission"] = relationship(
        "Permission",
        back_populates="role_permissions",
        foreign_keys=[permission_id]
    )


class DataDictionary(Base):
    """
    Data Dictionary model - 数据字典表
    
    存储系统中的各类枚举值和配置项
    """
    
    __tablename__ = "data_dictionaries"
    __table_args__ = (
        # 唯一约束
        UniqueConstraint('dict_type', 'dict_code', name='uq_data_dictionaries'),
        # 索引
        Index('idx_data_dictionaries_type', 'dict_type'),
        Index('idx_data_dictionaries_status', 'status'),
        # 检查约束
        CheckConstraint(
            "status IN ('active', 'inactive')",
            name='ck_data_dictionaries_status'
        ),
        CheckConstraint("sort_order >= 0", name='ck_data_dictionaries_sort'),
        {'comment': '数据字典表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 字典信息
    dict_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="字典类型"
    )
    dict_code: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="字典编码"
    )
    dict_label: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="字典标签（显示值）"
    )
    
    # 排序和状态
    sort_order: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        server_default="0",
        comment="排序序号"
    )
    status: Mapped[str] = mapped_column(
        String(10), 
        default="active", 
        server_default="active",
        comment="状态：active/inactive"
    )


class Notification(Base):
    """
    Notification model - 通知表
    
    存储用户通知消息
    """
    
    __tablename__ = "notifications"
    __table_args__ = (
        # 索引
        Index('idx_notifications_user', 'user_id'),
        Index('idx_notifications_type', 'type'),
        Index('idx_notifications_is_read', 'is_read'),
        Index('idx_notifications_created_at', 'created_at'),
        # 复合索引
        Index('idx_notifications_user_unread', 'user_id', 'is_read', 
              postgresql_where='is_read = false'),
        # 检查约束
        CheckConstraint(
            "type IN ('info', 'warning', 'error', 'success', 'task', 'system')",
            name='ck_notifications_type'
        ),
        {'comment': '通知表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 用户
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID"
    )
    
    # 通知内容
    title: Mapped[str] = mapped_column(
        String(200), 
        nullable=False,
        comment="标题"
    )
    content: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="内容"
    )
    type: Mapped[str] = mapped_column(
        String(30), 
        default="info", 
        server_default="info",
        comment="类型：info/warning/error/success/task/system"
    )
    
    # 关联资产
    related_asset_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        nullable=True,
        comment="关联资产ID"
    )
    
    # 状态
    is_read: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        server_default="false",
        comment="是否已读"
    )
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        comment="创建时间"
    )
    
    # ==================== Relationships ====================
    
    # 用户
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications",
        foreign_keys=[user_id]
    )


class SystemConfig(Base):
    """
    System Config model - 系统配置表
    
    存储系统配置项
    """
    
    __tablename__ = "system_configs"
    __table_args__ = (
        # 索引
        Index('idx_system_configs_key', 'config_key', unique=True),
        {'comment': '系统配置表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 配置信息
    config_key: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="配置键（唯一）"
    )
    config_value: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="配置值"
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(200), 
        nullable=True,
        comment="描述"
    )
    
    # 更新信息
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        onupdate="CURRENT_TIMESTAMP",
        comment="更新时间"
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="更新人ID"
    )
    
    # ==================== Relationships ====================
    
    # 更新人
    updater: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="updated_system_configs",
        foreign_keys=[updated_by]
    )


class AsyncJob(Base):
    """
    Async Job model - 异步任务表
    
    存储异步任务信息，支持任务队列和重试机制
    """
    
    __tablename__ = "async_jobs"
    __table_args__ = (
        # 索引
        Index('idx_async_jobs_type', 'job_type'),
        Index('idx_async_jobs_status', 'status'),
        Index('idx_async_jobs_created_at', 'created_at'),
        # 复合索引
        Index('idx_async_jobs_pending', 'status', 'created_at',
              postgresql_where="status = 'pending'"),
        # 检查约束
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'cancelled')",
            name='ck_async_jobs_status'
        ),
        CheckConstraint("retry_count >= 0", name='ck_async_jobs_retry'),
        CheckConstraint("max_retries >= 0", name='ck_async_jobs_max_retries'),
        {'comment': '异步任务表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 任务信息
    job_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="任务类型"
    )
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, 
        nullable=True,
        comment="任务参数（JSON格式）"
    )
    
    # 状态
    status: Mapped[str] = mapped_column(
        String(20), 
        default="pending", 
        server_default="pending",
        comment="状态：pending/running/completed/failed/cancelled"
    )
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, 
        nullable=True,
        comment="执行结果（JSON格式）"
    )
    
    # 重试机制
    retry_count: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        server_default="0",
        comment="已重试次数"
    )
    max_retries: Mapped[int] = mapped_column(
        Integer, 
        default=3, 
        server_default="3",
        comment="最大重试次数"
    )
    
    # 时间信息
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        comment="创建时间"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="开始时间"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="完成时间"
    )
    
    # 错误信息
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="错误信息"
    )
    
    # ==================== Properties ====================
    
    @property
    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return self.status == 'failed' and self.retry_count < self.max_retries


class OperationLog(Base):
    """
    Operation Log model - 操作日志表
    
    记录用户的业务操作日志（比审计日志更详细）
    """
    
    __tablename__ = "operation_logs"
    __table_args__ = (
        # 索引
        Index('idx_operation_logs_user', 'user_id'),
        Index('idx_operation_logs_type', 'operation_type'),
        Index('idx_operation_logs_target', 'target_type'),
        Index('idx_operation_logs_target_id', 'target_id'),
        Index('idx_operation_logs_result', 'result'),
        Index('idx_operation_logs_created_at', 'created_at'),
        # 复合索引
        Index('idx_operation_logs_target_full', 'target_type', 'target_id'),
        # 检查约束
        CheckConstraint(
            "result IN ('success', 'failure', 'partial')",
            name='ck_operation_logs_result'
        ),
        {'comment': '操作日志表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 用户
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="用户ID"
    )
    
    # 操作信息
    operation_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="操作类型"
    )
    target_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="目标类型"
    )
    target_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        nullable=True,
        comment="目标ID"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="操作描述"
    )
    
    # 客户端信息
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # 支持IPv6
        nullable=True,
        comment="客户端IP"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="User-Agent"
    )
    
    # 结果
    result: Mapped[str] = mapped_column(
        String(20), 
        default="success", 
        server_default="success",
        comment="操作结果：success/failure/partial"
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="错误信息"
    )
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        comment="创建时间"
    )
    
    # ==================== Relationships ====================
    
    # 用户
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="operation_logs",
        foreign_keys=[user_id]
    )
