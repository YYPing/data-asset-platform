"""
System models: AuditLog, Permission, RolePermission, DataDictionary, Notification, SystemConfig, AsyncJob
"""
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Boolean, JSON, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AuditLog(Base):
    """Audit Log model (partitioned by created_at)"""
    
    __tablename__ = "audit_logs"
    __table_args__ = {
        'postgresql_partition_by': 'RANGE (created_at)'
    }
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    username: Mapped[Optional[str]] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[Optional[int]] = mapped_column(Integer)
    detail: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    result: Mapped[str] = mapped_column(String(10), default="success", server_default="success")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        primary_key=True,
        server_default="CURRENT_TIMESTAMP"
    )


class Permission(Base):
    """Permission model"""
    
    __tablename__ = "permissions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    resource: Mapped[Optional[str]] = mapped_column(String(50))
    action: Mapped[Optional[str]] = mapped_column(String(20))
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="permission"
    )


class RolePermission(Base):
    """Role Permission model"""
    
    __tablename__ = "role_permissions"
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("permissions.id"), nullable=False)
    
    # Relationships
    permission: Mapped["Permission"] = relationship(
        "Permission",
        back_populates="role_permissions"
    )


class DataDictionary(Base):
    """Data Dictionary model"""
    
    __tablename__ = "data_dictionaries"
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dict_type: Mapped[str] = mapped_column(String(50), nullable=False)
    dict_code: Mapped[str] = mapped_column(String(50), nullable=False)
    dict_label: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    status: Mapped[str] = mapped_column(String(10), default="active", server_default="active")


class Notification(Base):
    """Notification model"""
    
    __tablename__ = "notifications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(30), default="info", server_default="info")
    related_asset_id: Mapped[Optional[int]] = mapped_column(Integer)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default="CURRENT_TIMESTAMP"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications"
    )


class SystemConfig(Base):
    """System Config model"""
    
    __tablename__ = "system_configs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    config_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    config_value: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(String(200))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        onupdate="CURRENT_TIMESTAMP"
    )
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    
    # Relationships
    updater: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="updated_system_configs"
    )


class AsyncJob(Base):
    """Async Job model"""
    
    __tablename__ = "async_jobs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="pending", server_default="pending")
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    max_retries: Mapped[int] = mapped_column(Integer, default=3, server_default="3")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default="CURRENT_TIMESTAMP"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
