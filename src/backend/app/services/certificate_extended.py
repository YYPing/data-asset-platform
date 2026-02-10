"""
证书管理服务 - 扩展版
包含完整的证书管理功能：导入、解析、验证、关联、提醒等
"""
import io
import hashlib
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from fastapi import UploadFile, HTTPException
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from minio import Minio
from minio.error import S3Error

from app.models.certificate import (
    Certificate, CertificateFile, CertificateAsset, 
    CertificateValidation, ExpiryAlert,
    CertificateType, CertificateStatus, FileFormat,
    ValidationStatus, AlertType, AlertMethod
)
from app.models.asset import DataAsset
from app.schemas.certificate import (
    CertificateCreate, CertificateUpdate, CertificateImportRequest,
    CertificateAssociateRequest, CertificateRenewalRequest,
    CertificateQueryParams
)
from app.config import settings
from app.utils.ocr_processor import get_ocr_processor
from app.utils.certificate_parser import get_certificate_parser
from app.utils.expiry_manager import get_expiry_manager
from app.utils.certificate_validator import get_certificate_validator
from app.utils.file_hash import calculate_bytes_hash


class CertificateExtendedService:
    """证书管理扩展服务"""
    
    # 支持的文件类型
    ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.xlsx', '.xls'}
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'image/jpeg',
        'image/jpg',
        'image/png',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
    }
    
    def __init__(self, db: AsyncSession):
        """初始化服务"""
        self.db = db
        self.minio_client = self._init_minio()
        self.bucket_name = getattr(settings, 'MINIO_BUCKET_CERTIFICATES', 'certificates')
        self.ocr_processor = get_ocr_processor()
        self.parser = get_certificate_parser()
        self.expiry_manager = get_expiry_manager()
        self.validator = get_certificate_validator()
    
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
    def _validate_file_type(filename: str, content_type: str) -> bool:
        """验证文件类型"""
        import os
        ext = os.path.splitext(filename)[1].lower()
        return ext in CertificateExtendedService.ALLOWED_EXTENSIONS and \
               content_type in CertificateExtendedService.ALLOWED_MIME_TYPES
    
    async def import_certificate_with_parsing(
        self,
        file: UploadFile,
        user_id: int,
        auto_parse: bool = True
    ) -> Tuple[Certificate, Dict[str, Any]]:
        """
        导入证书并自动解析
        
        Args:
            file: 上传的文件
            user_id: 用户ID
            auto_parse: 是否自动解析证书内容
            
        Returns:
            tuple: (证书对象, 解析信息)
        """
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
        
        # 计算文件哈希
        file_hash = calculate_bytes_hash(file_content, 'sha256')
        
        # 解析证书信息（如果启用）
        parsed_info = {}
        if auto_parse:
            import os
            file_format = os.path.splitext(file.filename)[1].lower().replace('.', '')
            try:
                parsed_info = self.parser.parse_from_file(file_content, file_format, file.filename)
            except Exception as e:
                # 解析失败不影响导入，只记录错误
                parsed_info = {'parse_error': str(e)}
        
        # 生成证书编号（如果解析失败）
        cert_no = parsed_info.get('certificate_no')
        if not cert_no:
            cert_no = f"CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 创建证书记录
        certificate = Certificate(
            certificate_no=cert_no,
            certificate_type=CertificateType.REGISTRATION,
            certificate_name=parsed_info.get('certificate_name'),
            issuing_authority=parsed_info.get('issuing_authority', '未知'),
            issue_date=parsed_info.get('issue_date', date.today()),
            expiry_date=parsed_info.get('expiry_date'),
            holder_name=parsed_info.get('holder_name'),
            holder_id_number=parsed_info.get('id_number'),
            status=self._calculate_status(parsed_info.get('expiry_date')),
            imported_by=user_id,
            imported_at=datetime.now(),
            notes=parsed_info.get('notes'),
        )
        
        self.db.add(certificate)
        await self.db.flush()  # 获取证书ID
        
        # 上传文件到MinIO
        await self._ensure_bucket_exists()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        import os
        ext = os.path.splitext(file.filename)[1]
        object_name = f"cert_{certificate.id}/{timestamp}_{file.filename}"
        
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
        
        # 创建文件记录
        cert_file = CertificateFile(
            certificate_id=certificate.id,
            file_name=file.filename,
            file_path=object_name,
            file_size=len(file_content),
            file_format=FileFormat(ext.replace('.', '').lower()),
            file_hash=file_hash,
            mime_type=file.content_type,
            is_primary=True,
            uploaded_by=user_id,
        )
        
        self.db.add(cert_file)
        
        # 生成缩略图（异步处理）
        try:
            thumbnail_data = self.ocr_processor.generate_thumbnail(
                file_content,
                ext.replace('.', '').lower()
            )
            if thumbnail_data:
                thumbnail_name = f"cert_{certificate.id}/thumbnail_{timestamp}.jpg"
                self.minio_client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=thumbnail_name,
                    data=io.BytesIO(thumbnail_data),
                    length=len(thumbnail_data),
                    content_type='image/jpeg'
                )
                cert_file.thumbnail_path = thumbnail_name
        except Exception as e:
            # 缩略图生成失败不影响主流程
            print(f"缩略图生成失败: {e}")
        
        await self.db.commit()
        await self.db.refresh(certificate)
        
        return certificate, parsed_info
    
    @staticmethod
    def _calculate_status(expiry_date: Optional[date]) -> CertificateStatus:
        """根据有效期计算证书状态"""
        if not expiry_date:
            return CertificateStatus.VALID
        
        today = date.today()
        if expiry_date < today:
            return CertificateStatus.EXPIRED
        
        days_until_expiry = (expiry_date - today).days
        if days_until_expiry <= 30:
            return CertificateStatus.EXPIRING
        
        return CertificateStatus.VALID
    
    async def create_certificate(
        self,
        cert_data: CertificateCreate,
        user_id: int
    ) -> Certificate:
        """
        创建证书记录（不上传文件）
        
        Args:
            cert_data: 证书数据
            user_id: 用户ID
            
        Returns:
            Certificate: 证书对象
        """
        # 检查证书编号是否已存在
        existing = await self.db.execute(
            select(Certificate).where(Certificate.certificate_no == cert_data.certificate_no)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="证书编号已存在")
        
        # 创建证书
        certificate = Certificate(
            **cert_data.model_dump(),
            status=self._calculate_status(cert_data.expiry_date),
            imported_by=user_id,
            imported_at=datetime.now(),
        )
        
        self.db.add(certificate)
        await self.db.commit()
        await self.db.refresh(certificate)
        
        return certificate
    
    async def get_certificate_by_id(self, cert_id: int) -> Optional[Certificate]:
        """根据ID获取证书"""
        result = await self.db.execute(
            select(Certificate)
            .where(Certificate.id == cert_id)
            .where(Certificate.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()
    
    async def get_certificate_by_no(self, cert_no: str) -> Optional[Certificate]:
        """根据证书编号获取证书"""
        result = await self.db.execute(
            select(Certificate)
            .where(Certificate.certificate_no == cert_no)
            .where(Certificate.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()
    
    async def list_certificates(
        self,
        query_params: CertificateQueryParams
    ) -> Tuple[List[Certificate], int]:
        """
        查询证书列表
        
        Args:
            query_params: 查询参数
            
        Returns:
            tuple: (证书列表, 总数)
        """
        # 构建查询条件
        conditions = [Certificate.deleted_at.is_(None)]
        
        if query_params.certificate_no:
            conditions.append(Certificate.certificate_no.ilike(f"%{query_params.certificate_no}%"))
        
        if query_params.certificate_type:
            conditions.append(Certificate.certificate_type == query_params.certificate_type)
        
        if query_params.status:
            conditions.append(Certificate.status == query_params.status)
        
        if query_params.issuing_authority:
            conditions.append(Certificate.issuing_authority.ilike(f"%{query_params.issuing_authority}%"))
        
        if query_params.holder_name:
            conditions.append(Certificate.holder_name.ilike(f"%{query_params.holder_name}%"))
        
        if query_params.issue_date_start:
            conditions.append(Certificate.issue_date >= query_params.issue_date_start)
        
        if query_params.issue_date_end:
            conditions.append(Certificate.issue_date <= query_params.issue_date_end)
        
        if query_params.expiry_date_start:
            conditions.append(Certificate.expiry_date >= query_params.expiry_date_start)
        
        if query_params.expiry_date_end:
            conditions.append(Certificate.expiry_date <= query_params.expiry_date_end)
        
        if query_params.days_until_expiry_max is not None:
            threshold_date = date.today() + timedelta(days=query_params.days_until_expiry_max)
            conditions.append(Certificate.expiry_date <= threshold_date)
            conditions.append(Certificate.expiry_date >= date.today())
        
        # 查询总数
        count_query = select(func.count()).select_from(Certificate).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 查询数据
        query = select(Certificate).where(and_(*conditions))
        
        # 排序
        order_column = getattr(Certificate, query_params.order_by, Certificate.created_at)
        if query_params.order_desc:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))
        
        # 分页
        offset = (query_params.page - 1) * query_params.page_size
        query = query.offset(offset).limit(query_params.page_size)
        
        result = await self.db.execute(query)
        certificates = list(result.scalars().all())
        
        return certificates, total
    
    async def update_certificate(
        self,
        cert_id: int,
        update_data: CertificateUpdate
    ) -> Certificate:
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
    
    async def delete_certificate(self, cert_id: int) -> Certificate:
        """删除证书（软删除）"""
        certificate = await self.get_certificate_by_id(cert_id)
        if not certificate:
            raise HTTPException(status_code=404, detail="证书不存在")
        
        certificate.soft_delete()
        certificate.status = CertificateStatus.REVOKED
        
        await self.db.commit()
        await self.db.refresh(certificate)
        
        return certificate
    
    async def associate_asset(
        self,
        cert_id: int,
        asset_id: int,
        user_id: int,
        notes: Optional[str] = None
    ) -> CertificateAsset:
        """
        关联证书到资产
        
        Args:
            cert_id: 证书ID
            asset_id: 资产ID
            user_id: 用户ID
            notes: 备注
            
        Returns:
            CertificateAsset: 关联记录
        """
        # 验证证书存在
        certificate = await self.get_certificate_by_id(cert_id)
        if not certificate:
            raise HTTPException(status_code=404, detail="证书不存在")
        
        # 验证资产存在
        asset_result = await self.db.execute(
            select(DataAsset).where(DataAsset.id == asset_id)
        )
        asset = asset_result.scalar_one_or_none()
        if not asset:
            raise HTTPException(status_code=404, detail="资产不存在")
        
        # 检查是否已关联
        existing = await self.db.execute(
            select(CertificateAsset).where(
                and_(
                    CertificateAsset.certificate_id == cert_id,
                    CertificateAsset.asset_id == asset_id,
                    CertificateAsset.is_active == True
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="证书已关联到该资产")
        
        # 创建关联
        association = CertificateAsset(
            certificate_id=cert_id,
            asset_id=asset_id,
            is_active=True,
            associated_by=user_id,
            associated_at=datetime.now(),
            notes=notes,
        )
        
        self.db.add(association)
        await self.db.commit()
        await self.db.refresh(association)
        
        return association
    
    async def disassociate_asset(
        self,
        cert_id: int,
        asset_id: int,
        user_id: int,
        notes: Optional[str] = None
    ) -> CertificateAsset:
        """
        解除证书与资产的关联
        
        Args:
            cert_id: 证书ID
            asset_id: 资产ID
            user_id: 用户ID
            notes: 备注
            
        Returns:
            CertificateAsset: 关联记录
        """
        # 查找关联记录
        result = await self.db.execute(
            select(CertificateAsset).where(
                and_(
                    CertificateAsset.certificate_id == cert_id,
                    CertificateAsset.asset_id == asset_id,
                    CertificateAsset.is_active == True
                )
            )
        )
        association = result.scalar_one_or_none()
        
        if not association:
            raise HTTPException(status_code=404, detail="未找到有效的关联记录")
        
        # 解除关联
        association.is_active = False
        association.disassociated_by = user_id
        association.disassociated_at = datetime.now()
        if notes:
            association.notes = (association.notes or "") + f"\n解除关联: {notes}"
        
        await self.db.commit()
        await self.db.refresh(association)
        
        return association
    
    async def get_associated_assets(self, cert_id: int) -> List[DataAsset]:
        """获取证书关联的资产列表"""
        result = await self.db.execute(
            select(DataAsset)
            .join(CertificateAsset, CertificateAsset.asset_id == DataAsset.id)
            .where(
                and_(
                    CertificateAsset.certificate_id == cert_id,
                    CertificateAsset.is_active == True
                )
            )
        )
        return list(result.scalars().all())
    
    async def verify_certificate(
        self,
        cert_id: int,
        user_id: int,
        method: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        验证证书
        
        Args:
            cert_id: 证书ID
            user_id: 用户ID
            method: 验证方法（hash/signature/comprehensive）
            
        Returns:
            dict: 验证结果
        """
        certificate = await self.get_certificate_by_id(cert_id)
        if not certificate:
            raise HTTPException(status_code=404, detail="证书不存在")
        
        # 获取证书文件
        file_result = await self.db.execute(
            select(CertificateFile)
            .where(CertificateFile.certificate_id == cert_id)
            .where(CertificateFile.is_primary == True)
        )
        cert_file = file_result.scalar_one_or_none()
        
        # 下载文件内容
        file_content = None
        if cert_file:
            try:
                response = self.minio_client.get_object(
                    bucket_name=self.bucket_name,
                    object_name=cert_file.file_path
                )
                file_content = response.read()
                response.close()
                response.release_conn()
            except S3Error as e:
                file_content = None
        
        # 执行验证
        cert_data = {
            'certificate_no': certificate.certificate_no,
            'issuing_authority': certificate.issuing_authority,
            'issue_date': certificate.issue_date,
            'expiry_date': certificate.expiry_date,
            'file_hash': cert_file.file_hash if cert_file else None,
            'digital_signature': certificate.digital_signature,
            'qr_code_data': certificate.qr_code_data,
            'verification_code': certificate.verification_code,
        }
        
        validation_result = self.validator.comprehensive_validation(cert_data, file_content)
        
        # 记录验证历史
        validation_record = CertificateValidation(
            certificate_id=cert_id,
            validation_status=ValidationStatus.PASSED if validation_result['is_valid'] else ValidationStatus.FAILED,
            validation_method=method,
            is_valid=validation_result['is_valid'],
            validation_message=validation_result['summary'],
            stored_hash=cert_file.file_hash if cert_file else None,
            current_hash=validation_result.get('validations', [{}])[0].get('details', {}).get('current_hash') if file_content else None,
            validated_by=user_id,
            validated_at=datetime.now(),
        )
        
        self.db.add(validation_record)
        await self.db.commit()
        
        return validation_result
    
    async def renew_certificate(
        self,
        cert_id: int,
        new_expiry_date: date,
        notes: Optional[str] = None
    ) -> Certificate:
        """
        续期证书
        
        Args:
            cert_id: 证书ID
            new_expiry_date: 新的有效期
            notes: 续期说明
            
        Returns:
            Certificate: 更新后的证书
        """
        certificate = await self.get_certificate_by_id(cert_id)
        if not certificate:
            raise HTTPException(status_code=404, detail="证书不存在")
        
        # 验证新有效期
        if new_expiry_date <= certificate.issue_date:
            raise HTTPException(status_code=400, detail="新有效期不能早于颁发日期")
        
        # 更新有效期
        old_expiry = certificate.expiry_date
        certificate.expiry_date = new_expiry_date
        certificate.status = self._calculate_status(new_expiry_date)
        
        # 更新备注
        renewal_note = f"\n续期: {old_expiry} -> {new_expiry_date}"
        if notes:
            renewal_note += f" ({notes})"
        certificate.notes = (certificate.notes or "") + renewal_note
        
        await self.db.commit()
        await self.db.refresh(certificate)
        
        return certificate
    
    async def get_expiring_certificates(
        self,
        days: int = 30,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Certificate], int]:
        """获取即将过期的证书列表"""
        today = date.today()
        expiry_threshold = today + timedelta(days=days)
        
        # 查询条件
        conditions = [
            Certificate.deleted_at.is_(None),
            Certificate.expiry_date.isnot(None),
            Certificate.expiry_date >= today,
            Certificate.expiry_date <= expiry_threshold,
            Certificate.status != CertificateStatus.REVOKED,
        ]
        
        # 计算总数
        count_query = select(func.count()).select_from(Certificate).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 查询数据
        query = select(Certificate).where(and_(*conditions)).order_by(Certificate.expiry_date.asc())
        
        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        certificates = list(result.scalars().all())
        
        return certificates, total
    
    def enrich_certificate_response(self, cert: Certificate) -> Dict[str, Any]:
        """丰富证书响应数据"""
        expiry_info = self.expiry_manager.get_expiry_info(cert.expiry_date)
        
        cert_dict = {
            'id': cert.id,
            'certificate_no': cert.certificate_no,
            'certificate_type': cert.certificate_type.value,
            'certificate_name': cert.certificate_name,
            'issuing_authority': cert.issuing_authority,
            'issue_date': cert.issue_date,
            'expiry_date': cert.expiry_date,
            'holder_name': cert.holder_name,
            'holder_id_number': cert.holder_id_number,
            'status': cert.status.value,
            'imported_by': cert.imported_by,
            'imported_at': cert.imported_at,
            'notes': cert.notes,
            'created_at': cert.created_at,
            'updated_at': cert.updated_at,
            # 计算字段
            'days_until_expiry': expiry_info['days_until_expiry'],
            'is_expired': expiry_info['is_expired'],
            'is_expiring_soon': expiry_info['is_expiring_soon'],
            'alert_level': expiry_info['alert_level'],
            'expiry_message': expiry_info['message'],
        }
        
        return cert_dict
