"""
Material API routes
"""
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.models.asset import Material
from app.schemas.base import ApiResponse
from app.schemas.material import (
    MaterialResponse, MaterialUploadResponse,
    MaterialListResponse, MaterialVerifyResponse, MaterialChecklistResponse
)
from app.services.material import material_service


router = APIRouter(prefix="", tags=["materials"])


@router.post("/upload", response_model=ApiResponse)
async def upload_material(
    file: UploadFile = File(..., description="上传的文件"),
    asset_id: int = Form(..., description="资产ID"),
    material_name: str = Form(..., description="材料名称"),
    material_type: str = Form(..., description="材料类型"),
    stage: str = Form(..., description="所属阶段"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    上传材料文件
    
    - **file**: 文件（支持格式: pdf, jpg, jpeg, png, xlsx, xls, docx, doc）
    - **asset_id**: 关联的数据资产ID
    - **material_name**: 材料名称
    - **material_type**: 材料类型
    - **stage**: 所属阶段（registration/compliance/ownership/confirmation/valuation/accounting）
    
    自动计算SHA256哈希值并存储到MinIO
    """
    try:
        material = await material_service.upload_material(
            db=db,
            file=file,
            asset_id=asset_id,
            material_name=material_name,
            material_type=material_type,
            stage=stage,
            user_id=current_user["id"]
        )
        
        response_data = MaterialUploadResponse(
            id=material.id,
            material_name=material.material_name,
            file_hash=material.file_hash,
            file_size=material.file_size,
            uploaded_at=material.uploaded_at
        )
        
        return ApiResponse(
            code=200,
            message="材料上传成功",
            data=response_data.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/{asset_id}", response_model=ApiResponse)
async def get_materials_by_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取资产的所有材料（按阶段分组）
    
    - **asset_id**: 资产ID
    
    返回按stage分组的材料列表
    """
    try:
        materials = await material_service.get_materials_by_asset(db, asset_id)
        
        return ApiResponse(
            code=200,
            message="获取成功",
            data=[m.model_dump() for m in materials]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/{id}/download")
async def download_material(
    id: int,
    mode: str = "stream",  # stream or presigned
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    下载材料文件
    
    - **id**: 材料ID
    - **mode**: 下载模式
        - stream: 直接流式返回文件内容（默认）
        - presigned: 返回MinIO预签名URL（有效期1小时）
    """
    try:
        material = await material_service.get_material_by_id(db, id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        if mode == "presigned":
            # Return presigned URL
            url = material_service.get_presigned_url(material.file_path)
            return ApiResponse(
                code=200,
                message="获取下载链接成功",
                data={"download_url": url, "expires_in": 3600}
            )
        else:
            # Stream file content
            file_data = await material_service.download_from_minio(material.file_path)
            
            # Determine content type
            content_type_map = {
                'pdf': 'application/pdf',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'xls': 'application/vnd.ms-excel',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'doc': 'application/msword'
            }
            content_type = content_type_map.get(material.file_format, 'application/octet-stream')
            
            # Extract filename from path
            filename = material.file_path.split('/')[-1]
            
            return StreamingResponse(
                iter([file_data]),
                media_type=content_type,
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    'Content-Length': str(len(file_data))
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.get("/{id}/verify", response_model=ApiResponse)
async def verify_material_hash(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    验证材料文件哈希值
    
    - **id**: 材料ID
    
    重新计算文件SHA256哈希值并与存储的值对比，验证文件完整性
    """
    try:
        result = await material_service.verify_material_hash(db, id)
        
        return ApiResponse(
            code=200,
            message=result.message,
            data=result.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")


@router.get("/checklist/{stage}", response_model=ApiResponse)
async def get_stage_checklist(
    stage: str,
    asset_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取阶段材料清单
    
    - **stage**: 阶段名称（registration/compliance/ownership/confirmation/valuation/accounting）
    - **asset_id**: 可选，指定资产ID以查看该资产的上传状态
    
    返回该阶段的必需材料清单及上传状态
    """
    try:
        checklist = await material_service.get_stage_checklist(db, stage, asset_id)
        
        return ApiResponse(
            code=200,
            message="获取清单成功",
            data=checklist.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取清单失败: {str(e)}")


@router.delete("/{id}", response_model=ApiResponse)
async def delete_material(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    删除材料
    
    - **id**: 材料ID
    
    同时删除数据库记录和MinIO中的文件
    """
    try:
        await material_service.delete_material(db, id)
        
        return ApiResponse(
            code=200,
            message="删除成功",
            data={"id": id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
