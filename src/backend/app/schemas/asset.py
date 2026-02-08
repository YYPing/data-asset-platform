"""
数据资产 Pydantic 模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class AssetBase(BaseModel):
    """资产基础模型"""
    asset_name: str = Field(..., min_length=1, max_length=200, description="资产名称")
    organization_id: int = Field(..., description="所属组织ID")
    category: Optional[str] = Field(None, max_length=100, description="资产分类")
    data_classification: Optional[str] = Field(None, max_length=50, description="数据分类")
    sensitivity_level: Optional[str] = Field(None, max_length=50, description="敏感级别")
    description: Optional[str] = Field(None, description="资产描述")
    data_source: Optional[str] = Field(None, max_length=200, description="数据来源")
    data_volume: Optional[str] = Field(None, max_length=100, description="数据量")
    data_format: Optional[str] = Field(None, max_length=100, description="数据格式")
    update_frequency: Optional[str] = Field(None, max_length=100, description="更新频率")
    asset_type: Optional[str] = Field(None, max_length=100, description="资产类型")
    estimated_value: Optional[float] = Field(None, ge=0, description="估值")
    assigned_to: Optional[int] = Field(None, description="分配给用户ID")


class AssetCreate(AssetBase):
    """创建资产请求模型"""
    pass


class AssetUpdate(BaseModel):
    """更新资产请求模型（所有字段可选）"""
    asset_name: Optional[str] = Field(None, min_length=1, max_length=200, description="资产名称")
    organization_id: Optional[int] = Field(None, description="所属组织ID")
    category: Optional[str] = Field(None, max_length=100, description="资产分类")
    data_classification: Optional[str] = Field(None, max_length=50, description="数据分类")
    sensitivity_level: Optional[str] = Field(None, max_length=50, description="敏感级别")
    description: Optional[str] = Field(None, description="资产描述")
    data_source: Optional[str] = Field(None, max_length=200, description="数据来源")
    data_volume: Optional[str] = Field(None, max_length=100, description="数据量")
    data_format: Optional[str] = Field(None, max_length=100, description="数据格式")
    update_frequency: Optional[str] = Field(None, max_length=100, description="更新频率")
    asset_type: Optional[str] = Field(None, max_length=100, description="资产类型")
    estimated_value: Optional[float] = Field(None, ge=0, description="估值")
    assigned_to: Optional[int] = Field(None, description="分配给用户ID")


class AssetResponse(AssetBase):
    """资产响应模型"""
    id: int
    asset_code: str
    status: str
    current_stage: str
    created_by: int
    version: int
    previous_version_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class AssetListResponse(BaseModel):
    """资产列表响应模型"""
    items: List[AssetResponse]
    total: int
    page: int
    page_size: int


class SearchParams(BaseModel):
    """搜索参数模型"""
    q: Optional[str] = Field(None, description="搜索关键词")
    status: Optional[str] = Field(None, description="状态筛选")
    stage: Optional[str] = Field(None, description="阶段筛选")
    org_id: Optional[int] = Field(None, description="组织ID筛选")
    category: Optional[str] = Field(None, description="分类筛选")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class AssetSubmitResponse(BaseModel):
    """提交审批响应模型"""
    id: int
    asset_code: str
    status: str
    message: str
