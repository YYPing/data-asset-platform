"""
权限控制模块
提供RBAC权限检查、角色验证、数据权限过滤
"""
from typing import List, Optional, Callable
from functools import wraps
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.user import User, Organization
from app.models.system import Permission, RolePermission
from app.core.security import get_current_user
from app.database import get_db


# 角色定义
class Role:
    """角色常量"""
    HOLDER_ADMIN = "holder_admin"      # 持有单位管理员
    HOLDER_USER = "holder_user"        # 持有单位用户
    CENTER_ADMIN = "center_admin"      # 中心管理员
    CENTER_USER = "center_user"        # 中心用户
    EVALUATOR = "evaluator"            # 评估人员
    AUDITOR = "auditor"                # 审计人员
    SYS_ADMIN = "sys_admin"            # 系统管理员
    
    # 角色组
    HOLDER_ROLES = [HOLDER_ADMIN, HOLDER_USER]
    CENTER_ROLES = [CENTER_ADMIN, CENTER_USER]
    ADMIN_ROLES = [HOLDER_ADMIN, CENTER_ADMIN, SYS_ADMIN]
    ALL_ROLES = [HOLDER_ADMIN, HOLDER_USER, CENTER_ADMIN, CENTER_USER, EVALUATOR, AUDITOR, SYS_ADMIN]


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, user: User):
        self.user = user
    
    def is_holder_role(self) -> bool:
        """是否为持有单位角色"""
        return self.user.role in Role.HOLDER_ROLES
    
    def is_center_role(self) -> bool:
        """是否为中心角色"""
        return self.user.role in Role.CENTER_ROLES
    
    def is_admin_role(self) -> bool:
        """是否为管理员角色"""
        return self.user.role in Role.ADMIN_ROLES
    
    def is_sys_admin(self) -> bool:
        """是否为系统管理员"""
        return self.user.role == Role.SYS_ADMIN
    
    def is_auditor(self) -> bool:
        """是否为审计人员"""
        return self.user.role == Role.AUDITOR
    
    def is_evaluator(self) -> bool:
        """是否为评估人员"""
        return self.user.role == Role.EVALUATOR
    
    def can_access_organization(self, organization_id: int) -> bool:
        """
        检查是否可以访问指定组织的数据
        
        Args:
            organization_id: 组织ID
            
        Returns:
            bool: 是否有权限
        """
        # 系统管理员和审计人员可以访问所有组织
        if self.user.role in [Role.SYS_ADMIN, Role.AUDITOR]:
            return True
        
        # 中心角色可以访问所有组织
        if self.is_center_role():
            return True
        
        # 持有单位角色只能访问本组织
        if self.is_holder_role():
            return self.user.organization_id == organization_id
        
        # 评估人员需要额外检查任务分配（这里简化处理）
        if self.is_evaluator():
            return False  # 需要在具体业务逻辑中检查任务分配
        
        return False
    
    def can_modify_organization(self, organization_id: int) -> bool:
        """
        检查是否可以修改指定组织的数据
        
        Args:
            organization_id: 组织ID
            
        Returns:
            bool: 是否有权限
        """
        # 审计人员只读，不能修改
        if self.is_auditor():
            return False
        
        # 系统管理员可以修改所有组织
        if self.is_sys_admin():
            return True
        
        # 中心管理员可以修改所有组织
        if self.user.role == Role.CENTER_ADMIN:
            return True
        
        # 中心用户不能修改（只能查看和审批）
        if self.user.role == Role.CENTER_USER:
            return False
        
        # 持有单位管理员只能修改本组织
        if self.user.role == Role.HOLDER_ADMIN:
            return self.user.organization_id == organization_id
        
        # 持有单位用户不能修改
        if self.user.role == Role.HOLDER_USER:
            return False
        
        return False
    
    def can_approve(self) -> bool:
        """是否有审批权限"""
        return self.user.role in [Role.CENTER_ADMIN, Role.CENTER_USER]
    
    def can_evaluate(self) -> bool:
        """是否有评估权限"""
        return self.user.role == Role.EVALUATOR
    
    def can_manage_users(self) -> bool:
        """是否可以管理用户"""
        return self.user.role == Role.SYS_ADMIN
    
    def can_view_audit_logs(self) -> bool:
        """是否可以查看审计日志"""
        return self.user.role in [Role.SYS_ADMIN, Role.AUDITOR]


def require_roles(allowed_roles: List[str]):
    """
    角色验证装饰器（用于依赖注入）
    
    Args:
        allowed_roles: 允许的角色列表
        
    Returns:
        Callable: 依赖函数
        
    Example:
        @router.get("/admin")
        async def admin_endpoint(user: User = Depends(require_roles([Role.SYS_ADMIN]))):
            pass
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要以下角色之一: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker


def require_permission(permission_code: str):
    """
    权限验证装饰器（基于权限码）
    
    Args:
        permission_code: 权限代码
        
    Returns:
        Callable: 依赖函数
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # 系统管理员拥有所有权限
        if current_user.role == Role.SYS_ADMIN:
            return current_user
        
        # 查询用户角色的权限
        result = await db.execute(
            select(Permission)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .where(
                and_(
                    RolePermission.role == current_user.role,
                    Permission.code == permission_code,
                    Permission.status == "active"
                )
            )
        )
        permission = result.scalar_one_or_none()
        
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，缺少权限: {permission_code}"
            )
        
        return current_user
    
    return permission_checker


async def check_organization_access(
    user: User,
    organization_id: int,
    require_modify: bool = False
) -> bool:
    """
    检查用户对组织的访问权限
    
    Args:
        user: 用户对象
        organization_id: 组织ID
        require_modify: 是否需要修改权限
        
    Returns:
        bool: 是否有权限
        
    Raises:
        HTTPException: 权限不足
    """
    checker = PermissionChecker(user)
    
    if require_modify:
        has_permission = checker.can_modify_organization(organization_id)
        error_msg = "无权修改该组织的数据"
    else:
        has_permission = checker.can_access_organization(organization_id)
        error_msg = "无权访问该组织的数据"
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_msg
        )
    
    return True


def apply_organization_filter(query, model, user: User):
    """
    应用组织数据过滤（数据权限）
    
    Args:
        query: SQLAlchemy查询对象
        model: 数据模型（需要有organization_id字段）
        user: 当前用户
        
    Returns:
        query: 添加了过滤条件的查询对象
        
    Example:
        query = select(Asset)
        query = apply_organization_filter(query, Asset, current_user)
        result = await db.execute(query)
    """
    checker = PermissionChecker(user)
    
    # 系统管理员、审计人员、中心角色可以查看所有数据
    if user.role in [Role.SYS_ADMIN, Role.AUDITOR] or checker.is_center_role():
        return query
    
    # 持有单位角色只能查看本组织数据
    if checker.is_holder_role():
        if hasattr(model, 'organization_id'):
            query = query.where(model.organization_id == user.organization_id)
        return query
    
    # 评估人员需要额外的任务分配过滤（这里简化处理，返回空结果）
    if checker.is_evaluator():
        if hasattr(model, 'evaluator_id'):
            query = query.where(model.evaluator_id == user.id)
        else:
            # 如果模型没有evaluator_id字段，返回空结果
            query = query.where(False)
        return query
    
    return query


async def get_accessible_organization_ids(
    user: User,
    db: AsyncSession
) -> List[int]:
    """
    获取用户可访问的组织ID列表
    
    Args:
        user: 用户对象
        db: 数据库会话
        
    Returns:
        List[int]: 组织ID列表
    """
    checker = PermissionChecker(user)
    
    # 系统管理员、审计人员、中心角色可以访问所有组织
    if user.role in [Role.SYS_ADMIN, Role.AUDITOR] or checker.is_center_role():
        result = await db.execute(
            select(Organization.id).where(Organization.status == "active")
        )
        return [row[0] for row in result.all()]
    
    # 持有单位角色只能访问本组织
    if checker.is_holder_role():
        return [user.organization_id] if user.organization_id else []
    
    # 评估人员返回空列表（需要根据任务分配动态确定）
    return []


class DataPermissionFilter:
    """数据权限过滤器（用于复杂查询）"""
    
    def __init__(self, user: User):
        self.user = user
        self.checker = PermissionChecker(user)
    
    def get_organization_filter(self, model):
        """
        获取组织过滤条件
        
        Args:
            model: 数据模型
            
        Returns:
            SQLAlchemy过滤条件
        """
        # 全局访问权限
        if self.user.role in [Role.SYS_ADMIN, Role.AUDITOR] or self.checker.is_center_role():
            return True  # 不添加过滤条件
        
        # 持有单位角色
        if self.checker.is_holder_role():
            if hasattr(model, 'organization_id'):
                return model.organization_id == self.user.organization_id
            return False
        
        # 评估人员
        if self.checker.is_evaluator():
            if hasattr(model, 'evaluator_id'):
                return model.evaluator_id == self.user.id
            return False
        
        return False
    
    def get_creator_filter(self, model):
        """
        获取创建人过滤条件（用于"我创建的"数据）
        
        Args:
            model: 数据模型
            
        Returns:
            SQLAlchemy过滤条件
        """
        if hasattr(model, 'created_by'):
            return model.created_by == self.user.id
        return False


# 常用角色依赖（快捷方式）
require_sys_admin = require_roles([Role.SYS_ADMIN])
require_admin = require_roles(Role.ADMIN_ROLES)
require_center = require_roles(Role.CENTER_ROLES)
require_holder = require_roles(Role.HOLDER_ROLES)
require_auditor = require_roles([Role.AUDITOR])
require_evaluator = require_roles([Role.EVALUATOR])
