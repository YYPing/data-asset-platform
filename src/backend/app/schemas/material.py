"""
材料管理相关的 Pydantic 模型
用于请求验证和响应序列化
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

# 导入基础响应类
from app.schemas.base import ApiResponse


# ==================== 基础模型 ====================

class MaterialBase(BaseModel):
    """材料基础模型"""
    material_name: str = Field(..., min_length=1, max_length=200, description="材料名称")
    material_type: Optional[str] = Field(None, max_length=50, description="材料类型")
    stage: str = Field(..., max_length=50, description="所属阶段")
    is_required: bool = Field(default=False, description="是否必需")


class MaterialCreate(MaterialBase):
    """创建材料请求模型"""
    asset_id: int = Field(..., gt=0, description="关联资产ID")
    file_path: Optional[str] = Field(None, max_length=500, description="文件路径")
    file_size: Optional[int] = Field(None, ge=0, description="文件大小（字节）")
    file_format: Optional[str] = Field(None, max_length=20, description="文件格式")
    file_hash: str = Field(..., min_length=64, max_length=64, description="文件哈希（SHA-256）")
    
    @field_validator('stage')
    @classmethod
    def validate_stage(cls, v: str) -> str:
        """验证阶段"""
        allowed_stages = [
            'registration', 'compliance_assessment', 'value_assessment',
            'ownership_confirmation', 'registration_certificate', 'account_entry',
            'operation', 'change_management', 'supervision', 'exit'
        ]
        if v not in allowed_stages:
            raise ValueError(f'阶段必须是以下之一: {", ".join(allowed_stages)}')
        return v


class MaterialUpdate(BaseModel):
    """更新材料请求模型"""
    material_name: Optional[str] = Field(None, min_length=1, max_length=200, description="材料名称")
    material_type: Optional[str] = Field(None, max_length=50, description="材料类型")
    stage: Optional[str] = Field(None, max_length=50, description="所属阶段")
    is_required: Optional[bool] = Field(None, description="是否必需")
    status: Optional[str] = Field(None, description="状态")
    
    @field_validator('stage')
    @classmethod
    def validate_stage(cls, v: Optional[str]) -> Optional[str]:
        """验证阶段"""
        if v is not None:
            allowed_stages = [
                'registration', 'compliance_assessment', 'value_assessment',
                'ownership_confirmation', 'registration_certificate', 'account_entry',
                'operation', 'change_management', 'supervision', 'exit'
            ]
            if v not in allowed_stages:
                raise ValueError(f'阶段必须是以下之一: {", ".join(allowed_stages)}')
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """验证状态"""
        if v is not None:
            allowed_statuses = ['pending', 'approved', 'rejected', 'archived']
            if v not in allowed_statuses:
                raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v


class MaterialResponse(MaterialBase):
    """材料响应模型"""
    id: int
    asset_id: int
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_format: Optional[str] = None
    file_hash: str
    version: int
    status: str
    uploaded_by: Optional[int] = None
    uploaded_at: datetime
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_comment: Optional[str] = None
    
    class Config:
        from_attributes = True


class MaterialListResponse(BaseModel):
    """材料列表响应模型"""
    total: int = Field(..., description="总记录数")
    items: List[MaterialResponse] = Field(..., description="材料列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页记录数")


class MaterialQuery(BaseModel):
    """材料查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页记录数")
    asset_id: Optional[int] = Field(None, description="资产ID筛选")
    stage: Optional[str] = Field(None, description="阶段筛选")
    status: Optional[str] = Field(None, description="状态筛选")
    material_type: Optional[str] = Field(None, description="材料类型筛选")
    keyword: Optional[str] = Field(None, description="搜索关键词（材料名称）")


# ==================== 文件上传相关模型 ====================

class MaterialUploadRequest(BaseModel):
    """材料上传请求模型"""
    asset_id: int = Field(..., gt=0, description="关联资产ID")
    material_name: str = Field(..., min_length=1, max_length=200, description="材料名称")
    material_type: Optional[str] = Field(None, max_length=50, description="材料类型")
    stage: str = Field(..., max_length=50, description="所属阶段")
    is_required: bool = Field(default=False, description="是否必需")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., gt=0, description="文件大小（字节）")
    
    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """验证文件大小"""
        max_size = 1024 * 1024 * 1024  # 1GB
        if v > max_size:
            raise ValueError(f'文件大小不能超过 1GB')
        return v


class MaterialUploadResponse(BaseModel):
    """材料上传响应模型"""
    session_id: str = Field(..., description="上传会话ID")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    total_chunks: int = Field(..., description="总分片数")
    chunk_size: int = Field(..., description="分片大小（字节）")
    bucket_name: str = Field(..., description="存储桶名称")
    object_name: str = Field(..., description="对象名称")


class ChunkUploadRequest(BaseModel):
    """分片上传请求模型"""
    chunk_index: int = Field(..., ge=0, description="分片索引（从0开始）")


class ChunkUploadResponse(BaseModel):
    """分片上传响应模型"""
    session_id: str = Field(..., description="上传会话ID")
    chunk_index: int = Field(..., description="分片索引")
    chunk_hash: str = Field(..., description="分片哈希值")
    uploaded_chunks: int = Field(..., description="已上传分片数")
    total_chunks: int = Field(..., description="总分片数")
    progress: float = Field(..., description="上传进度（0-100）")
    is_complete: bool = Field(..., description="是否完成")


class CompleteUploadRequest(BaseModel):
    """完成上传请求模型"""
    verify_hash: Optional[str] = Field(None, description="验证哈希值（可选）")


class CompleteUploadResponse(BaseModel):
    """完成上传响应模型"""
    material_id: int = Field(..., description="材料ID")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    file_hash: str = Field(..., description="文件哈希值")
    object_name: str = Field(..., description="对象名称")


# ==================== 哈希相关模型 ====================

class MaterialHashRequest(BaseModel):
    """材料哈希请求模型"""
    algorithm: str = Field(default="sha256", description="哈希算法（sha256/md5/sha1）")
    
    @field_validator('algorithm')
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        """验证哈希算法"""
        allowed_algorithms = ['sha256', 'md5', 'sha1']
        if v not in allowed_algorithms:
            raise ValueError(f'哈希算法必须是以下之一: {", ".join(allowed_algorithms)}')
        return v


class MaterialHashResponse(BaseModel):
    """材料哈希响应模型"""
    material_id: int = Field(..., description="材料ID")
    file_hash: str = Field(..., description="文件哈希值")
    algorithm: str = Field(..., description="哈希算法")
    file_size: int = Field(..., description="文件大小（字节）")


class MaterialVerifyRequest(BaseModel):
    """材料验证请求模型"""
    expected_hash: str = Field(..., description="期望的哈希值")
    algorithm: str = Field(default="sha256", description="哈希算法（sha256/md5/sha1）")


class MaterialVerifyResponse(BaseModel):
    """材料验证响应模型"""
    material_id: int = Field(..., description="材料ID")
    is_valid: bool = Field(..., description="是否有效")
    expected_hash: str = Field(..., description="期望的哈希值")
    actual_hash: str = Field(..., description="实际的哈希值")
    algorithm: str = Field(..., description="哈希算法")


# ==================== 版本相关模型 ====================

class MaterialVersionCreate(BaseModel):
    """创建材料版本请求模型"""
    file_hash: str = Field(..., min_length=64, max_length=64, description="新版本文件哈希")
    file_path: Optional[str] = Field(None, max_length=500, description="新版本文件路径")
    file_size: Optional[int] = Field(None, ge=0, description="新版本文件大小")
    change_description: Optional[str] = Field(None, description="变更说明")


class MaterialVersionResponse(BaseModel):
    """材料版本响应模型"""
    id: int
    material_id: int
    version: int
    file_hash: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    change_description: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class MaterialVersionListResponse(BaseModel):
    """材料版本列表响应模型"""
    material_id: int = Field(..., description="材料ID")
    current_version: int = Field(..., description="当前版本号")
    versions: List[MaterialVersionResponse] = Field(..., description="版本历史")


# ==================== 审核相关模型 ====================

class MaterialSubmitRequest(BaseModel):
    """提交审核请求模型"""
    comment: Optional[str] = Field(None, description="提交说明")


class MaterialApproveRequest(BaseModel):
    """审核通过请求模型"""
    comment: Optional[str] = Field(None, description="审核意见")


class MaterialRejectRequest(BaseModel):
    """审核驳回请求模型"""
    comment: str = Field(..., min_length=1, description="驳回原因")


class MaterialReviewResponse(BaseModel):
    """审核响应模型"""
    material_id: int = Field(..., description="材料ID")
    status: str = Field(..., description="审核状态")
    reviewed_by: Optional[int] = Field(None, description="审核人ID")
    reviewed_at: Optional[datetime] = Field(None, description="审核时间")
    review_comment: Optional[str] = Field(None, description="审核意见")


# ==================== 下载相关模型 ====================

class MaterialDownloadResponse(BaseModel):
    """材料下载响应模型"""
    material_id: int = Field(..., description="材料ID")
    file_name: str = Field(..., description="文件名")
    download_url: str = Field(..., description="下载URL（预签名URL）")
    expires_in: int = Field(..., description="URL有效期（秒）")


class MaterialChecklistItem(BaseModel):
    """材料清单项模型"""
    material_name: str = Field(..., description="材料名称")
    material_type: str = Field(..., description="材料类型")
    is_required: bool = Field(..., description="是否必需")
    is_completed: bool = Field(..., description="是否已完成")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class MaterialChecklistResponse(BaseModel):
    """材料清单响应模型"""
    stage: str = Field(..., description="阶段名称")
    items: List[MaterialChecklistItem] = Field(default_factory=list, description="材料清单项列表")
    required_count: int = Field(..., description="必需材料总数")
    completed_count: int = Field(..., description="已完成材料数")
    progress: float = Field(..., description="完成进度（0-1）")
    is_complete: bool = Field(..., description="是否完成")
