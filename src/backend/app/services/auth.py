"""
认证服务层
处理登录、刷新、登出、修改密码等业务逻辑
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status

from app.models.user import User, Organization
from app.models.system import AuditLog
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    LoginResponse,
    UserInfo,
    OrganizationInfo,
    ChangePasswordRequest,
    PasswordChangeResponse
)
from app.core.security import (
    verify_password,
    get_password_hash,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    add_token_to_blacklist
)
from app.core.config import settings


async def create_audit_log(
    db: AsyncSession,
    user_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: Optional[int],
    details: Optional[str],
    ip_address: Optional[str],
    status: str = "success"
) -> None:
    """
    创建审计日志（使用独立session，不影响主事务）
    """
    try:
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as audit_session:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                detail=details,
                ip_address=ip_address,
                result=status,
                created_at=datetime.utcnow()
            )
            audit_session.add(audit_log)
            await audit_session.commit()
    except Exception as e:
        # 审计日志失败不应影响主流程
        print(f"创建审计日志失败: {e}")


async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str,
    ip_address: Optional[str] = None
) -> Tuple[User, Organization]:
    """
    用户认证
    
    Args:
        db: 数据库会话
        username: 用户名
        password: 密码
        ip_address: 登录IP地址
        
    Returns:
        Tuple[User, Organization]: 用户对象和组织对象
        
    Raises:
        HTTPException: 认证失败
    """
    # 查询用户
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    # 用户不存在
    if not user:
        await create_audit_log(
            db=db,
            user_id=None,
            action="login",
            resource_type="user",
            resource_id=None,
            details=f"用户名不存在: {username}",
            ip_address=ip_address,
            status="failure"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查账户状态
    if user.status != "active":
        await create_audit_log(
            db=db,
            user_id=user.id,
            action="login",
            resource_type="user",
            resource_id=user.id,
            details=f"账户已被禁用: {username}",
            ip_address=ip_address,
            status="failure"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    
    # 检查账户锁定
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining_minutes = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
        await create_audit_log(
            db=db,
            user_id=user.id,
            action="login",
            resource_type="user",
            resource_id=user.id,
            details=f"账户已锁定，剩余{remaining_minutes}分钟",
            ip_address=ip_address,
            status="failure"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"账户已被锁定，请在{remaining_minutes}分钟后重试"
        )
    
    # 验证密码
    if not verify_password(password, user.password_hash):
        # 增加失败次数
        failed_count = (user.failed_login_count or 0) + 1
        
        # 5次失败后锁定30分钟
        if failed_count >= 5:
            locked_until = datetime.utcnow() + timedelta(minutes=30)
            await db.execute(
                update(User)
                .where(User.id == user.id)
                .values(
                    failed_login_count=failed_count,
                    locked_until=locked_until
                )
            )
            await db.commit()
            
            await create_audit_log(
                db=db,
                user_id=user.id,
                action="login",
                resource_type="user",
                resource_id=user.id,
                details=f"密码错误次数过多，账户已锁定30分钟",
                ip_address=ip_address,
                status="failure"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="密码错误次数过多，账户已被锁定30分钟"
            )
        else:
            await db.execute(
                update(User)
                .where(User.id == user.id)
                .values(failed_login_count=failed_count)
            )
            await db.commit()
            
            await create_audit_log(
                db=db,
                user_id=user.id,
                action="login",
                resource_type="user",
                resource_id=user.id,
                details=f"密码错误，失败次数: {failed_count}/5",
                ip_address=ip_address,
                status="failure"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"用户名或密码错误（剩余尝试次数: {5 - failed_count}）"
            )
    
    # 检查密码是否过期
    if user.password_expires_at and user.password_expires_at < datetime.utcnow():
        await create_audit_log(
            db=db,
            user_id=user.id,
            action="login",
            resource_type="user",
            resource_id=user.id,
            details="密码已过期",
            ip_address=ip_address,
            status="failure"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="密码已过期，请联系管理员重置密码"
        )
    
    # 查询组织信息
    organization = None
    if user.organization_id:
        result = await db.execute(
            select(Organization).where(Organization.id == user.organization_id)
        )
        organization = result.scalar_one_or_none()
    
    # 更新登录信息
    await db.execute(
        update(User)
        .where(User.id == user.id)
        .values(
            failed_login_count=0,
            locked_until=None,
            last_login_at=datetime.utcnow(),
            last_login_ip=ip_address
        )
    )
    await db.commit()
    
    # 记录成功登录
    await create_audit_log(
        db=db,
        user_id=user.id,
        action="login",
        resource_type="user",
        resource_id=user.id,
        details=f"用户登录成功: {username}",
        ip_address=ip_address,
        status="success"
    )
    
    return user, organization


async def login(
    db: AsyncSession,
    login_data: LoginRequest,
    ip_address: Optional[str] = None
) -> LoginResponse:
    """
    用户登录
    
    Args:
        db: 数据库会话
        login_data: 登录请求数据
        ip_address: 登录IP地址
        
    Returns:
        LoginResponse: 登录响应（包含用户信息和Token）
    """
    # 认证用户
    user, organization = await authenticate_user(
        db=db,
        username=login_data.username,
        password=login_data.password,
        ip_address=ip_address
    )
    
    # 生成Token
    token_data = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # 构建响应
    user_info = UserInfo(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        organization_id=user.organization_id,
        organization=OrganizationInfo.from_orm(organization) if organization else None,
        status=user.status,
        last_login_at=user.last_login_at,
        password_expires_at=user.password_expires_at,
        created_at=user.created_at
    )
    
    token_response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return LoginResponse(user=user_info, token=token_response)


async def refresh_access_token(
    db: AsyncSession,
    refresh_token: str
) -> TokenResponse:
    """
    刷新访问令牌
    
    Args:
        db: 数据库会话
        refresh_token: 刷新令牌
        
    Returns:
        TokenResponse: 新的Token
        
    Raises:
        HTTPException: Token无效或用户不存在
    """
    # 验证refresh token
    payload = verify_refresh_token(refresh_token)
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的refresh token"
        )
    
    # 查询用户
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    
    # 生成新的Token
    token_data = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }
    
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    # 将旧的refresh token加入黑名单
    add_token_to_blacklist(refresh_token)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


async def logout(
    db: AsyncSession,
    user: User,
    access_token: str,
    ip_address: Optional[str] = None
) -> dict:
    """
    用户登出
    
    Args:
        db: 数据库会话
        user: 当前用户
        access_token: 访问令牌
        ip_address: IP地址
        
    Returns:
        dict: 登出响应
    """
    # 将access token加入黑名单
    add_token_to_blacklist(access_token)
    
    # 记录审计日志
    await create_audit_log(
        db=db,
        user_id=user.id,
        action="logout",
        resource_type="user",
        resource_id=user.id,
        details=f"用户登出: {user.username}",
        ip_address=ip_address,
        status="success"
    )
    
    return {"message": "登出成功"}


async def change_password(
    db: AsyncSession,
    user: User,
    password_data: ChangePasswordRequest,
    ip_address: Optional[str] = None
) -> PasswordChangeResponse:
    """
    修改密码
    
    Args:
        db: 数据库会话
        user: 当前用户
        password_data: 密码修改数据
        ip_address: IP地址
        
    Returns:
        PasswordChangeResponse: 修改密码响应
        
    Raises:
        HTTPException: 旧密码错误或新密码不符合要求
    """
    # 验证旧密码
    if not verify_password(password_data.old_password, user.password_hash):
        await create_audit_log(
            db=db,
            user_id=user.id,
            action="change_password",
            resource_type="user",
            resource_id=user.id,
            details="旧密码错误",
            ip_address=ip_address,
            status="failure"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 验证新密码强度
    is_valid, error_msg = validate_password_strength(password_data.new_password)
    if not is_valid:
        await create_audit_log(
            db=db,
            user_id=user.id,
            action="change_password",
            resource_type="user",
            resource_id=user.id,
            details=f"新密码不符合要求: {error_msg}",
            ip_address=ip_address,
            status="failure"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # 更新密码
    new_password_hash = get_password_hash(password_data.new_password)
    password_changed_at = datetime.utcnow()
    password_expires_at = password_changed_at + timedelta(days=90)  # 密码90天后过期
    
    await db.execute(
        update(User)
        .where(User.id == user.id)
        .values(
            password_hash=new_password_hash,
            password_changed_at=password_changed_at,
            password_expires_at=password_expires_at
        )
    )
    await db.commit()
    
    # 记录审计日志
    await create_audit_log(
        db=db,
        user_id=user.id,
        action="change_password",
        resource_type="user",
        resource_id=user.id,
        details="密码修改成功",
        ip_address=ip_address,
        status="success"
    )
    
    return PasswordChangeResponse(
        message="密码修改成功，请使用新密码重新登录",
        password_expires_at=password_expires_at
    )


async def get_user_info(
    db: AsyncSession,
    user: User
) -> UserInfo:
    """
    获取用户信息
    
    Args:
        db: 数据库会话
        user: 当前用户
        
    Returns:
        UserInfo: 用户信息
    """
    # 查询组织信息
    organization = None
    if user.organization_id:
        result = await db.execute(
            select(Organization).where(Organization.id == user.organization_id)
        )
        organization = result.scalar_one_or_none()
    
    return UserInfo(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        organization_id=user.organization_id,
        organization=OrganizationInfo.from_orm(organization) if organization else None,
        status=user.status,
        last_login_at=user.last_login_at,
        password_expires_at=user.password_expires_at,
        created_at=user.created_at
    )
