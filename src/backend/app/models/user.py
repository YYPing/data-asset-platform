"""
User and Organization models
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Organization(Base, TimestampMixin):
    """Organization model"""
    
    __tablename__ = "organizations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    unified_credit_code: Mapped[Optional[str]] = mapped_column(String(18))
    type: Mapped[Optional[str]] = mapped_column(String(50))
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id"))
    level: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    contact_person: Mapped[Optional[str]] = mapped_column(String(100))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="active")
    
    # Relationships
    parent: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        remote_side=[id],
        back_populates="children"
    )
    children: Mapped[List["Organization"]] = relationship(
        "Organization",
        back_populates="parent"
    )
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="organization"
    )
    data_assets: Mapped[List["DataAsset"]] = relationship(
        "DataAsset",
        back_populates="organization",
        foreign_keys="DataAsset.organization_id"
    )
    assessment_records: Mapped[List["AssessmentRecord"]] = relationship(
        "AssessmentRecord",
        back_populates="evaluator_org",
        foreign_keys="AssessmentRecord.evaluator_org_id"
    )


class User(Base, TimestampMixin):
    """User model"""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    password_changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default="CURRENT_TIMESTAMP"
    )
    password_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(45))
    real_name: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id"))
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="active")
    
    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        back_populates="users"
    )
    created_assets: Mapped[List["DataAsset"]] = relationship(
        "DataAsset",
        back_populates="creator",
        foreign_keys="DataAsset.created_by"
    )
    assigned_assets: Mapped[List["DataAsset"]] = relationship(
        "DataAsset",
        back_populates="assignee",
        foreign_keys="DataAsset.assigned_to"
    )
    uploaded_materials: Mapped[List["Material"]] = relationship(
        "Material",
        back_populates="uploader",
        foreign_keys="Material.uploaded_by"
    )
    reviewed_materials: Mapped[List["Material"]] = relationship(
        "Material",
        back_populates="reviewer",
        foreign_keys="Material.reviewed_by"
    )
    updated_workflow_definitions: Mapped[List["WorkflowDefinition"]] = relationship(
        "WorkflowDefinition",
        back_populates="updater"
    )
    created_workflow_instances: Mapped[List["WorkflowInstance"]] = relationship(
        "WorkflowInstance",
        back_populates="creator"
    )
    assigned_workflow_nodes: Mapped[List["WorkflowNode"]] = relationship(
        "WorkflowNode",
        back_populates="assignee"
    )
    approval_records: Mapped[List["ApprovalRecord"]] = relationship(
        "ApprovalRecord",
        back_populates="operator"
    )
    assessment_records: Mapped[List["AssessmentRecord"]] = relationship(
        "AssessmentRecord",
        back_populates="evaluator"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user"
    )
    updated_system_configs: Mapped[List["SystemConfig"]] = relationship(
        "SystemConfig",
        back_populates="updater"
    )
    imported_certificates: Mapped[List["RegistrationCertificate"]] = relationship(
        "RegistrationCertificate",
        back_populates="importer"
    )
