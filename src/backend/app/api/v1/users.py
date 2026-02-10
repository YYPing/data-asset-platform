"""
User management API endpoints
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import require_roles
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserResetPasswordResponse,
    UserQuery
)
from app.services.user import UserService


router = APIRouter()


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页记录数"),
    keyword: str = Query(default=None, description="搜索关键词"),
    role: str = Query(default=None, description="角色筛选"),
    status: str = Query(default=None, description="状态筛选"),
    organization_id: int = Query(default=None, description="机构ID筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "asset_manager"]))
):
    """
    获取用户列表
    
    - 支持分页
    - 支持关键词搜索（用户名/姓名/邮箱/手机号）
    - 支持角色筛选
    - 支持状态筛选
    - 支持机构筛选
    """
    query = UserQuery(
        page=page,
        page_size=page_size,
        keyword=keyword,
        role=role,
        status=status,
        organization_id=organization_id
    )
    
    users, total = await UserService.list_users(db, query)
    
    return UserListResponse(
        total=total,
        items=[UserResponse.model_validate(user) for user in users],
        page=page,
        page_size=page_size
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "asset_manager"]))
):
    """
    获取用户详情
    """
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户ID {user_id} 不存在"
        )
    
    return UserResponse.model_validate(user)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """
    创建新用户
    
    - 仅管理员可操作
    - 用户名必须唯一
    - 密码必须符合强度要求（至少8位，包含大小写字母和数字）
    """
    try:
        user = await UserService.create_user(db, user_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """
    更新用户信息
    
    - 仅管理员可操作
    - 不能修改用户名和密码（密码通过重置密码接口修改）
    """
    user = await UserService.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户ID {user_id} 不存在"
        )
    
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """
    删除用户
    
    - 仅管理员可操作
    - 不能删除系统管理员账户
    """
    try:
        success = await UserService.delete_user(db, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户ID {user_id} 不存在"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}/reset-password", response_model=UserResetPasswordResponse)
async def reset_user_password(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """
    重置用户密码
    
    - 仅管理员可操作
    - 系统自动生成随机密码
    - 返回新密码（请妥善保管并通知用户）
    - 重置后用户需要在90天内修改密码
    """
    user, new_password = await UserService.reset_password(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户ID {user_id} 不存在"
        )
    
    return UserResetPasswordResponse(
        message=f"用户 {user.username} 的密码已重置",
        new_password=new_password
    )


@router.get("/me/profile", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前登录用户信息
    """
    return UserResponse.model_validate(current_user)
