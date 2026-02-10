"""
认证API路由
提供登录、刷新、登出、获取用户信息、修改密码等接口
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserInfo,
    ChangePasswordRequest,
    PasswordChangeResponse,
    LogoutResponse
)
from app.models.user import User
from app.core.security import get_current_user, get_current_active_user
from app.core.database import get_db
from app.services import auth as auth_service


router = APIRouter(prefix="", tags=["认证"])


def get_client_ip(request: Request) -> Optional[str]:
    """
    获取客户端IP地址
    
    Args:
        request: FastAPI请求对象
        
    Returns:
        Optional[str]: IP地址
    """
    # 优先从X-Forwarded-For获取（代理场景）
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # 从X-Real-IP获取
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # 直接从client获取
    if request.client:
        return request.client.host
    
    return None


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="用户登录",
    description="使用用户名和密码登录，返回访问令牌和刷新令牌"
)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    
    - **username**: 用户名（3-50字符）
    - **password**: 密码
    
    返回：
    - **user**: 用户信息
    - **token**: 访问令牌和刷新令牌
    
    错误码：
    - 40001: 用户名或密码错误
    - 40003: 账户已被禁用
    - 40004: 账户已被锁定
    - 40005: 密码已过期
    """
    ip_address = get_client_ip(request)
    
    try:
        result = await auth_service.login(
            db=db,
            login_data=login_data,
            ip_address=ip_address
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="刷新访问令牌",
    description="使用刷新令牌获取新的访问令牌和刷新令牌"
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新访问令牌
    
    - **refresh_token**: 刷新令牌
    
    返回：
    - **access_token**: 新的访问令牌
    - **refresh_token**: 新的刷新令牌
    - **token_type**: 令牌类型（bearer）
    - **expires_in**: 访问令牌过期时间（秒）
    
    注意：
    - 旧的刷新令牌将被加入黑名单
    - 刷新令牌只能使用一次
    
    错误码：
    - 40101: 无效的刷新令牌
    - 40102: 刷新令牌已过期
    - 40103: 用户不存在或已被禁用
    """
    try:
        result = await auth_service.refresh_access_token(
            db=db,
            refresh_token=refresh_data.refresh_token
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新令牌失败: {str(e)}"
        )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="用户登出",
    description="登出当前用户，将访问令牌加入黑名单"
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登出
    
    需要认证：是
    
    功能：
    - 将当前访问令牌加入黑名单
    - 记录登出审计日志
    
    返回：
    - **message**: 登出成功消息
    
    注意：
    - 登出后需要重新登录获取新令牌
    - 已登出的令牌无法继续使用
    """
    # 从请求头获取token
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证令牌"
        )
    
    access_token = authorization.replace("Bearer ", "")
    ip_address = get_client_ip(request)
    
    try:
        result = await auth_service.logout(
            db=db,
            user=current_user,
            access_token=access_token,
            ip_address=ip_address
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出失败: {str(e)}"
        )


@router.get(
    "/me",
    response_model=UserInfo,
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息"
)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户信息
    
    需要认证：是
    
    返回：
    - **id**: 用户ID
    - **username**: 用户名
    - **real_name**: 真实姓名
    - **email**: 邮箱
    - **phone**: 手机号
    - **role**: 角色
    - **organization_id**: 组织ID
    - **organization**: 组织信息
    - **status**: 状态
    - **last_login_at**: 最后登录时间
    - **password_expires_at**: 密码过期时间
    - **created_at**: 创建时间
    """
    try:
        result = await auth_service.get_user_info(
            db=db,
            user=current_user
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )


@router.put(
    "/me/password",
    response_model=PasswordChangeResponse,
    summary="修改密码",
    description="修改当前用户的密码"
)
async def change_password(
    password_data: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码
    
    需要认证：是
    
    - **old_password**: 旧密码
    - **new_password**: 新密码（长度≥8，含大小写+数字+特殊字符）
    - **confirm_password**: 确认新密码
    
    返回：
    - **message**: 修改成功消息
    - **password_expires_at**: 新密码过期时间（90天后）
    
    密码要求：
    - 长度至少8位
    - 必须包含大写字母
    - 必须包含小写字母
    - 必须包含数字
    - 必须包含特殊字符（!@#$%^&*()_+-=[]{}|;:,.<>?/）
    - 新密码不能与旧密码相同
    
    错误码：
    - 40201: 旧密码错误
    - 40202: 新密码不符合强度要求
    - 40203: 两次输入的密码不一致
    
    注意：
    - 修改密码后需要重新登录
    - 密码90天后过期，需要再次修改
    """
    ip_address = get_client_ip(request)
    
    try:
        result = await auth_service.change_password(
            db=db,
            user=current_user,
            password_data=password_data,
            ip_address=ip_address
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改密码失败: {str(e)}"
        )


# 健康检查接口（不需要认证）
@router.get(
    "/health",
    summary="健康检查",
    description="检查认证服务是否正常运行",
    tags=["系统"]
)
async def health_check():
    """
    健康检查
    
    返回：
    - **status**: 服务状态
    - **message**: 状态消息
    """
    return {
        "status": "healthy",
        "message": "认证服务运行正常"
    }
