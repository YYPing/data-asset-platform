from sqlalchemy import Text
"""
Base models and mixins for SQLAlchemy 2.0
数据资产管理平台 - 基础模型定义

Features:
- 异步支持 (asyncpg)
- 时间戳自动管理
- 软删除支持
- 中文全文搜索支持
"""
from datetime import datetime
from typing import Optional, Any

from sqlalchemy import DateTime, func, event, String, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr



class Base(DeclarativeBase):
    """
    Base class for all models
    所有模型的基类
    """
    
    # 类型注解映射
    type_annotation_map = {
        str: String(255),
    }
    
    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self) -> str:
        """String representation"""
        pk = getattr(self, 'id', None)
        return f"<{self.__class__.__name__}(id={pk})>"


class TimestampMixin:
    """
    Mixin for created_at and updated_at timestamps
    时间戳混入类，自动管理创建和更新时间
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        comment="创建时间"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        comment="更新时间"
    )


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality
    软删除混入类
    """
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="删除时间（软删除）"
    )
    
    @property
    def is_deleted(self) -> bool:
        """Check if record is soft deleted"""
        return self.deleted_at is not None
    
    def soft_delete(self) -> None:
        """Mark record as deleted"""
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore soft deleted record"""
        self.deleted_at = None


class FullTextSearchMixin:
    """
    Mixin for Chinese full-text search support
    中文全文搜索混入类（需要zhparser扩展）
    
    Usage:
        class MyModel(Base, FullTextSearchMixin):
            __searchable_columns__ = ['name', 'description']
    """
    
    # 子类需要定义可搜索的列
    __searchable_columns__: list[str] = []
    
    # 全文搜索向量列（由触发器自动更新）
    search_vector: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="全文搜索向量"
    )
    
    @declared_attr
    def __table_args__(cls):
        """Add GIN index for full-text search"""
        args = getattr(super(), '__table_args__', ())
        if isinstance(args, dict):
            args = (args,)
        
        # 添加全文搜索索引
        if cls.__searchable_columns__:
            search_idx = Index(
                f'idx_{cls.__tablename__}_search',
                'search_vector',
                postgresql_using='gin'
            )
            args = args + (search_idx,)
        
        return args


# 审计日志事件监听器
def audit_log_listener(mapper, connection, target):
    """
    Event listener for audit logging
    可以在模型变更时自动记录审计日志
    """
    pass  # 实际实现需要根据业务需求定制
