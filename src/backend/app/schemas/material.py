"""
Material schemas for data asset platform
"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict


class MaterialBase(BaseModel):
    """Base material schema"""
    material_name: str = Field(..., description="材料名称")
    material_type: str = Field(..., description="材料类型")
    stage: str = Field(..., description="所属阶段")
    is_required: bool = Field(default=False, description="是否必需")


class MaterialCreate(MaterialBase):
    """Material creation schema"""
    asset_id: int = Field(..., description="关联资产ID")
    file_path: str = Field(..., description="文件路径")
    file_size: int = Field(..., description="文件大小(字节)")
    file_format: str = Field(..., description="文件格式")
    file_hash: str = Field(..., description="文件SHA256哈希")
    version: int = Field(default=1, description="版本号")
    uploaded_by: int = Field(..., description="上传人ID")


class MaterialUpdate(BaseModel):
    """Material update schema"""
    material_name: Optional[str] = None
    material_type: Optional[str] = None
    status: Optional[str] = None
    review_comment: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MaterialResponse(MaterialBase):
    """Material response schema"""
    id: int
    asset_id: int
    file_path: str
    file_size: int
    file_format: str
    file_hash: str
    version: int
    status: str
    uploaded_by: int
    uploaded_at: datetime
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MaterialListResponse(BaseModel):
    """Material list grouped by stage"""
    stage: str
    materials: List[MaterialResponse]


class MaterialUploadResponse(BaseModel):
    """Material upload response"""
    id: int
    material_name: str
    file_hash: str
    file_size: int
    uploaded_at: datetime


class MaterialVerifyResponse(BaseModel):
    """Material hash verification response"""
    material_id: int
    stored_hash: str
    calculated_hash: str
    is_valid: bool
    message: str


class MaterialChecklistItem(BaseModel):
    """Material checklist item"""
    material_name: str
    is_required: bool
    is_uploaded: bool
    uploaded_count: int = 0
    latest_upload: Optional[MaterialResponse] = None


class MaterialChecklistResponse(BaseModel):
    """Material checklist response"""
    stage: str
    total_required: int
    uploaded_required: int
    completion_rate: float
    items: List[MaterialChecklistItem]


class ApiResponse(BaseModel):
    """Unified API response"""
    code: int = 200
    message: str = "success"
    data: Optional[Dict | List | MaterialResponse | MaterialUploadResponse | 
                   MaterialVerifyResponse | MaterialChecklistResponse | 
                   List[MaterialListResponse]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
