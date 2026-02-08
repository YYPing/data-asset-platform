"""
登记证书管理 - 业务逻辑服务
"""
import hashlib
from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from minio import Minio
from minio.error import S3Error
import io

from app.models.asset import RegistrationCertificate, DataAsset
from app.schemas.certificate import CertificateImport, CertificateUpdate, CertificateResponse
from app.config import settings


class CertificateService:
    """证书管理服务"""
    
    # 支持的文件类型
    ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'image/jpeg',
        'image/jpg',
        'image/png'
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.minio_client = self._init_minio()
        self.bucket_name = getattr(settings, 'MINIO_BUCKET_CERTIFICATES', 'certificates')
    
    def _init_minio(self) -> Minio:
        """初始化MinIO客户端"""
        return Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=getattr(settings, 'MINIO_SECURE', False)
        )
    
    async def _ensure_bucket_exists(self):
        """确保存储桶存在"""
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"MinIO错误: {str(e)}")
    
    @staticmethod
    def _calculate_sha256(file_content: bytes) -> str:
        """计算文件SHA256哈希值"""
        return hashlib.sha256(file_content).hexdigest()
    
    @staticmethod
    def _validate_file_type(filename: str, content_type: str) -> bool:
        """验证文件类型"""
        import os
        ext = os.path.splitext(filename)[1].lower()
        return ext in CertificateService.ALLOWED_EXTENSIONS and content_type in CertificateService.ALLOWED_MIME_TYPES
    
    @staticmethod
    def _calculate_status(expiry_date: Optional[date]) -> str:
        """根据有效期计算证书状态"""
        if not expiry_date:
            return "valid"
        
        today = date.today()
        if expiry_date < today:
            return "expired"
        
        days_until_expiry = (expiry_date - today).days
        if days_until_expiry <= 30:
            return "expiring"
        
        return "valid"
    
    async def import_certificate(
        self,
        file: UploadFile,
        cert_data: CertificateImport,
        user_id: int
    ) -> RegistrationCertificate:
        """导入证书"""
        # 验证资产是否存在
        asset_result = await self.db.execute(
            select(DataAsset).where(DataAsset.id == cert_data.asset_id)
        )
        asset = asset_result.scalar_one_or_none()
        if not asset:
            raise HTTPException(status_code=404, detail="资产不存在")
        
        # 验证文件类型
        if not self._validate_file_type(file.filename, file.content_type):
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型。仅支持: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # 读取文件内容
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="文件内容为空")
        
        # 计算SHA256哈希
        file_hash = self._calculate_sha256(file_content)
        
        # 生成文件路径
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        import os
        ext = os.path.splitext(file.filename)[1]
        object_name = f"asset_{cert_data.asset_id}/{timestamp}_{cert_data.certificate_no}{ext}"
        
        # 上传到MinIO
        await self._ensure_bucket_exists()
        try:
            self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=io.BytesIO(file_content),
                length=len(file_content),
                content_type=file.content_type
            )
        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
        
        # 计算状态
        status = self._calculate_status(cert_data.expiry_date)
        
        # 创建数据库记录
        certificate = RegistrationCertificate(
            asset_id=cert_data.asset_id,
            certificate_no=cert_data.certificate_no,
            issuing_authority=cert_data.issuing_authority,
            issue_date=cert_data.issue_date,
            expiry_date=cert_data.expiry_date,
            file_path=object_name,
            file_hash=file_hash,
            status=status,
            imported_by=user_id,
            imported_at=datetime.now(),
            notes=cert_data.notes
        )
        
        self.db.add(certificate)
        await self.db.commit()
        await self.db.refresh(certificate)
        
        return certificate
    
    async def get_certificates_by_asset(self, asset_id: int) -> list[RegistrationCertificate]:
        """查询资产的所有证书"""
        result = await self.db.execute(
            select(RegistrationCertificate)
            .where(RegistrationCertificate.asset_id == asset_id)
            .where(RegistrationCertificate.status != "revoked")
            .order_by(RegistrationCertificate.imported_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_certificate_by_id(self, cert_id: int) -> Optional[RegistrationCertificate]:
        """根据ID获取证书"""
        result = await self.db.execute(
            select(RegistrationCertificate).where(RegistrationCertificate.id == cert_id)
        )
        return result.scalar_one_or_none()
    
    async def verify_certificate(self, cert_id: int) -> dict:
        """验证证书哈希（防篡改校验）"""
        certificate = await self.get_certificate_by_id(cert_id)
        if not certificate:
            raise HTTPException(status_code=404, detail="证书不存在")
        
        # 从MinIO下载文件
        try:
            response = self.minio_client.get_object(
                bucket_name=self.bucket_name,
                object_name=certificate.file_path
            )
            file_content = response.read()
            response.close()
            response.release_conn()
        except S3Error as e:
            return {
                "is_valid": False,
                "stored_hash": certificate.file_hash,
                "current_hash": None,
                "message": f"无法读取文件: {str(e)}"
            }
        
        # 计算当前哈希
        current_hash = self._calculate_sha256(file_content)
        
        # 比对哈希值
        is_valid = current_hash == certificate.file_hash
        
        return {
            "is_valid": is_valid,
            "stored_hash": certificate.file_hash,
            "current_hash": current_hash,
            "message": "证书完整性验证通过" if is_valid else "警告：证书文件已被篡改！"
        }
    
    async def update_certificate(
        self,
        cert_id: int,
        update_data: CertificateUpdate
    ) -> RegistrationCertificate:
        """更新证书信息"""
        certificate = await self.get_certificate_by_id(cert_id)
        if not certificate:
            raise HTTPException(status_code=404, detail="证书不存在")
        
        # 更新字段
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # 如果更新了有效期，重新计算状态
        if "expiry_date" in update_dict and "status" not in update_dict:
            update_dict["status"] = self._calculate_status(update_dict["expiry_date"])
        
        for field, value in update_dict.items():
            setattr(certificate, field, value)
        
        await self.db.commit()
        await self.db.refresh(certificate)
        
        return certificate
    
    async def get_expiring_certificates(
        self,
        days: int = 30,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[list[RegistrationCertificate], int]:
        """获取即将过期的证书列表"""
        today = date.today()
        expiry_threshold = today + timedelta(days=days)
        
        # 查询条件：有效期在今天到阈值之间，且状态不是revoked
        query = select(RegistrationCertificate).where(
            and_(
                RegistrationCertificate.expiry_date.isnot(None),
                RegistrationCertificate.expiry_date >= today,
                RegistrationCertificate.expiry_date <= expiry_threshold,
                RegistrationCertificate.status != "revoked"
            )
        ).order_by(RegistrationCertificate.expiry_date.asc())
        
        # 计算总数
        from sqlalchemy import func
        count_query = select(func.count()).select_from(RegistrationCertificate).where(
            and_(
                RegistrationCertificate.expiry_date.isnot(None),
                RegistrationCertificate.expiry_date >= today,
                RegistrationCertificate.expiry_date <= expiry_threshold,
                RegistrationCertificate.status != "revoked"
            )
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        certificates = list(result.scalars().all())
        
        return certificates, total
    
    async def delete_certificate(self, cert_id: int) -> RegistrationCertificate:
        """删除证书（软删除）"""
        certificate = await self.get_certificate_by_id(cert_id)
        if not certificate:
            raise HTTPException(status_code=404, detail="证书不存在")
        
        certificate.status = "revoked"
        await self.db.commit()
        await self.db.refresh(certificate)
        
        return certificate
    
    @staticmethod
    def enrich_certificate_response(cert: RegistrationCertificate) -> dict:
        """丰富证书响应数据（添加距离过期天数）"""
        cert_dict = {
            "id": cert.id,
            "asset_id": cert.asset_id,
            "certificate_no": cert.certificate_no,
            "issuing_authority": cert.issuing_authority,
            "issue_date": cert.issue_date,
            "expiry_date": cert.expiry_date,
            "file_path": cert.file_path,
            "file_hash": cert.file_hash,
            "status": cert.status,
            "imported_by": cert.imported_by,
            "imported_at": cert.imported_at,
            "notes": cert.notes,
            "days_until_expiry": None
        }
        
        if cert.expiry_date:
            days_until_expiry = (cert.expiry_date - date.today()).days
            cert_dict["days_until_expiry"] = days_until_expiry
        
        return cert_dict
