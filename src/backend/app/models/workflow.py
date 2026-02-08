"""
Workflow models: WorkflowDefinition, WorkflowInstance, WorkflowNode, ApprovalRecord
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class WorkflowDefinition(Base):
    """Workflow Definition model"""
    
    __tablename__ = "workflow_definitions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    asset_type: Mapped[Optional[str]] = mapped_column(String(50))
    nodes: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    transitions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="active")
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default="CURRENT_TIMESTAMP"
    )
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    
    # Relationships
    updater: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="updated_workflow_definitions"
    )
    workflow_instances: Mapped[List["WorkflowInstance"]] = relationship(
        "WorkflowInstance",
        back_populates="definition"
    )


class WorkflowInstance(Base):
    """Workflow Instance model"""
    
    __tablename__ = "workflow_instances"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey("data_assets.id"), nullable=False)
    definition_id: Mapped[int] = mapped_column(Integer, ForeignKey("workflow_definitions.id"), nullable=False)
    current_node: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="active")
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default="CURRENT_TIMESTAMP"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    
    # Relationships
    asset: Mapped["DataAsset"] = relationship(
        "DataAsset",
        back_populates="workflow_instances"
    )
    definition: Mapped["WorkflowDefinition"] = relationship(
        "WorkflowDefinition",
        back_populates="workflow_instances"
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="created_workflow_instances"
    )
    workflow_nodes: Mapped[List["WorkflowNode"]] = relationship(
        "WorkflowNode",
        back_populates="workflow"
    )
    approval_records: Mapped[List["ApprovalRecord"]] = relationship(
        "ApprovalRecord",
        back_populates="workflow"
    )


class WorkflowNode(Base):
    """Workflow Node model"""
    
    __tablename__ = "workflow_nodes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workflow_id: Mapped[int] = mapped_column(Integer, ForeignKey("workflow_instances.id"), nullable=False)
    node_id: Mapped[str] = mapped_column(String(50), nullable=False)
    node_type: Mapped[str] = mapped_column(String(20), default="serial", server_default="serial")
    parallel_group: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="pending", server_default="pending")
    assigned_to: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)
    result: Mapped[Optional[str]] = mapped_column(String(20))
    comment: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    workflow: Mapped["WorkflowInstance"] = relationship(
        "WorkflowInstance",
        back_populates="workflow_nodes"
    )
    assignee: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="assigned_workflow_nodes"
    )


class ApprovalRecord(Base):
    """Approval Record model"""
    
    __tablename__ = "approval_records"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workflow_id: Mapped[int] = mapped_column(Integer, ForeignKey("workflow_instances.id"), nullable=False)
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey("data_assets.id"), nullable=False)
    node_name: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    operator_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    comment: Mapped[Optional[str]] = mapped_column(Text)
    reject_to_node: Mapped[Optional[str]] = mapped_column(String(50))
    operated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default="CURRENT_TIMESTAMP"
    )
    
    # Relationships
    workflow: Mapped["WorkflowInstance"] = relationship(
        "WorkflowInstance",
        back_populates="approval_records"
    )
    asset: Mapped["DataAsset"] = relationship(
        "DataAsset",
        back_populates="approval_records"
    )
    operator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="approval_records"
    )
