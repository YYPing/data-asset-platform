"""
Organization model - 组织机构管理
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Organization(Base):
    """组织机构表"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    org_code = Column(String(50), unique=True, index=True, nullable=False, comment="机构代码")
    org_name = Column(String(200), nullable=False, comment="机构名称")
    org_type = Column(String(50), nullable=False, comment="机构类型: government/enterprise/institution")
    legal_person = Column(String(100), comment="法人代表")
    contact_person = Column(String(100), comment="联系人")
    contact_phone = Column(String(50), comment="联系电话")
    email = Column(String(100), comment="邮箱")
    address = Column(String(500), comment="地址")
    business_scope = Column(Text, comment="业务范围")
    registration_no = Column(String(100), comment="注册号")
    tax_no = Column(String(100), comment="税号")
    credit_code = Column(String(100), comment="统一社会信用代码")
    status = Column(String(20), default="active", comment="状态: active/inactive/suspended")
    level = Column(Integer, default=1, comment="机构层级")
    parent_id = Column(Integer, ForeignKey("organizations.id"), comment="上级机构ID")
    
    # 关系
    parent = relationship("Organization", remote_side=[id], backref="children")
    
    # 审计字段
    created_by = Column(Integer, comment="创建人")
    updated_by = Column(Integer, comment="更新人")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    is_deleted = Column(Boolean, default=False, comment="是否删除")
    
    def __repr__(self):
        return f"<Organization {self.org_code}: {self.org_name}>"