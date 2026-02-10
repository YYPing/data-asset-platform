"""
Workflow models: WorkflowDefinition, WorkflowInstance, WorkflowNode, ApprovalRecord
工作流模型

Tables:
- workflow_definitions: 工作流定义表
- workflow_instances: 工作流实例表
- workflow_nodes: 工作流节点表
- approval_records: 审批记录表
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Boolean, Index, CheckConstraint
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.asset import DataAsset


class WorkflowDefinition(Base, TimestampMixin):
    """
    Workflow Definition model - 工作流定义表
    
    定义工作流的节点、转换规则等配置
    支持版本管理
    """
    
    __tablename__ = "workflow_definitions"
    __table_args__ = (
        # 索引
        Index('idx_wf_defs_name', 'name'),
        Index('idx_wf_defs_asset_type', 'asset_type'),
        Index('idx_wf_defs_status', 'status'),
        Index('idx_wf_defs_is_default', 'is_default'),
        # 检查约束
        CheckConstraint(
            "status IN ('active', 'inactive', 'draft', 'archived')",
            name='ck_wf_defs_status'
        ),
        CheckConstraint("version >= 1", name='ck_wf_defs_version'),
        {'comment': '工作流定义表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 基本信息
    name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="工作流名称"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="描述"
    )
    asset_type: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="适用资产类型"
    )
    
    # 工作流配置（JSONB格式）
    nodes: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        nullable=False,
        comment="节点配置"
    )
    transitions: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        nullable=False,
        comment="转换规则"
    )
    
    # 状态和版本
    is_default: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        server_default="false",
        comment="是否默认工作流"
    )
    status: Mapped[str] = mapped_column(
        String(20), 
        default="active", 
        server_default="active",
        comment="状态：active/inactive/draft/archived"
    )
    version: Mapped[int] = mapped_column(
        Integer, 
        default=1, 
        server_default="1",
        comment="版本号"
    )
    
    # 更新人
    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="最后更新人ID"
    )
    
    # ==================== Relationships ====================
    
    # 更新人
    updater: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="updated_workflow_definitions",
        foreign_keys=[updated_by]
    )
    
    # 工作流实例
    workflow_instances: Mapped[List["WorkflowInstance"]] = relationship(
        "WorkflowInstance",
        back_populates="definition",
        foreign_keys="WorkflowInstance.definition_id"
    )


class WorkflowInstance(Base):
    """
    Workflow Instance model - 工作流实例表
    
    记录每个数据资产的工作流执行实例
    """
    
    __tablename__ = "workflow_instances"
    __table_args__ = (
        # 索引
        Index('idx_wf_instances_asset', 'asset_id'),
        Index('idx_wf_instances_definition', 'definition_id'),
        Index('idx_wf_instances_status', 'status'),
        Index('idx_wf_instances_current_node', 'current_node'),
        Index('idx_wf_instances_created_by', 'created_by'),
        # 复合索引
        Index('idx_wf_instances_asset_status', 'asset_id', 'status'),
        # 检查约束
        CheckConstraint(
            "status IN ('active', 'completed', 'cancelled', 'suspended', 'failed')",
            name='ck_wf_instances_status'
        ),
        {'comment': '工作流实例表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 关联信息
    asset_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("data_assets.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联资产ID"
    )
    definition_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("workflow_definitions.id", ondelete="RESTRICT"),
        nullable=False,
        comment="工作流定义ID"
    )
    
    # 当前状态
    current_node: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="当前节点ID"
    )
    status: Mapped[str] = mapped_column(
        String(20), 
        default="active", 
        server_default="active",
        comment="状态：active/completed/cancelled/suspended/failed"
    )
    
    # 时间信息
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        comment="开始时间"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="完成时间"
    )
    deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="截止时间"
    )
    
    # 创建人
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="创建人ID"
    )
    
    # ==================== Relationships ====================
    
    # 关联资产
    asset: Mapped["DataAsset"] = relationship(
        "DataAsset",
        back_populates="workflow_instances",
        foreign_keys=[asset_id]
    )
    
    # 工作流定义
    definition: Mapped["WorkflowDefinition"] = relationship(
        "WorkflowDefinition",
        back_populates="workflow_instances",
        foreign_keys=[definition_id]
    )
    
    # 创建人
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="created_workflow_instances",
        foreign_keys=[created_by]
    )
    
    # 工作流节点
    workflow_nodes: Mapped[List["WorkflowNode"]] = relationship(
        "WorkflowNode",
        back_populates="workflow",
        foreign_keys="WorkflowNode.workflow_id",
        cascade="all, delete-orphan"
    )
    
    # 审批记录
    approval_records: Mapped[List["ApprovalRecord"]] = relationship(
        "ApprovalRecord",
        back_populates="workflow",
        foreign_keys="ApprovalRecord.workflow_id",
        cascade="all, delete-orphan"
    )
    
    # ==================== Properties ====================
    
    @property
    def is_active(self) -> bool:
        """Check if workflow is active"""
        return self.status == 'active'
    
    @property
    def is_overdue(self) -> bool:
        """Check if workflow is overdue"""
        if self.deadline is None:
            return False
        return datetime.utcnow() > self.deadline and self.status == 'active'


class WorkflowNode(Base):
    """
    Workflow Node model - 工作流节点表
    
    记录工作流实例中每个节点的执行状态
    支持串行和并行节点
    """
    
    __tablename__ = "workflow_nodes"
    __table_args__ = (
        # 索引
        Index('idx_wf_nodes_workflow', 'workflow_id'),
        Index('idx_wf_nodes_status', 'status'),
        Index('idx_wf_nodes_assigned_to', 'assigned_to'),
        Index('idx_wf_nodes_node_type', 'node_type'),
        # 复合索引
        Index('idx_wf_nodes_workflow_status', 'workflow_id', 'status'),
        # 检查约束
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'skipped', 'failed')",
            name='ck_wf_nodes_status'
        ),
        CheckConstraint(
            "node_type IN ('serial', 'parallel', 'conditional', 'auto')",
            name='ck_wf_nodes_type'
        ),
        CheckConstraint(
            "result IS NULL OR result IN ('approved', 'rejected', 'returned', 'auto_passed')",
            name='ck_wf_nodes_result'
        ),
        {'comment': '工作流节点表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 关联工作流
    workflow_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("workflow_instances.id", ondelete="CASCADE"),
        nullable=False,
        comment="工作流实例ID"
    )
    
    # 节点信息
    node_id: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="节点ID（对应定义中的节点）"
    )
    node_type: Mapped[str] = mapped_column(
        String(20), 
        default="serial", 
        server_default="serial",
        comment="节点类型：serial/parallel/conditional/auto"
    )
    parallel_group: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="并行组ID（用于并行节点分组）"
    )
    
    # 状态
    status: Mapped[str] = mapped_column(
        String(20), 
        default="pending", 
        server_default="pending",
        comment="状态：pending/in_progress/completed/skipped/failed"
    )
    
    # 分配信息
    assigned_to: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="处理人ID"
    )
    
    # 时间信息
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
    deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="截止时间"
    )
    
    # 结果
    result: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True,
        comment="处理结果：approved/rejected/returned/auto_passed"
    )
    comment: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="处理意见"
    )
    
    # ==================== Relationships ====================
    
    # 工作流实例
    workflow: Mapped["WorkflowInstance"] = relationship(
        "WorkflowInstance",
        back_populates="workflow_nodes",
        foreign_keys=[workflow_id]
    )
    
    # 处理人
    assignee: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="assigned_workflow_nodes",
        foreign_keys=[assigned_to]
    )


class ApprovalRecord(Base):
    """
    Approval Record model - 审批记录表
    
    记录每次审批操作的详细信息
    """
    
    __tablename__ = "approval_records"
    __table_args__ = (
        # 索引
        Index('idx_approval_records_workflow', 'workflow_id'),
        Index('idx_approval_records_asset', 'asset_id'),
        Index('idx_approval_records_operator', 'operator_id'),
        Index('idx_approval_records_action', 'action'),
        Index('idx_approval_records_operated_at', 'operated_at'),
        # 复合索引
        Index('idx_approval_records_asset_action', 'asset_id', 'action'),
        # 检查约束
        CheckConstraint(
            "action IN ('submit', 'approve', 'reject', 'return', 'withdraw', 'reassign', 'comment')",
            name='ck_approval_records_action'
        ),
        {'comment': '审批记录表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 关联信息
    workflow_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("workflow_instances.id", ondelete="CASCADE"),
        nullable=False,
        comment="工作流实例ID"
    )
    asset_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("data_assets.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联资产ID"
    )
    
    # 节点信息
    node_name: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="节点名称"
    )
    
    # 操作信息
    action: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        comment="操作类型：submit/approve/reject/return/withdraw/reassign/comment"
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="操作人ID"
    )
    comment: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="审批意见"
    )
    
    # 驳回信息
    reject_to_node: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="驳回到的节点（用于return操作）"
    )
    
    # 操作时间
    operated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        comment="操作时间"
    )
    
    # ==================== Relationships ====================
    
    # 工作流实例
    workflow: Mapped["WorkflowInstance"] = relationship(
        "WorkflowInstance",
        back_populates="approval_records",
        foreign_keys=[workflow_id]
    )
    
    # 关联资产
    asset: Mapped["DataAsset"] = relationship(
        "DataAsset",
        back_populates="approval_records",
        foreign_keys=[asset_id]
    )
    
    # 操作人
    operator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="approval_records",
        foreign_keys=[operator_id]
    )
