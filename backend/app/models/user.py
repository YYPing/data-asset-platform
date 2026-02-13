import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Role(str, enum.Enum):
    DATA_HOLDER = "data_holder"          # 数据持有方
    REGISTRY_CENTER = "registry_center"  # 登记中心
    ASSESSOR = "assessor"                # 评估机构
    COMPLIANCE = "compliance"            # 合规人员
    REGULATOR = "regulator"              # 行业监管部门
    ADMIN = "admin"                      # 系统管理员


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False, default="")
    real_name = Column(String(100))
    role = Column(Enum(Role), nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())

    organization = relationship("Organization", backref="users")
