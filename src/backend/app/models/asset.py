"""
Data Asset, Material, and Registration Certificate models
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Numeric, BigInteger, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class DataAsset(Base, TimestampMixin):
    """Data Asset model"""
    
    __tablename__ = "data_assets"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    asset_name: Mapped[str] = mapped_column(String(200), nullable=False)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    data_classification: Mapped[str] = mapped_column(String(20), default="internal", server_default="internal")
    sensitivity_level: Mapped[str] = mapped_column(String(20), default="low", server_default="low")
    description: Mapped[Optional[str]] = mapped_column(Text)
    data_source: Mapped[Optional[str]] = mapped_column(Text)
    data_volume: Mapped[Optional[str]] = mapped_column(String(50))
    data_format: Mapped[Optional[str]] = mapped_column(String(50))
    update_frequency: Mapped[Optional[str]] = mapped_column(String(50))
    current_stage: Mapped[str] = mapped_column(String(30), default="registration", server_default="registration")
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="draft")
    asset_type: Mapped[Optional[str]] = mapped_column(String(30))
    estimated_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    assigned_to: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    previous_version_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("data_assets.id"))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="data_assets",
        foreign_keys=[organization_id]
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="created_assets",
        foreign_keys=[created_by]
    )
    assignee: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="assigned_assets",
        foreign_keys=[assigned_to]
    )
    previous_version: Mapped[Optional["DataAsset"]] = relationship(
        "DataAsset",
        remote_side=[id],
        back_populates="next_versions"
    )
    next_versions: Mapped[List["DataAsset"]] = relationship(
        "DataAsset",
        back_populates="previous_version"
    )
    materials: Mapped[List["Material"]] = relationship(
        "Material",
        back_populates="asset"
    )
    workflow_instances: Mapped[List["WorkflowInstance"]] = relationship(
        "WorkflowInstance",
        back_populates="asset"
    )
    approval_records: Mapped[List["ApprovalRecord"]] = relationship(
        "ApprovalRecord",
        back_populates="asset"
    )
    assessment_records: Mapped[List["AssessmentRecord"]] = relationship(
        "AssessmentRecord",
        back_populates="asset"
    )
    registration_certificates: Mapped[List["RegistrationCertificate"]] = relationship(
        "RegistrationCertificate",
        back_populates="asset"
    )


class Material(Base):
    """Material model"""
    
    __tablename__ = "materials"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey("data_assets.id"), nullable=False)
    material_name: Mapped[str] = mapped_column(String(200), nullable=False)
    material_type: Mapped[Optional[str]] = mapped_column(String(50))
    stage: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    file_format: Mapped[Optional[str]] = mapped_column(String(20))
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    status: Mapped[str] = mapped_column(String(20), default="pending", server_default="pending")
    uploaded_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default="CURRENT_TIMESTAMP"
    )
    reviewed_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    review_comment: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    asset: Mapped["DataAsset"] = relationship(
        "DataAsset",
        back_populates="materials"
    )
    uploader: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="uploaded_materials",
        foreign_keys=[uploaded_by]
    )
    reviewer: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="reviewed_materials",
        foreign_keys=[reviewed_by]
    )
    assessment_records: Mapped[List["AssessmentRecord"]] = relationship(
        "AssessmentRecord",
        back_populates="report_material"
    )


class RegistrationCertificate(Base):
    """Registration Certificate model"""
    
    __tablename__ = "registration_certificates"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey("data_assets.id"), nullable=False)
    certificate_no: Mapped[Optional[str]] = mapped_column(String(100))
    issuing_authority: Mapped[Optional[str]] = mapped_column(String(200))
    issue_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="valid", server_default="valid")
    imported_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    imported_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default="CURRENT_TIMESTAMP"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    asset: Mapped["DataAsset"] = relationship(
        "DataAsset",
        back_populates="registration_certificates"
    )
    importer: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="imported_certificates"
    )
