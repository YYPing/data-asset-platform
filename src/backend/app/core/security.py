"""
安全核心模块
提供JWT生成/验证、密码哈希、token黑名单、用户认证依赖
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import redis
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.config import settings
from app.core.database import get_db

# 密码哈希上下文（使用bcrypt）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer认证
security = HTTPBearer()

# Redis连接（用于token黑名单）
# 从REDIS_URL解析或使用mock
try:
    # 尝试从REDIS_URL解析
    if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
        import redis
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    else:
        # 使用mock
        from tests.redis_mock import get_redis_mock
        redis_client = get_redis_mock()
except (ImportError, AttributeError):
    # 如果redis不可用，使用mock
    from tests.redis_mock import get_redis_mock
    redis_client = get_redis_mock()


import hashlib
import secrets

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        bool: 密码是否匹配
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # fallback: sha256方式
        if ':' in hashed_password:
            salt, hash_val = hashed_password.split(':', 1)
            test_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
            return test_hash == hash_val
        return False


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    try:
        return pwd_context.hash(password)
    except Exception:
        # fallback: sha256 + salt
        salt = secrets.token_hex(16)
        hash_val = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}:{hash_val}"


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    验证密码强度
    要求：长度≥8，含大小写+数字+特殊字符
    
    Args:
        password: 待验证的密码
        
    Returns:
        tuple[bool, str]: (是否通过, 错误信息)
    """
    if len(password) < 8:
        return False, "密码长度至少为8位"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for c in password)
    
    if not has_upper:
        return False, "密码必须包含大写字母"
    if not has_lower:
        return False, "密码必须包含小写字母"
    if not has_digit:
        return False, "密码必须包含数字"
    if not has_special:
        return False, "密码必须包含特殊字符"
    
    return True, ""


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌（access_token）
    
    Args:
        data: 要编码的数据（通常包含user_id, username等）
        expires_delta: 过期时间增量，默认2小时
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建刷新令牌（refresh_token）
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量，默认7天
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    解码JWT token
    
    Args:
        token: JWT token字符串
        
    Returns:
        Dict[str, Any]: 解码后的payload
        
    Raises:
        HTTPException: token无效或过期
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证"
        )


def add_token_to_blacklist(token: str, expire_seconds: int = None) -> None:
    """
    将token添加到黑名单（Redis）
    
    Args:
        token: JWT token
        expire_seconds: 过期时间（秒），默认为token剩余有效期
    """
    try:
        payload = decode_token(token)
        exp = payload.get("exp")
        
        if exp:
            # 计算token剩余有效期
            expire_time = datetime.fromtimestamp(exp)
            remaining_seconds = int((expire_time - datetime.utcnow()).total_seconds())
            
            if remaining_seconds > 0:
                # 使用token的jti或完整token作为key
                key = f"blacklist:{token}"
                redis_client.setex(key, remaining_seconds, "1")
    except Exception as e:
        # 记录错误但不抛出异常，避免影响登出流程
        print(f"添加token到黑名单失败: {e}")


def is_token_blacklisted(token: str) -> bool:
    """
    检查token是否在黑名单中
    
    Args:
        token: JWT token
        
    Returns:
        bool: 是否在黑名单中
    """
    try:
        key = f"blacklist:{token}"
        return redis_client.exists(key) > 0
    except Exception as e:
        print(f"检查token黑名单失败: {e}")
        return False


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前认证用户（FastAPI依赖）
    
    Args:
        credentials: HTTP Bearer认证凭证
        db: 数据库会话
        
    Returns:
        User: 当前用户对象
        
    Raises:
        HTTPException: 认证失败
    """
    token = credentials.credentials
    
    # 检查token是否在黑名单中
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已失效，请重新登录"
        )
    
    # 解码token
    try:
        payload = decode_token(token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证"
        )
    
    # 验证token类型
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token类型"
        )
    
    # 获取用户ID
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证"
        )
    
    # 查询用户
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    # 检查用户状态
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 检查账户是否被锁定
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining_minutes = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"账户已被锁定，请在{remaining_minutes}分钟后重试"
        )
    
    # 检查密码是否过期
    if user.password_expires_at and user.password_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="密码已过期，请修改密码"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户（额外的状态检查）
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 当前用户对象
        
    Raises:
        HTTPException: 用户状态异常
    """
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户未激活"
        )
    return current_user


def verify_refresh_token(token: str) -> Dict[str, Any]:
    """
    验证刷新令牌
    
    Args:
        token: refresh_token
        
    Returns:
        Dict[str, Any]: 解码后的payload
        
    Raises:
        HTTPException: token无效或类型错误
    """
    # 检查token是否在黑名单中
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已失效，请重新登录"
        )
    
    payload = decode_token(token)
    
    # 验证token类型
    token_type = payload.get("type")
    if token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的refresh token"
        )
    
    return payload
