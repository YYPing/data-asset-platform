"""
Material service - Business logic for material management
"""
import hashlib
import os
from datetime import datetime
from typing import List, Optional, Dict, BinaryIO
from io import BytesIO

from fastapi import UploadFile, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from minio import Minio
from minio.error import S3Error

from app.models.asset import Material, DataAsset
from app.schemas.material import (
    MaterialCreate, MaterialResponse, MaterialListResponse,
    MaterialVerifyResponse, MaterialChecklistItem, MaterialChecklistResponse
)
from app.config import settings


# 文件格式白名单
ALLOWED_FORMATS = {'pdf', 'jpg', 'jpeg', 'png', 'xlsx', 'xls', 'docx', 'doc'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# 各阶段必需材料清单
STAGE_REQUIRED_MATERIALS = {
    'registration': [
        '数据情况说明书',
        '数据质量报告',
        '合规报告',
        '外部登记证书',
        '营业执照/组织代码'
    ],
    'compliance': [
        '数据情况说明书',
        '数据质量报告',
        '数据安全评估报告',
        '个人信息保护影响评估',
        '合规自查表'
    ],
    'ownership': [
        '数据情况说明书',
        '数据来源协议',
        '采集授权书',
        '加工记录',
        '权属声明'
    ],
    'confirmation': [
        '数据情况说明书',
        '登记申请表',
        '权属证明材料汇总',
        '确权登记证书'
    ],
    'valuation': [
        '数据情况说明书',
        '数据质量报告',
        '评估委托书',
        '第三方评估报告',
        '评估方法说明'
    ],
    'accounting': [
        '数据情况说明书',
        '数据质量报告',
        '会计处理方案',
        '入表类型判断依据',
        '财务审批单'
    ]
}


class MaterialService:
    """Material service class"""
    
    def __init__(self):
        """Initialize MinIO client"""
        self.minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        self.bucket_name = settings.MINIO_BUCKET
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Ensure MinIO bucket exists"""
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"MinIO bucket error: {e}")
    
    @staticmethod
    async def calculate_file_hash(file: UploadFile) -> str:
        """
        Calculate SHA256 hash of uploaded file
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            SHA256 hash string
        """
        sha256_hash = hashlib.sha256()
        
        # Read file in chunks to handle large files
        await file.seek(0)
        while chunk := await file.read(8192):
            sha256_hash.update(chunk)
        
        # Reset file pointer
        await file.seek(0)
        
        return sha256_hash.hexdigest()
    
    @staticmethod
    def validate_file_format(filename: str) -> str:
        """
        Validate file format against whitelist
        
        Args:
            filename: Original filename
            
        Returns:
            File extension (lowercase)
            
        Raises:
            HTTPException: If format not allowed
        """
        file_ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        
        if file_ext not in ALLOWED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"文件格式不支持。允许的格式: {', '.join(ALLOWED_FORMATS)}"
            )
        
        return file_ext
    
    @staticmethod
    def validate_file_size(file_size: int):
        """
        Validate file size
        
        Args:
            file_size: File size in bytes
            
        Raises:
            HTTPException: If file too large
        """
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制。最大允许: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )
    
    async def upload_to_minio(
        self,
        file: UploadFile,
        object_name: str
    ) -> str:
        """
        Upload file to MinIO
        
        Args:
            file: FastAPI UploadFile object
            object_name: Object name in MinIO (path)
            
        Returns:
            Object name (path) in MinIO
            
        Raises:
            HTTPException: If upload fails
        """
        try:
            # Get file size
            await file.seek(0, 2)  # Seek to end
            file_size = await file.tell()
            await file.seek(0)  # Reset to beginning
            
            # Read file content
            file_data = await file.read()
            file_stream = BytesIO(file_data)
            
            # Upload to MinIO
            self.minio_client.put_object(
                self.bucket_name,
                object_name,
                file_stream,
                length=file_size,
                content_type=file.content_type or 'application/octet-stream'
            )
            
            # Reset file pointer for potential reuse
            await file.seek(0)
            
            return object_name
            
        except S3Error as e:
            raise HTTPException(
                status_code=500,
                detail=f"MinIO上传失败: {str(e)}"
            )
    
    async def download_from_minio(self, object_name: str) -> bytes:
        """
        Download file from MinIO
        
        Args:
            object_name: Object name in MinIO
            
        Returns:
            File content as bytes
            
        Raises:
            HTTPException: If download fails
        """
        try:
            response = self.minio_client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            raise HTTPException(
                status_code=404,
                detail=f"文件下载失败: {str(e)}"
            )
    
    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        """
        Get presigned download URL from MinIO
        
        Args:
            object_name: Object name in MinIO
            expires: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Presigned URL
        """
        try:
            from datetime import timedelta
            url = self.minio_client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            raise HTTPException(
                status_code=500,
                detail=f"生成下载链接失败: {str(e)}"
            )
    
    async def delete_from_minio(self, object_name: str):
        """
        Delete file from MinIO
        
        Args:
            object_name: Object name in MinIO
            
        Raises:
            HTTPException: If deletion fails
        """
        try:
            self.minio_client.remove_object(self.bucket_name, object_name)
        except S3Error as e:
            raise HTTPException(
                status_code=500,
                detail=f"MinIO删除失败: {str(e)}"
            )
    
    async def upload_material(
        self,
        db: AsyncSession,
        file: UploadFile,
        asset_id: int,
        material_name: str,
        material_type: str,
        stage: str,
        user_id: int
    ) -> Material:
        """
        Upload material with validation and hash calculation
        
        Args:
            db: Database session
            file: Uploaded file
            asset_id: Asset ID
            material_name: Material name
            material_type: Material type
            stage: Stage name
            user_id: Current user ID
            
        Returns:
            Created Material object
            
        Raises:
            HTTPException: If validation fails or asset not found
        """
        # Verify asset exists
        result = await db.execute(
            select(DataAsset).where(DataAsset.id == asset_id)
        )
        asset = result.scalar_one_or_none()
        if not asset:
            raise HTTPException(status_code=404, detail="资产不存在")
        
        # Validate file format
        file_format = self.validate_file_format(file.filename)
        
        # Get file size
        await file.seek(0, 2)
        file_size = await file.tell()
        await file.seek(0)
        
        # Validate file size
        self.validate_file_size(file_size)
        
        # Calculate file hash
        file_hash = await self.calculate_file_hash(file)
        
        # Generate MinIO object path: {asset_id}/{stage}/{filename}
        safe_filename = file.filename.replace(' ', '_')
        object_name = f"{asset_id}/{stage}/{safe_filename}"
        
        # Upload to MinIO
        file_path = await self.upload_to_minio(file, object_name)
        
        # Check if material is required
        is_required = material_name in STAGE_REQUIRED_MATERIALS.get(stage, [])
        
        # Get latest version for this material
        version_result = await db.execute(
            select(Material.version)
            .where(
                and_(
                    Material.asset_id == asset_id,
                    Material.material_name == material_name,
                    Material.stage == stage
                )
            )
            .order_by(Material.version.desc())
            .limit(1)
        )
        latest_version = version_result.scalar_one_or_none()
        version = (latest_version or 0) + 1
        
        # Create material record
        material = Material(
            asset_id=asset_id,
            material_name=material_name,
            material_type=material_type,
            stage=stage,
            file_path=file_path,
            file_size=file_size,
            file_format=file_format,
            file_hash=file_hash,
            version=version,
            is_required=is_required,
            status='pending',
            uploaded_by=user_id,
            uploaded_at=datetime.utcnow()
        )
        
        db.add(material)
        await db.commit()
        await db.refresh(material)
        
        return material
    
    async def get_materials_by_asset(
        self,
        db: AsyncSession,
        asset_id: int
    ) -> List[MaterialListResponse]:
        """
        Get all materials for an asset, grouped by stage
        
        Args:
            db: Database session
            asset_id: Asset ID
            
        Returns:
            List of materials grouped by stage
        """
        result = await db.execute(
            select(Material)
            .where(Material.asset_id == asset_id)
            .order_by(Material.stage, Material.uploaded_at.desc())
        )
        materials = result.scalars().all()
        
        # Group by stage
        grouped: Dict[str, List[Material]] = {}
        for material in materials:
            if material.stage not in grouped:
                grouped[material.stage] = []
            grouped[material.stage].append(material)
        
        # Convert to response format
        response = [
            MaterialListResponse(
                stage=stage,
                materials=[MaterialResponse.model_validate(m) for m in mats]
            )
            for stage, mats in grouped.items()
        ]
        
        return response
    
    async def get_material_by_id(
        self,
        db: AsyncSession,
        material_id: int
    ) -> Optional[Material]:
        """
        Get material by ID
        
        Args:
            db: Database session
            material_id: Material ID
            
        Returns:
            Material object or None
        """
        result = await db.execute(
            select(Material).where(Material.id == material_id)
        )
        return result.scalar_one_or_none()
    
    async def verify_material_hash(
        self,
        db: AsyncSession,
        material_id: int
    ) -> MaterialVerifyResponse:
        """
        Verify material file hash
        
        Args:
            db: Database session
            material_id: Material ID
            
        Returns:
            Verification result
            
        Raises:
            HTTPException: If material not found
        """
        material = await self.get_material_by_id(db, material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        # Download file from MinIO
        file_data = await self.download_from_minio(material.file_path)
        
        # Calculate hash
        calculated_hash = hashlib.sha256(file_data).hexdigest()
        
        is_valid = calculated_hash == material.file_hash
        
        return MaterialVerifyResponse(
            material_id=material_id,
            stored_hash=material.file_hash,
            calculated_hash=calculated_hash,
            is_valid=is_valid,
            message="哈希验证通过" if is_valid else "哈希验证失败，文件可能已被篡改"
        )
    
    async def get_stage_checklist(
        self,
        db: AsyncSession,
        stage: str,
        asset_id: Optional[int] = None
    ) -> MaterialChecklistResponse:
        """
        Get material checklist for a stage
        
        Args:
            db: Database session
            stage: Stage name
            asset_id: Optional asset ID to check upload status
            
        Returns:
            Checklist with upload status
            
        Raises:
            HTTPException: If stage invalid
        """
        if stage not in STAGE_REQUIRED_MATERIALS:
            raise HTTPException(status_code=400, detail="无效的阶段")
        
        required_materials = STAGE_REQUIRED_MATERIALS[stage]
        
        # Get uploaded materials for this stage and asset
        uploaded_materials = {}
        if asset_id:
            result = await db.execute(
                select(Material)
                .where(
                    and_(
                        Material.asset_id == asset_id,
                        Material.stage == stage
                    )
                )
                .order_by(Material.uploaded_at.desc())
            )
            materials = result.scalars().all()
            
            # Group by material name
            for material in materials:
                if material.material_name not in uploaded_materials:
                    uploaded_materials[material.material_name] = []
                uploaded_materials[material.material_name].append(material)
        
        # Build checklist items
        items = []
        uploaded_required_count = 0
        
        for material_name in required_materials:
            uploaded_list = uploaded_materials.get(material_name, [])
            is_uploaded = len(uploaded_list) > 0
            
            if is_uploaded:
                uploaded_required_count += 1
            
            items.append(MaterialChecklistItem(
                material_name=material_name,
                is_required=True,
                is_uploaded=is_uploaded,
                uploaded_count=len(uploaded_list),
                latest_upload=MaterialResponse.model_validate(uploaded_list[0]) if uploaded_list else None
            ))
        
        completion_rate = (uploaded_required_count / len(required_materials) * 100) if required_materials else 100.0
        
        return MaterialChecklistResponse(
            stage=stage,
            total_required=len(required_materials),
            uploaded_required=uploaded_required_count,
            completion_rate=round(completion_rate, 2),
            items=items
        )
    
    async def delete_material(
        self,
        db: AsyncSession,
        material_id: int
    ):
        """
        Delete material
        
        Args:
            db: Database session
            material_id: Material ID
            
        Raises:
            HTTPException: If material not found
        """
        material = await self.get_material_by_id(db, material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        # Delete from MinIO
        await self.delete_from_minio(material.file_path)
        
        # Delete from database
        await db.delete(material)
        await db.commit()


# Singleton instance
material_service = MaterialService()
