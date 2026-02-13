from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, func
from app.core.database import Base


class StageMaterial(Base):
    __tablename__ = "stage_materials"

    id = Column(Integer, primary_key=True, index=True)
    stage_record_id = Column(Integer, ForeignKey("stage_records.id"), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(BigInteger)
    file_type = Column(String(50))
    hash_sha256 = Column(String(64), nullable=False)  # SHA-256哈希存证
    version = Column(Integer, default=1)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
