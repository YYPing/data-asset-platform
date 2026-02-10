"""
基础Schema类
"""
from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """API响应基类"""
    success: bool = True
    message: str = ""
    data: Optional[T] = None
    code: int = 200
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    message: str
    code: int = 400
    details: Optional[Any] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: list[T]
    total: int
    page: int
    size: int
    pages: int