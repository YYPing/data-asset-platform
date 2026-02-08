"""
User schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    role: str = Field(..., description="角色: admin/asset_manager/evaluator/viewer")
    organization_id: Optional[int] = Field(None, description="所属机构ID")
    status: str = Field(default="active", description="状态: active/inactive/locked")


class UserCreate(UserBase):
    """Create user schema"""
    password: str = Field(..., min_length=8, max_length=50, description="密码")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role"""
        allowed_roles = ['admin', 'asset_manager', 'evaluator', 'viewer']
        if v not in allowed_roles:
            raise ValueError(f'角色必须是以下之一: {", ".join(allowed_roles)}')
        return v


class UserUpdate(BaseModel):
    """Update user schema"""
    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    role: Optional[str] = Field(None, description="角色")
    organization_id: Optional[int] = Field(None, description="所属机构ID")
    status: Optional[str] = Field(None, description="状态")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        """Validate role"""
        if v is not None:
            allowed_roles = ['admin', 'asset_manager', 'evaluator', 'viewer']
            if v not in allowed_roles:
                raise ValueError(f'角色必须是以下之一: {", ".join(allowed_roles)}')
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status"""
        if v is not None:
            allowed_statuses = ['active', 'inactive', 'locked']
            if v not in allowed_statuses:
                raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v


class UserResponse(UserBase):
    """User response schema"""
    id: int
    password_changed_at: datetime
    password_expires_at: Optional[datetime] = None
    failed_login_count: int
    locked_until: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """User list response schema"""
    total: int = Field(..., description="总记录数")
    items: list[UserResponse] = Field(..., description="用户列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页记录数")


class UserResetPasswordResponse(BaseModel):
    """Reset password response schema"""
    message: str = Field(..., description="提示信息")
    new_password: str = Field(..., description="新密码")


class UserQuery(BaseModel):
    """User query parameters"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页记录数")
    keyword: Optional[str] = Field(None, description="搜索关键词（用户名/姓名/邮箱/手机号）")
    role: Optional[str] = Field(None, description="角色筛选")
    status: Optional[str] = Field(None, description="状态筛选")
    organization_id: Optional[int] = Field(None, description="机构ID筛选")
