from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from app.core.database import Base


class ApprovalRecord(Base):
    __tablename__ = "approval_records"

    id = Column(Integer, primary_key=True, index=True)
    stage_record_id = Column(Integer, ForeignKey("stage_records.id"), nullable=False)
    action = Column(String(20), nullable=False)  # approve/reject
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
