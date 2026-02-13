import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.asset import AssetStage


class StageStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class StageRecord(Base):
    __tablename__ = "stage_records"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("data_assets.id"), nullable=False)
    stage = Column(Enum(AssetStage), nullable=False)
    status = Column(Enum(StageStatus), default=StageStatus.DRAFT)
    submitted_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    reject_reason = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    materials = relationship("StageMaterial", backref="stage_record")
