"""
材料管理服务 - 增强版
包含完整的材料CRUD、文件上传（分片上传、断点续传）、哈希存证、版本管理和审核流程
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from pathlib import Path

from fastapi import UploadFile, HTTPException
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Material, DataAsset
from app.models.user import User
from app.schemas.material import (
    MaterialCreate, MaterialUpdate, MaterialResponse, MaterialListResponse,
    MaterialQuery, MaterialUploadRequest, MaterialUploadResponse,
    ChunkUploadResponse, CompleteUploadResponse,
    MaterialHashResponse, MaterialVerifyResponse,
    MaterialVersionCreate, MaterialVersionResponse, MaterialVersionListResponse,
    MaterialReviewResponse, MaterialDownloadResponse
)
from app.utils.minio_client import minio_client
from app.utils.file_hash import calculate_file_hash, calculate_bytes_hash, verify_file_hash
from app.utils.upload_manager import upload_manager
from app.config import settings

logger = logging.getLogger(__name__)


class MaterialService:
    """材料管理服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.bucket_name = settings.MINIO_BUCKET
        # 确保存储桶存在
        minio_client.ensure_bucket(self.bucket_name)
    
    # ==================== CRUD 操作 ====================
    
    async def create_material(
        self,
        db: AsyncSession,
        material_data: MaterialCreate,
        user_id: int
    ) -> Material:
        """
        创建材料记录
        
        Args:
            db: 数据库会话
            material_data: 材料数据
            user_id: 当前用户ID
            
        Returns:
            Material: 创建的材料对象
            
        Raises:
            HTTPException: 资产不存在
        """
        # 验证资产是否存在
        result = await db.execute(
            select(DataAsset).where(DataAsset.id == material_data.asset_id)
        )
        asset = result.scalar_one_or_none()
        if not asset:
            raise HTTPException(status_code=404, detail="资产不存在")
        
        # 创建材料记录
        material = Material(
            asset_id=material_data.asset_id,
            material_name=material_data.material_name,
            material_type=material_data.material_type,
            stage=material_data.stage,
            file_path=material_data.file_path,
            file_size=material_data.file_size,
            file_format=material_data.file_format,
            file_hash=material_data.file_hash,
            version=1,
            is_required=material_data.is_required,
            status='pending',
            uploaded_by=user_id,
            uploaded_at=datetime.utcnow()
        )
        
        db.add(material)
        await db.commit()
        await db.refresh(material)
        
        logger.info(f"创建材料记录: ID={material.id}, 名称={material.material_name}")
        return material
    
    async def get_material(
        self,
        db: AsyncSession,
        material_id: int
    ) -> Optional[Material]:
        """
        获取材料详情
        
        Args:
            db: 数据库会话
            material_id: 材料ID
            
        Returns:
            Optional[Material]: 材料对象或None
        """
        result = await db.execute(
            select(Material).where(Material.id == material_id)
        )
        return result.scalar_one_or_none()
    
    async def list_materials(
        self,
        db: AsyncSession,
        query: MaterialQuery
    ) -> Tuple[List[Material], int]:
        """
        获取材料列表（分页、筛选）
        
        Args:
            db: 数据库会话
            query: 查询参数
            
        Returns:
            Tuple[List[Material], int]: 材料列表和总数
        """
        # 构建查询条件
        conditions = []
        
        if query.asset_id:
            conditions.append(Material.asset_id == query.asset_id)
        
        if query.stage:
            conditions.append(Material.stage == query.stage)
        
        if query.status:
            conditions.append(Material.status == query.status)
        
        if query.material_type:
            conditions.append(Material.material_type == query.material_type)
        
        if query.keyword:
            conditions.append(
                Material.material_name.ilike(f"%{query.keyword}%")
            )
        
        # 查询总数
        count_stmt = select(func.count(Material.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        
        count_result = await db.execute(count_stmt)
        total = count_result.scalar()
        
        # 查询列表
        stmt = select(Material)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.order_by(desc(Material.uploaded_at))
        stmt = stmt.offset((query.page - 1) * query.page_size)
        stmt = stmt.limit(query.page_size)
        
        result = await db.execute(stmt)
        materials = result.scalars().all()
        
        return list(materials), total
    
    async def update_material(
        self,
        db: AsyncSession,
        material_id: int,
        material_data: MaterialUpdate
    ) -> Material:
        """
        更新材料信息
        
        Args:
            db: 数据库会话
            material_id: 材料ID
            material_data: 更新数据
            
        Returns:
            Material: 更新后的材料对象
            
        Raises:
            HTTPException: 材料不存在
        """
        material = await self.get_material(db, material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        # 更新字段
        update_data = material_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(material, field, value)
        
        await db.commit()
        await db.refresh(material)
        
        logger.info(f"更新材料: ID={material_id}")
        return material
    
    async def delete_material(
        self,
        db: AsyncSession,
        material_id: int,
        soft_delete: bool = True
    ) -> None:
        """
        删除材料（软删除或硬删除）
        
        Args:
            db: 数据库会话
            material_id: 材料ID
            soft_delete: 是否软删除
            
        Raises:
            HTTPException: 材料不存在
        """
        material = await self.get_material(db, material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        if soft_delete:
            # 软删除：更新状态为 archived
            material.status = 'archived'
            await db.commit()
            logger.info(f"软删除材料: ID={material_id}")
        else:
            # 硬删除：删除MinIO文件和数据库记录
            try:
                if material.file_path:
                    minio_client.delete_file(self.bucket_name, material.file_path)
            except Exception as e:
                logger.warning(f"删除MinIO文件失败: {e}")
            
            await db.delete(material)
            await db.commit()
            logger.info(f"硬删除材料: ID={material_id}")
    
    # ==================== 文件上传（分片上传、断点续传）====================
    
    async def initiate_upload(
        self,
        db: AsyncSession,
        upload_request: MaterialUploadRequest,
        user_id: int
    ) -> MaterialUploadResponse:
        """
        初始化文件上传（创建上传会话）
        
        Args:
            db: 数据库会话
            upload_request: 上传请求
            user_id: 当前用户ID
            
        Returns:
            MaterialUploadResponse: 上传会话信息
            
        Raises:
            HTTPException: 资产不存在
        """
        # 验证资产是否存在
        result = await db.execute(
            select(DataAsset).where(DataAsset.id == upload_request.asset_id)
        )
        asset = result.scalar_one_or_none()
        if not asset:
            raise HTTPException(status_code=404, detail="资产不存在")
        
        # 生成会话ID和对象名称
        session_id = str(uuid.uuid4())
        object_name = f"{upload_request.asset_id}/{upload_request.stage}/{session_id}_{upload_request.file_name}"
        
        # 创建上传会话
        session = upload_manager.create_session(
            session_id=session_id,
            file_name=upload_request.file_name,
            file_size=upload_request.file_size,
            bucket_name=self.bucket_name,
            object_name=object_name
        )
        
        logger.info(
            f"初始化上传: 会话ID={session_id}, 文件={upload_request.file_name}, "
            f"大小={upload_request.file_size}"
        )
        
        return MaterialUploadResponse(
            session_id=session.session_id,
            file_name=session.file_name,
            file_size=session.file_size,
            total_chunks=session.total_chunks,
            chunk_size=upload_manager.chunk_size,
            bucket_name=session.bucket_name,
            object_name=session.object_name
        )
    
    async def upload_chunk(
        self,
        session_id: str,
        chunk_index: int,
        chunk_data: bytes
    ) -> ChunkUploadResponse:
        """
        上传文件分片
        
        Args:
            session_id: 上传会话ID
            chunk_index: 分片索引
            chunk_data: 分片数据
            
        Returns:
            ChunkUploadResponse: 上传结果
            
        Raises:
            HTTPException: 会话不存在或上传失败
        """
        try:
            result = upload_manager.upload_chunk(
                session_id=session_id,
                chunk_index=chunk_index,
                chunk_data=chunk_data
            )
            
            return ChunkUploadResponse(**result)
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"上传分片失败: {e}")
            raise HTTPException(status_code=500, detail=f"上传分片失败: {str(e)}")
    
    async def complete_upload(
        self,
        db: AsyncSession,
        session_id: str,
        material_name: str,
        material_type: Optional[str],
        stage: str,
        is_required: bool,
        user_id: int,
        verify_hash: Optional[str] = None
    ) -> CompleteUploadResponse:
        """
        完成文件上传（合并分片并创建材料记录）
        
        Args:
            db: 数据库会话
            session_id: 上传会话ID
            material_name: 材料名称
            material_type: 材料类型
            stage: 所属阶段
            is_required: 是否必需
            user_id: 当前用户ID
            verify_hash: 验证哈希值（可选）
            
        Returns:
            CompleteUploadResponse: 完成结果
            
        Raises:
            HTTPException: 会话不存在或上传未完成
        """
        try:
            # 完成上传（合并分片）
            result = await upload_manager.complete_upload(
                session_id=session_id,
                verify_hash=verify_hash
            )
            
            # 从对象名称中提取资产ID
            asset_id = int(result["object_name"].split("/")[0])
            
            # 提取文件格式
            file_format = Path(result["file_name"]).suffix.lstrip(".")
            
            # 创建材料记录
            material = Material(
                asset_id=asset_id,
                material_name=material_name,
                material_type=material_type,
                stage=stage,
                file_path=result["object_name"],
                file_size=result["file_size"],
                file_format=file_format,
                file_hash=result["file_hash"],
                version=1,
                is_required=is_required,
                status='pending',
                uploaded_by=user_id,
                uploaded_at=datetime.utcnow()
            )
            
            db.add(material)
            await db.commit()
            await db.refresh(material)
            
            logger.info(
                f"完成上传: 会话ID={session_id}, 材料ID={material.id}, "
                f"哈希={result['file_hash']}"
            )
            
            return CompleteUploadResponse(
                material_id=material.id,
                file_name=result["file_name"],
                file_size=result["file_size"],
                file_hash=result["file_hash"],
                object_name=result["object_name"]
            )
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"完成上传失败: {e}")
            raise HTTPException(status_code=500, detail=f"完成上传失败: {str(e)}")
    
    async def cancel_upload(self, session_id: str) -> None:
        """
        取消上传
        
        Args:
            session_id: 上传会话ID
        """
        try:
            upload_manager.cancel_upload(session_id)
            logger.info(f"取消上传: 会话ID={session_id}")
        except Exception as e:
            logger.error(f"取消上传失败: {e}")
            raise HTTPException(status_code=500, detail=f"取消上传失败: {str(e)}")
    
    # ==================== 文件下载 ====================
    
    async def download_material(
        self,
        db: AsyncSession,
        material_id: int,
        expires_in: int = 3600
    ) -> MaterialDownloadResponse:
        """
        生成材料下载URL（预签名URL）
        
        Args:
            db: 数据库会话
            material_id: 材料ID
            expires_in: URL有效期（秒）
            
        Returns:
            MaterialDownloadResponse: 下载信息
            
        Raises:
            HTTPException: 材料不存在
        """
        material = await self.get_material(db, material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        if not material.file_path:
            raise HTTPException(status_code=400, detail="材料文件不存在")
        
        # 生成预签名URL
        download_url = minio_client.get_presigned_url(
            bucket_name=self.bucket_name,
            object_name=material.file_path,
            expires=timedelta(seconds=expires_in)
        )
        
        logger.info(f"生成下载URL: 材料ID={material_id}")
        
        return MaterialDownloadResponse(
            material_id=material_id,
            file_name=material.material_name,
            download_url=download_url,
            expires_in=expires_in
        )
    
    # ==================== 哈希计算和验证 ====================
    
    async def get_material_hash(
        self,
        db: AsyncSession,
        material_id: int,
        algorithm: str = "sha256"
    ) -> MaterialHashResponse:
        """
        获取材料哈希值
        
        Args:
            db: 数据库会话
            material_id: 材料ID
            algorithm: 哈希算法
            
        Returns:
            MaterialHashResponse: 哈希信息
            
        Raises:
            HTTPException: 材料不存在
        """
        material = await self.get_material(db, material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        # 如果请求的是SHA256且数据库中已有，直接返回
        if algorithm == "sha256":
            return MaterialHashResponse(
                material_id=material_id,
                file_hash=material.file_hash,
                algorithm=algorithm,
                file_size=material.file_size or 0
            )
        
        # 否则需要重新计算
        if not material.file_path:
            raise HTTPException(status_code=400, detail="材料文件不存在")
        
        # 下载文件并计算哈希
        file_data = minio_client.download_stream(
            bucket_name=self.bucket_name,
            object_name=material.file_path
        )
        
        file_hash = calculate_bytes_hash(file_data, algorithm)
        
        return MaterialHashResponse(
            material_id=material_id,
            file_hash=file_hash,
            algorithm=algorithm,
            file_size=len(file_data)
        )
    
    async def verify_material(
        self,
        db: AsyncSession,
        material_id: int,
        expected_hash: str,
        algorithm: str = "sha256"
    ) -> MaterialVerifyResponse:
        """
        验证材料完整性
        
        Args:
            db: 数据库会话
            material_id: 材料ID
            expected_hash: 期望的哈希值
            algorithm: 哈希算法
            
        Returns:
            MaterialVerifyResponse: 验证结果
            
        Raises:
            HTTPException: 材料不存在
        """
        material = await self.get_material(db, material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        if not material.file_path:
            raise HTTPException(status_code=400, detail="材料文件不存在")
        
        # 下载文件并计算哈希
        file_data = minio_client.download_stream(
            bucket_name=self.bucket_name,
            object_name=material.file_path
        )
        
        actual_hash = calculate_bytes_hash(file_data, algorithm)
        is_valid = actual_hash.lower() == expected_hash.lower()
        
        logger.info(
            f"验证材料: ID={material_id}, 算法={algorithm}, "
            f"结果={'通过' if is_valid else '失败'}"
        )
        
        return MaterialVerifyResponse(
            material_id=material_id,
            is_valid=is_valid,
            expected_hash=expected_hash,
            actual_hash=actual_hash,
            algorithm=algorithm
        )
    
    # ==================== 版本管理 ====================
    
    async def create_version(
        self,
        db: AsyncSession,
        material_id: int,
        version_data: MaterialVersionCreate,
        user_id: int
    ) -> Material:
        """
        创建材料新版本
        
        Args:
            db: 数据库会话
            material_id: 材料ID
            version_data: 版本数据
            user_id: 当前用户ID
            
        Returns:
            Material: 新版本材料对象
            
        Raises:
            HTTPException: 材料不存在
        """
        # 获取当前材料
        current_material = await self.get_material(db, material_id)
        if not current_material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        # 创建新版本
        new_version = current_material.version + 1
        
        new_material = Material(
            asset_id=current_material.asset_id,
            material_name=current_material.material_name,
            material_type=current_material.material_type,
            stage=current_material.stage,
            file_path=version_data.file_path,
            file_size=version_data.file_size,
            file_format=current_material.file_format,
            file_hash=version_data.file_hash,
            version=new_version,
            is_required=current_material.is_required,
            status='pending',
            uploaded_by=user_id,
            uploaded_at=datetime.utcnow()
        )
        
        db.add(new_material)
        await db.commit()
        await db.refresh(new_material)
        
        logger.info(
            f"创建材料新版本: 原ID={material_id}, 新ID={new_material.id}, "
            f"版本={new_version}"
        )
        
        return new_material
    
    async def get_version_history(
        self,
        db: AsyncSession,
        material_id: int
    ) -> MaterialVersionListResponse:
        """
        获取材料版本历史
        
        Args:
            db: 数据库会话
            material_id: 材料ID
            
        Returns:
            MaterialVersionListResponse: 版本历史
            
        Raises:
            HTTPException: 材料不存在
        """
        material = await self.get_material(db, material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        # 查询同名材料的所有版本
        result = await db.execute(
            select(Material)
            .where(
                and_(
                    Material.asset_id == material.asset_id,
                    Material.material_name == material.material_name,
                    Material.stage == material.stage
                )
            )
            .order_by(desc(Material.version))
        )
        versions = result.scalars().all()
        
        # 转换为响应格式
        version_responses = [
            MaterialVersionResponse(
                id=v.id,
                material_id=material_id,
                version=v.version,
                file_hash=v.file_hash,
                file_path=v.file_path,
                file_size=v.file_size,
                change_description=None,  # 可以从元数据中获取
                created_by=v.uploaded_by,
                created_at=v.uploaded_at
            )
            for v in versions
        ]
        
        return MaterialVersionListResponse(
            material_id=material_id,
            current_version=material.version,
            versions=version_responses
        )
    
    # ==================== 审核流程 ====================
    
    async def submit_for_review(
        self,
        db: AsyncSession,
        material_id: int,
        comment: Optional[str] = None
    ) -> MaterialReviewResponse:
        """
        提交材料审核
        
        Args:
            db: 数据库会话
            material_id: 材料ID
            comment: 提交说明
            
        Returns:
            MaterialReviewResponse: 审核响应
            
        Raises:
            HTTPException: 材料不存在或状态不允许
        """
        material = await self.get_material(db, material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        if material.status != 'pending':
            raise HTTPException(
                status_code=400,
                detail=f"材料状态不允许提交审核: {material.status}"
            )
        
        # 更新状态（这里简化处理，实际应该创建审核流程）
        material.status = 'pending'
        material.review_comment = comment
        
        await db.commit()
        await db.refresh(material)
        
        logger.info(f"提交材料审核: ID={material_id}")
        
        return MaterialReviewResponse(
            material_id=material_id,
            status=material.status,
            reviewed_by=material.reviewed_by,
            reviewed_at=material.reviewed_at,
            review_comment=material.review_comment
        )
    
    async def approve_material(
        self,
        db: AsyncSession,
        material_id: int,
        reviewer_id: int,
        comment: Optional[str] = None
    ) -> MaterialReviewResponse:
        """
        审核通过材料
        
        Args:
            db: 数据库会话
            material_id: 材料ID
            reviewer_id: 审核人ID
            comment: 审核意见
            
        Returns:
            MaterialReviewResponse: 审核响应
            
        Raises:
            HTTPException: 材料不存在或状态不允许
        """
        material = await self.get_material(db, material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        if material.status not in ['pending']:
            raise HTTPException(
                status_code=400,
                detail=f"材料状态不允许审核: {material.status}"
            )
        
        # 更新审核信息
        material.status = 'approved'
        material.reviewed_by = reviewer_id
        material.reviewed_at = datetime.utcnow()
        material.review_comment = comment
        
        await db.commit()
        await db.refresh(material)
        
        logger.info(f"审核通过材料: ID={material_id}, 审核人={reviewer_id}")
        
        return MaterialReviewResponse(
            material_id=material_id,
            status=material.status,
            reviewed_by=material.reviewed_by,
            reviewed_at=material.reviewed_at,
            review_comment=material.review_comment
        )
    
    async def reject_material(
        self,
        db: AsyncSession,
        material_id: int,
        reviewer_id: int,
        comment: str
    ) -> MaterialReviewResponse:
        """
        审核驳回材料
        
        Args:
            db: 数据库会话
            material_id: 材料ID
            reviewer_id: 审核人ID
            comment: 驳回原因
            
        Returns:
            MaterialReviewResponse: 审核响应
            
        Raises:
            HTTPException: 材料不存在或状态不允许
        """
        material = await self.get_material(db, material_id)
        if not material:
            raise HTTPException(status_code=404, detail="材料不存在")
        
        if material.status not in ['pending']:
            raise HTTPException(
                status_code=400,
                detail=f"材料状态不允许审核: {material.status}"
            )
        
        # 更新审核信息
        material.status = 'rejected'
        material.reviewed_by = reviewer_id
        material.reviewed_at = datetime.utcnow()
        material.review_comment = comment
        
        await db.commit()
        await db.refresh(material)
        
        logger.info(f"审核驳回材料: ID={material_id}, 审核人={reviewer_id}")
        
        return MaterialReviewResponse(
            material_id=material_id,
            status=material.status,
            reviewed_by=material.reviewed_by,
            reviewed_at=material.reviewed_at,
            review_comment=material.review_comment
        )


# 全局服务实例
material_service = MaterialService()
