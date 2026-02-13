from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    org_type = Column(String(50), nullable=False)  # enterprise, government, institution
    credit_code = Column(String(50), unique=True)  # 统一社会信用代码
    contact_person = Column(String(100))
    contact_phone = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
