"""
SQLAlchemy models for Data Asset Management Platform
数据资产管理平台 - SQLAlchemy模型

This package exports all database models for easy import.
支持17张核心表的完整模型定义。

Tables:
1. organizations - 组织机构表
2. users - 用户表
3. data_assets - 数据资产表
4. materials - 材料表
5. registration_certificates - 登记证书表
6. workflow_definitions - 工作流定义表
7. workflow_instances - 工作流实例表
8. workflow_nodes - 工作流节点表
9. approval_records - 审批记录表
10. assessment_records - 评估记录表
11. audit_logs - 审计日志表（分区表）
12. permissions - 权限表
13. role_permissions - 角色权限关联表
14. data_dictionaries - 数据字典表
15. notifications - 通知表
16. system_configs - 系统配置表
17. async_jobs - 异步任务表
18. operation_logs - 操作日志表
"""

# Base classes
from app.models.base import Base, TimestampMixin, SoftDeleteMixin, FullTextSearchMixin

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
    AsyncJob,
    OperationLog
)

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "FullTextSearchMixin",
    
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
    "OperationLog",
]

# Model count for verification
MODEL_COUNT = 18  # 17 tables + 1 base
