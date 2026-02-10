"""
材料服务 - 修复版本（支持禁用MinIO）
"""
import os
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any, BinaryIO
from uuid import uuid4

from minio import Minio
from minio.error import S3Error
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import joinedload

from app.models.asset import Material, DataAsset
from app.schemas.material import (
    MaterialCreate, MaterialResponse, MaterialListResponse,
    MaterialVerifyResponse, MaterialChecklistItem, MaterialChecklistResponse
)
from app.config import settings
from app.core.security import get_password_hash


class MaterialService:
    """材料管理服务"""
    
    def __init__(self):
        """Initialize MaterialService"""
        if getattr(settings, 'MINIO_ENABLED', False):
            self.minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=False
            )
            self.bucket_name = settings.MINIO_BUCKET
            self._ensure_bucket()
        else:
            self.minio_client = None
            self.bucket_name = "mock-bucket"
            print("⚠️  MinIO disabled, using mock storage")
    
    def _ensure_bucket(self):
        """Ensure MinIO bucket exists"""
        if not getattr(settings, 'MINIO_ENABLED', False) or self.minio_client is None:
            return
            
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"MinIO bucket error: {e}")
    
    # 其他方法保持不变，但需要检查minio_client是否为None
    def upload_file(self, file_data: BinaryIO, file_name: str, content_type: str = "application/octet-stream") -> str:
        """上传文件到存储"""
        if self.minio_client is None:
            # 模拟上传，返回mock对象ID
            object_name = f"mock/{uuid4().hex}/{file_name}"
            print(f"Mock upload: {object_name}")
            return object_name
        
        object_name = f"{datetime.now().strftime('%Y/%m/%d')}/{uuid4().hex}/{file_name}"
        
        try:
            file_size = os.fstat(file_data.fileno()).st_size
            self.minio_client.put_object(
                self.bucket_name,
                object_name,
                file_data,
                file_size,
                content_type=content_type
            )
            return object_name
        except S3Error as e:
            print(f"MinIO upload error: {e}")
            raise
    
    def get_file_url(self, object_name: str, expires_seconds: int = 3600) -> str:
        """获取文件访问URL"""
        if self.minio_client is None:
            return f"mock://{self.bucket_name}/{object_name}"
        
        try:
            return self.minio_client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires_seconds
            )
        except S3Error as e:
            print(f"MinIO URL error: {e}")
            return ""
    
    # 其他方法也需要类似处理...


# 创建服务实例
material_service = MaterialService()