from sqlalchemy import Column, Integer, String, DateTime, Text, func
from app.core.database import Base


class AuditLog(Base):
    """审计日志 — 只INSERT，不可UPDATE/DELETE"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)        # create/update/delete/approve/reject/upload
    resource_type = Column(String(100), nullable=False)  # asset/material/stage/user
    resource_id = Column(Integer)
    detail = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
