"""
Assessment Record model
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AssessmentRecord(Base):
    """Assessment Record model"""
    
    __tablename__ = "assessment_records"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(Integer, ForeignKey("data_assets.id"), nullable=False)
    assessment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    method: Mapped[Optional[str]] = mapped_column(String(30))
    evaluator_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    evaluator_org_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id"))
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    risk_level: Mapped[Optional[str]] = mapped_column(String(10))
    result_summary: Mapped[Optional[str]] = mapped_column(Text)
    report_material_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("materials.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending", server_default="pending")
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default="CURRENT_TIMESTAMP"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    asset: Mapped["DataAsset"] = relationship(
        "DataAsset",
        back_populates="assessment_records"
    )
    evaluator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="assessment_records"
    )
    evaluator_org: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        back_populates="assessment_records",
        foreign_keys=[evaluator_org_id]
    )
    report_material: Mapped[Optional["Material"]] = relationship(
        "Material",
        back_populates="assessment_records"
    )
