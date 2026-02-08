"""
SQLAlchemy models for Data Asset Management Platform

This package exports all database models for easy import.
"""

# Base classes
from app.models.base import Base, TimestampMixin

# User and Organization models
from app.models.user import User, Organization

# Asset-related models
from app.models.asset import DataAsset, Material, RegistrationCertificate

# Workflow models
from app.models.workflow import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowNode,
    ApprovalRecord
)

# Assessment model
from app.models.assessment import AssessmentRecord

# System models
from app.models.system import (
    AuditLog,
    Permission,
    RolePermission,
    DataDictionary,
    Notification,
    SystemConfig,
    AsyncJob
)

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    
    # User & Organization
    "User",
    "Organization",
    
    # Assets
    "DataAsset",
    "Material",
    "RegistrationCertificate",
    
    # Workflow
    "WorkflowDefinition",
    "WorkflowInstance",
    "WorkflowNode",
    "ApprovalRecord",
    
    # Assessment
    "AssessmentRecord",
    
    # System
    "AuditLog",
    "Permission",
    "RolePermission",
    "DataDictionary",
    "Notification",
    "SystemConfig",
    "AsyncJob",
]
