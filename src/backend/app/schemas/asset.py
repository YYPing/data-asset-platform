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


# ==================== 版本控制相关模型 ====================

class AssetVersionCreate(BaseModel):
    """创建资产版本请求模型"""
    comment: Optional[str] = Field(None, max_length=500, description="版本说明")


class AssetVersionResponse(BaseModel):
    """资产版本响应模型"""
    id: int
    asset_code: str
    asset_name: str
    version: int
    previous_version_id: Optional[int]
    status: str
    current_stage: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AssetVersionListResponse(BaseModel):
    """资产版本列表响应模型"""
    items: List[AssetVersionResponse]
    total: int


# ==================== 搜索相关模型 ====================

class AssetSearchRequest(BaseModel):
    """高级搜索请求模型"""
    keyword: str = Field(..., min_length=1, max_length=200, description="搜索关键词")
    status: Optional[List[str]] = Field(None, description="状态筛选（多选）")
    stage: Optional[List[str]] = Field(None, description="阶段筛选（多选）")
    category: Optional[List[str]] = Field(None, description="分类筛选（多选）")
    organization_id: Optional[int] = Field(None, description="组织ID筛选")
    data_classification: Optional[List[str]] = Field(None, description="数据分类筛选（多选）")
    sensitivity_level: Optional[List[str]] = Field(None, description="敏感级别筛选（多选）")
    created_by: Optional[int] = Field(None, description="创建人ID筛选")
    date_from: Optional[datetime] = Field(None, description="创建日期起始")
    date_to: Optional[datetime] = Field(None, description="创建日期结束")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    use_fulltext: bool = Field(True, description="是否使用全文搜索（中文分词）")


class AssetSearchResponse(BaseModel):
    """搜索结果响应模型"""
    items: List[AssetResponse]
    total: int
    page: int
    page_size: int
    search_time_ms: Optional[float] = Field(None, description="搜索耗时（毫秒）")


# ==================== 状态流转相关模型 ====================

class AssetStatusTransitionRequest(BaseModel):
    """状态流转请求模型"""
    comment: Optional[str] = Field(None, max_length=1000, description="备注/意见")
    reason: Optional[str] = Field(None, max_length=1000, description="原因（驳回/注销时必填）")


class AssetApproveRequest(AssetStatusTransitionRequest):
    """审核通过请求模型"""
    pass


class AssetRejectRequest(BaseModel):
    """审核驳回请求模型"""
    reason: str = Field(..., min_length=1, max_length=1000, description="驳回原因")


class AssetRegisterRequest(AssetStatusTransitionRequest):
    """完成登记请求模型"""
    certificate_no: Optional[str] = Field(None, max_length=100, description="证书编号")


class AssetCancelRequest(BaseModel):
    """注销资产请求模型"""
    reason: str = Field(..., min_length=1, max_length=1000, description="注销原因")


class AssetStatusTransitionResponse(BaseModel):
    """状态流转响应模型"""
    id: int
    asset_code: str
    old_status: str
    new_status: str
    old_stage: Optional[str] = None
    new_stage: Optional[str] = None
    message: str
    timestamp: datetime
