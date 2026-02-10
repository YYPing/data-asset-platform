"""
材料管理数据模型
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base


class Material(Base):
    """
    材料实体
    存储数据资产相关的材料文件信息
    """
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(100), unique=True, index=True, nullable=False, comment="材料编码")
    name = Column(String(200), nullable=False, comment="材料名称")
    description = Column(Text, comment="材料描述")
    
    # 材料类型
    type = Column(String(50), nullable=False, comment="材料类型: report, certificate, contract, other")
    
    # 文件信息
    file_name = Column(String(500), comment="原始文件名")
    file_size = Column(Integer, comment="文件大小(字节)")
    file_hash = Column(String(128), comment="文件哈希值(SHA256)")
    file_path = Column(String(1000), comment="文件存储路径")
    mime_type = Column(String(100), comment="文件MIME类型")
    
    # 关联信息
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), index=True, comment="关联的资产ID")
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="上传者ID")
    
    # 状态管理
    status = Column(String(20), default="draft", nullable=False, comment="状态: draft, submitted, approved, rejected")
    version = Column(Integer, default=1, nullable=False, comment="版本号")
    is_latest = Column(Boolean, default=True, nullable=False, comment="是否是最新版本")
    
    # 审核信息
    reviewer_id = Column(Integer, ForeignKey("users.id"), comment="审核人ID")
    review_comment = Column(Text, comment="审核意见")
    reviewed_at = Column(DateTime, comment="审核时间")
    
    # 元数据
    meta_data = Column(JSON, comment="材料元数据")
    tags = Column(JSON, comment="标签列表")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    asset = relationship("Asset", back_populates="materials")
    uploader = relationship("User", foreign_keys=[uploader_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    
    def __repr__(self):
        return f"<Material(id={self.id}, code={self.code}, name={self.name})>"


class MaterialVersion(Base):
    """
    材料版本历史
    记录材料的历史版本信息
    """
    __tablename__ = "material_versions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False, comment="版本号")
    
    # 版本信息
    name = Column(String(200), nullable=False, comment="材料名称")
    description = Column(Text, comment="材料描述")
    file_hash = Column(String(128), comment="文件哈希值")
    file_path = Column(String(1000), comment="文件存储路径")
    
    # 变更信息
    change_reason = Column(Text, comment="变更原因")
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="变更人ID")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    material = relationship("Material", back_populates="versions")
    changed_by = relationship("User")
    
    # 复合唯一约束
    __table_args__ = (
        (UniqueConstraint('material_id', 'version', name='uq_material_version')),
    )
    
    def __repr__(self):
        return f"<MaterialVersion(material_id={self.material_id}, version={self.version})>"


# 在Material模型中添加反向关系
Material.versions = relationship("MaterialVersion", back_populates="material", cascade="all, delete-orphan")


class MaterialApproval(Base):
    """
    材料审核记录
    记录材料的审核流程
    """
    __tablename__ = "material_approvals"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 审核信息
    action = Column(String(20), nullable=False, comment="审核动作: submit, approve, reject, return")
    comment = Column(Text, comment="审核意见")
    
    # 操作人
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="操作人ID")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    material = relationship("Material", back_populates="approvals")
    operator = relationship("User")
    
    def __repr__(self):
        return f"<MaterialApproval(material_id={self.material_id}, action={self.action})>"


# 在Material模型中添加审核记录反向关系
Material.approvals = relationship("MaterialApproval", back_populates="material", cascade="all, delete-orphan")


class MaterialTag(Base):
    """
    材料标签
    用于材料分类和搜索
    """
    __tablename__ = "material_tags"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, comment="标签名称")
    description = Column(Text, comment="标签描述")
    color = Column(String(20), comment="标签颜色")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<MaterialTag(id={self.id}, name={self.name})>"