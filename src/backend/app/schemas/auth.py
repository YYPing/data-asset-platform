"""
认证相关的Pydantic模型
包括登录请求/响应、Token、用户信息等
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, description="密码")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "Admin@123"
            }
        }


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="访问令牌过期时间（秒）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 7200
            }
        }


class RefreshTokenRequest(BaseModel):
    """刷新Token请求"""
    refresh_token: str = Field(..., description="刷新令牌")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=1, description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码")
    confirm_password: str = Field(..., min_length=8, description="确认新密码")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """验证两次密码输入是否一致"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v
    
    @validator('new_password')
    def password_not_same_as_old(cls, v, values):
        """验证新密码不能与旧密码相同"""
        if 'old_password' in values and v == values['old_password']:
            raise ValueError('新密码不能与旧密码相同')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "OldPass@123",
                "new_password": "NewPass@456",
                "confirm_password": "NewPass@456"
            }
        }


class OrganizationInfo(BaseModel):
    """组织信息"""
    id: int = Field(..., description="组织ID")
    name: str = Field(..., description="组织名称")
    code: Optional[str] = Field(None, description="组织代码")
    type: Optional[str] = Field(None, description="组织类型")
    level: Optional[int] = Field(None, description="组织层级")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "市数据资产管理中心",
                "code": "CENTER001",
                "type": "center",
                "level": 1
            }
        }


class UserInfo(BaseModel):
    """用户信息"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    real_name: Optional[str] = Field(None, description="真实姓名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    role: str = Field(..., description="角色")
    organization_id: Optional[int] = Field(None, description="组织ID")
    organization: Optional[OrganizationInfo] = Field(None, description="组织信息")
    status: str = Field(..., description="状态")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    password_expires_at: Optional[datetime] = Field(None, description="密码过期时间")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "admin",
                "real_name": "系统管理员",
                "email": "admin@example.com",
                "phone": "13800138000",
                "role": "sys_admin",
                "organization_id": 1,
                "organization": {
                    "id": 1,
                    "name": "市数据资产管理中心",
                    "code": "CENTER001",
                    "type": "center",
                    "level": 1
                },
                "status": "active",
                "last_login_at": "2024-01-15T10:30:00",
                "password_expires_at": "2024-04-15T10:30:00",
                "created_at": "2024-01-01T00:00:00"
            }
        }


class LoginResponse(BaseModel):
    """登录响应（包含用户信息和Token）"""
    user: UserInfo = Field(..., description="用户信息")
    token: TokenResponse = Field(..., description="认证令牌")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": 1,
                    "username": "admin",
                    "real_name": "系统管理员",
                    "role": "sys_admin",
                    "status": "active"
                },
                "token": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 7200
                }
            }
        }


class PasswordChangeResponse(BaseModel):
    """修改密码响应"""
    message: str = Field(default="密码修改成功", description="响应消息")
    password_expires_at: Optional[datetime] = Field(None, description="新密码过期时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "密码修改成功",
                "password_expires_at": "2024-04-15T10:30:00"
            }
        }


class LogoutResponse(BaseModel):
    """登出响应"""
    message: str = Field(default="登出成功", description="响应消息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "登出成功"
            }
        }


class TokenPayload(BaseModel):
    """Token载荷（用于内部解析）"""
    user_id: int
    username: str
    role: str
    type: str  # access 或 refresh
    exp: int  # 过期时间戳
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "username": "admin",
                "role": "sys_admin",
                "type": "access",
                "exp": 1705315200
            }
        }
