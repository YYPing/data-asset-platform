"""
数据资产业务逻辑服务
"""
import logging
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Request

from app.models.asset import DataAsset
from app.models.user import User
from app.schemas.asset import (
    AssetCreate, 
    AssetUpdate, 
    SearchParams,
    AssetSearchRequest
)
from app.utils.search import SearchService
from app.utils.audit import AuditLogger

logger = logging.getLogger(__name__)


class AssetService:
    """资产服务类"""

    # 可编辑状态
    EDITABLE_STATUSES = ["draft", "correction"]
    # 可删除状态
    DELETABLE_STATUSES = ["draft"]
    # 可提交状态
    SUBMITTABLE_STATUSES = ["draft"]
    
    # 状态流转规则
    STATUS_TRANSITIONS = {
        "draft": ["submitted"],  # 草稿 -> 已提交
        "submitted": ["approved", "rejected"],  # 已提交 -> 已审核/已驳回
        "approved": ["registered"],  # 已审核 -> 已登记
        "rejected": ["draft"],  # 已驳回 -> 草稿（修改后重新提交）
        "registered": ["cancelled"],  # 已登记 -> 已注销
    }
    
    # 阶段流转规则
    STAGE_TRANSITIONS = {
        "registration": ["compliance_assessment"],  # 登记 -> 合规评估
        "compliance_assessment": ["value_assessment"],  # 合规评估 -> 价值评估
        "value_assessment": ["ownership_confirmation"],  # 价值评估 -> 权属确认
        "ownership_confirmation": ["registration_certificate"],  # 权属确认 -> 登记证书
        "registration_certificate": ["account_entry"],  # 登记证书 -> 入账
        "account_entry": ["operation"],  # 入账 -> 运营
        "operation": ["change_management", "supervision", "exit"],  # 运营 -> 变更管理/监督/退出
    }

    @staticmethod
    async def generate_asset_code(db: AsyncSession) -> str:
        """
        生成资产编码：DA-YYYYMMDD-XXXX
        格式：DA-20260208-0001
        """
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"DA-{today}-"

        # 查询今天已有的最大序号
        stmt = select(DataAsset.asset_code).where(
            DataAsset.asset_code.like(f"{prefix}%")
        ).order_by(DataAsset.asset_code.desc()).limit(1)
        
        result = await db.execute(stmt)
        last_code = result.scalar_one_or_none()

        if last_code:
            # 提取序号并加1
            try:
                last_seq = int(last_code.split("-")[-1])
                new_seq = last_seq + 1
            except (ValueError, IndexError):
                new_seq = 1
        else:
            new_seq = 1

        return f"{prefix}{new_seq:04d}"

    @staticmethod
    async def create_asset(
        db: AsyncSession,
        asset_data: AssetCreate,
        current_user: User
    ) -> DataAsset:
        """
        创建资产（草稿状态）
        """
        # 生成资产编码
        asset_code = await AssetService.generate_asset_code(db)

        # 创建资产对象
        asset = DataAsset(
            asset_code=asset_code,
            asset_name=asset_data.asset_name,
            organization_id=asset_data.organization_id,
            category=asset_data.category,
            data_classification=asset_data.data_classification,
            sensitivity_level=asset_data.sensitivity_level,
            description=asset_data.description,
            data_source=asset_data.data_source,
            data_volume=asset_data.data_volume,
            data_format=asset_data.data_format,
            update_frequency=asset_data.update_frequency,
            asset_type=asset_data.asset_type,
            estimated_value=asset_data.estimated_value,
            assigned_to=asset_data.assigned_to,
            status="draft",
            current_stage="registration",
            created_by=current_user.id,
            version=1,
            previous_version_id=None
        )

        db.add(asset)
        await db.commit()
        await db.refresh(asset)

        logger.info(
            f"Asset created: {asset.asset_code} by user {current_user.id} "
            f"(org: {asset.organization_id})"
        )

        return asset

    @staticmethod
    async def get_asset_by_id(
        db: AsyncSession,
        asset_id: int,
        current_user: User
    ) -> DataAsset:
        """
        根据ID获取资产详情
        """
        stmt = select(DataAsset).where(
            and_(
                DataAsset.id == asset_id,
                DataAsset.deleted_at.is_(None)
            )
        )

        result = await db.execute(stmt)
        asset = result.scalar_one_or_none()

        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )

        # 权限检查：holder角色只能查看本组织资产
        if current_user.role in ["holder_admin", "holder_user"]:
            if asset.organization_id != current_user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No permission to access this asset"
                )

        return asset

    @staticmethod
    async def update_asset(
        db: AsyncSession,
        asset_id: int,
        asset_data: AssetUpdate,
        current_user: User
    ) -> DataAsset:
        """
        更新资产（仅draft/correction状态可编辑）
        """
        asset = await AssetService.get_asset_by_id(db, asset_id, current_user)

        # 状态检查
        if asset.status not in AssetService.EDITABLE_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Asset in status '{asset.status}' cannot be edited. "
                       f"Only {AssetService.EDITABLE_STATUSES} are editable."
            )

        # 权限检查：holder角色只能编辑本组织资产
        if current_user.role in ["holder_admin", "holder_user"]:
            if asset.organization_id != current_user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No permission to edit this asset"
                )

        # 更新字段
        update_data = asset_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(asset, field, value)

        asset.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(asset)

        logger.info(
            f"Asset updated: {asset.asset_code} by user {current_user.id}"
        )

        return asset

    @staticmethod
    async def delete_asset(
        db: AsyncSession,
        asset_id: int,
        current_user: User
    ) -> None:
        """
        软删除资产（仅draft状态）
        """
        asset = await AssetService.get_asset_by_id(db, asset_id, current_user)

        # 状态检查
        if asset.status not in AssetService.DELETABLE_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Asset in status '{asset.status}' cannot be deleted. "
                       f"Only {AssetService.DELETABLE_STATUSES} can be deleted."
            )

        # 权限检查
        if current_user.role in ["holder_admin", "holder_user"]:
            if asset.organization_id != current_user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No permission to delete this asset"
                )

        # 软删除
        asset.deleted_at = datetime.utcnow()
        await db.commit()

        logger.info(
            f"Asset soft-deleted: {asset.asset_code} by user {current_user.id}"
        )

    @staticmethod
    async def submit_asset(
        db: AsyncSession,
        asset_id: int,
        current_user: User
    ) -> DataAsset:
        """
        提交资产审批（draft → submitted）
        """
        asset = await AssetService.get_asset_by_id(db, asset_id, current_user)

        # 状态检查
        if asset.status not in AssetService.SUBMITTABLE_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Asset in status '{asset.status}' cannot be submitted. "
                       f"Only {AssetService.SUBMITTABLE_STATUSES} can be submitted."
            )

        # 权限检查
        if current_user.role in ["holder_admin", "holder_user"]:
            if asset.organization_id != current_user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No permission to submit this asset"
                )

        # 更新状态
        asset.status = "submitted"
        asset.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(asset)

        logger.info(
            f"Asset submitted: {asset.asset_code} by user {current_user.id}"
        )

        return asset

    @staticmethod
    async def list_assets(
        db: AsyncSession,
        params: SearchParams,
        current_user: User
    ) -> Tuple[List[DataAsset], int]:
        """
        资产列表查询（分页+搜索+筛选）
        """
        # 基础查询
        stmt = select(DataAsset).where(DataAsset.deleted_at.is_(None))

        # 组织过滤：holder角色只能查看本组织
        if current_user.role in ["holder_admin", "holder_user"]:
            stmt = stmt.where(DataAsset.organization_id == current_user.organization_id)
        elif params.org_id:
            stmt = stmt.where(DataAsset.organization_id == params.org_id)

        # 关键词搜索
        if params.q:
            search_term = f"%{params.q}%"
            stmt = stmt.where(
                or_(
                    DataAsset.asset_code.like(search_term),
                    DataAsset.asset_name.like(search_term),
                    DataAsset.description.like(search_term),
                    DataAsset.data_source.like(search_term)
                )
            )

        # 状态筛选
        if params.status:
            stmt = stmt.where(DataAsset.status == params.status)

        # 阶段筛选
        if params.stage:
            stmt = stmt.where(DataAsset.current_stage == params.stage)

        # 分类筛选
        if params.category:
            stmt = stmt.where(DataAsset.category == params.category)

        # 总数统计
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        # 分页
        offset = (params.page - 1) * params.page_size
        stmt = stmt.order_by(DataAsset.created_at.desc()).offset(offset).limit(params.page_size)

        # 执行查询
        result = await db.execute(stmt)
        assets = result.scalars().all()

        logger.info(
            f"Asset list query by user {current_user.id}: "
            f"total={total}, page={params.page}, page_size={params.page_size}"
        )

        return list(assets), total

    @staticmethod
    async def search_assets(
        db: AsyncSession,
        query: str,
        current_user: User,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[DataAsset], int]:
        """
        全文搜索资产
        """
        params = SearchParams(
            q=query,
            page=page,
            page_size=page_size
        )
        return await AssetService.list_assets(db, params, current_user)
    
    # ==================== 版本控制功能 ====================
    
    @staticmethod
    async def create_version(
        db: AsyncSession,
        asset_id: int,
        current_user: User,
        comment: Optional[str] = None,
        request: Optional[Request] = None
    ) -> DataAsset:
        """
        创建资产新版本
        
        将当前资产复制为新版本，保留历史版本
        """
        # 获取当前资产
        current_asset = await AssetService.get_asset_by_id(db, asset_id, current_user)
        
        # 权限检查
        if current_user.role in ["holder_admin", "holder_user"]:
            if current_asset.organization_id != current_user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No permission to create version for this asset"
                )
        
        # 创建新版本
        new_version = DataAsset(
            asset_code=current_asset.asset_code,
            asset_name=current_asset.asset_name,
            organization_id=current_asset.organization_id,
            category=current_asset.category,
            data_classification=current_asset.data_classification,
            sensitivity_level=current_asset.sensitivity_level,
            description=current_asset.description,
            data_source=current_asset.data_source,
            data_volume=current_asset.data_volume,
            data_format=current_asset.data_format,
            update_frequency=current_asset.update_frequency,
            current_stage=current_asset.current_stage,
            status=current_asset.status,
            asset_type=current_asset.asset_type,
            estimated_value=current_asset.estimated_value,
            created_by=current_user.id,
            assigned_to=current_asset.assigned_to,
            version=current_asset.version + 1,
            previous_version_id=current_asset.id
        )
        
        db.add(new_version)
        await db.commit()
        await db.refresh(new_version)
        
        # 记录审计日志
        await AuditLogger.log_version_create(
            db=db,
            user_id=current_user.id,
            asset_id=new_version.id,
            asset_code=new_version.asset_code,
            version=new_version.version,
            request=request
        )
        
        logger.info(
            f"Asset version created: {new_version.asset_code} v{new_version.version} "
            f"by user {current_user.id}"
        )
        
        return new_version
    
    @staticmethod
    async def get_version_history(
        db: AsyncSession,
        asset_id: int,
        current_user: User
    ) -> List[DataAsset]:
        """
        获取资产的版本历史
        
        返回该资产的所有版本（包括当前版本和历史版本）
        """
        # 获取当前资产
        current_asset = await AssetService.get_asset_by_id(db, asset_id, current_user)
        
        # 查询所有相同asset_code的版本
        stmt = select(DataAsset).where(
            and_(
                DataAsset.asset_code == current_asset.asset_code,
                DataAsset.deleted_at.is_(None)
            )
        ).order_by(DataAsset.version.desc())
        
        result = await db.execute(stmt)
        versions = list(result.scalars().all())
        
        return versions
    
    @staticmethod
    async def rollback_to_version(
        db: AsyncSession,
        asset_id: int,
        target_version_id: int,
        current_user: User,
        request: Optional[Request] = None
    ) -> DataAsset:
        """
        回滚到指定版本
        
        创建一个新版本，内容复制自目标版本
        """
        # 获取当前资产和目标版本
        current_asset = await AssetService.get_asset_by_id(db, asset_id, current_user)
        
        stmt = select(DataAsset).where(
            and_(
                DataAsset.id == target_version_id,
                DataAsset.asset_code == current_asset.asset_code,
                DataAsset.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        target_version = result.scalar_one_or_none()
        
        if not target_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target version not found"
            )
        
        # 权限检查
        if current_user.role in ["holder_admin", "holder_user"]:
            if current_asset.organization_id != current_user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No permission to rollback this asset"
                )
        
        # 创建新版本（内容来自目标版本）
        new_version = DataAsset(
            asset_code=target_version.asset_code,
            asset_name=target_version.asset_name,
            organization_id=target_version.organization_id,
            category=target_version.category,
            data_classification=target_version.data_classification,
            sensitivity_level=target_version.sensitivity_level,
            description=target_version.description,
            data_source=target_version.data_source,
            data_volume=target_version.data_volume,
            data_format=target_version.data_format,
            update_frequency=target_version.update_frequency,
            current_stage=target_version.current_stage,
            status=target_version.status,
            asset_type=target_version.asset_type,
            estimated_value=target_version.estimated_value,
            created_by=current_user.id,
            assigned_to=target_version.assigned_to,
            version=current_asset.version + 1,
            previous_version_id=current_asset.id
        )
        
        db.add(new_version)
        await db.commit()
        await db.refresh(new_version)
        
        # 记录审计日志
        await AuditLogger.log_version_rollback(
            db=db,
            user_id=current_user.id,
            asset_id=new_version.id,
            asset_code=new_version.asset_code,
            from_version=current_asset.version,
            to_version=target_version.version,
            request=request
        )
        
        logger.info(
            f"Asset rolled back: {new_version.asset_code} "
            f"v{current_asset.version} -> v{target_version.version} "
            f"(new version: v{new_version.version}) by user {current_user.id}"
        )
        
        return new_version
    
    # ==================== 状态流转功能 ====================
    
    @staticmethod
    def _check_status_transition(current_status: str, new_status: str) -> bool:
        """检查状态流转是否合法"""
        allowed_statuses = AssetService.STATUS_TRANSITIONS.get(current_status, [])
        return new_status in allowed_statuses
    
    @staticmethod
    async def approve_asset(
        db: AsyncSession,
        asset_id: int,
        current_user: User,
        comment: Optional[str] = None,
        request: Optional[Request] = None
    ) -> DataAsset:
        """
        审核通过资产（submitted -> approved）
        """
        asset = await AssetService.get_asset_by_id(db, asset_id, current_user)
        
        # 状态检查
        if asset.status != "submitted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Asset in status '{asset.status}' cannot be approved. "
                       "Only 'submitted' assets can be approved."
            )
        
        # 权限检查：只有审核员和管理员可以审核
        if current_user.role not in ["reviewer", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only reviewers and admins can approve assets"
            )
        
        # 更新状态
        old_status = asset.status
        asset.status = "approved"
        asset.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(asset)
        
        # 记录审计日志
        await AuditLogger.log_asset_approve(
            db=db,
            user_id=current_user.id,
            asset_id=asset.id,
            asset_code=asset.asset_code,
            comment=comment,
            request=request
        )
        
        logger.info(
            f"Asset approved: {asset.asset_code} by user {current_user.id}"
        )
        
        return asset
    
    @staticmethod
    async def reject_asset(
        db: AsyncSession,
        asset_id: int,
        current_user: User,
        reason: str,
        request: Optional[Request] = None
    ) -> DataAsset:
        """
        审核驳回资产（submitted -> rejected）
        """
        asset = await AssetService.get_asset_by_id(db, asset_id, current_user)
        
        # 状态检查
        if asset.status != "submitted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Asset in status '{asset.status}' cannot be rejected. "
                       "Only 'submitted' assets can be rejected."
            )
        
        # 权限检查：只有审核员和管理员可以驳回
        if current_user.role not in ["reviewer", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only reviewers and admins can reject assets"
            )
        
        # 更新状态
        old_status = asset.status
        asset.status = "rejected"
        asset.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(asset)
        
        # 记录审计日志
        await AuditLogger.log_asset_reject(
            db=db,
            user_id=current_user.id,
            asset_id=asset.id,
            asset_code=asset.asset_code,
            reason=reason,
            request=request
        )
        
        logger.info(
            f"Asset rejected: {asset.asset_code} by user {current_user.id}, reason: {reason}"
        )
        
        return asset
    
    @staticmethod
    async def register_asset(
        db: AsyncSession,
        asset_id: int,
        current_user: User,
        comment: Optional[str] = None,
        request: Optional[Request] = None
    ) -> DataAsset:
        """
        完成资产登记（approved -> registered）
        """
        asset = await AssetService.get_asset_by_id(db, asset_id, current_user)
        
        # 状态检查
        if asset.status != "approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Asset in status '{asset.status}' cannot be registered. "
                       "Only 'approved' assets can be registered."
            )
        
        # 权限检查：只有管理员可以完成登记
        if current_user.role not in ["admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can register assets"
            )
        
        # 更新状态
        old_status = asset.status
        asset.status = "registered"
        asset.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(asset)
        
        # 记录审计日志
        await AuditLogger.log_asset_register(
            db=db,
            user_id=current_user.id,
            asset_id=asset.id,
            asset_code=asset.asset_code,
            request=request
        )
        
        logger.info(
            f"Asset registered: {asset.asset_code} by user {current_user.id}"
        )
        
        return asset
    
    @staticmethod
    async def cancel_asset(
        db: AsyncSession,
        asset_id: int,
        current_user: User,
        reason: str,
        request: Optional[Request] = None
    ) -> DataAsset:
        """
        注销资产（registered -> cancelled）
        """
        asset = await AssetService.get_asset_by_id(db, asset_id, current_user)
        
        # 状态检查
        if asset.status != "registered":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Asset in status '{asset.status}' cannot be cancelled. "
                       "Only 'registered' assets can be cancelled."
            )
        
        # 权限检查：只有管理员可以注销
        if current_user.role not in ["admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can cancel assets"
            )
        
        # 更新状态
        old_status = asset.status
        asset.status = "cancelled"
        asset.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(asset)
        
        # 记录审计日志
        await AuditLogger.log_asset_cancel(
            db=db,
            user_id=current_user.id,
            asset_id=asset.id,
            asset_code=asset.asset_code,
            reason=reason,
            request=request
        )
        
        logger.info(
            f"Asset cancelled: {asset.asset_code} by user {current_user.id}, reason: {reason}"
        )
        
        return asset
    
    # ==================== 高级搜索功能 ====================
    
    @staticmethod
    async def advanced_search(
        db: AsyncSession,
        search_params: AssetSearchRequest,
        current_user: User
    ) -> Tuple[List[DataAsset], int]:
        """
        高级搜索 - 支持中文分词全文搜索和多维度筛选
        """
        # 确定组织过滤
        organization_id = None
        if current_user.role in ["holder_admin", "holder_user"]:
            organization_id = current_user.organization_id
        elif search_params.organization_id:
            organization_id = search_params.organization_id
        
        # 计算偏移量
        offset = (search_params.page - 1) * search_params.page_size
        
        # 使用搜索服务进行全文搜索
        assets, total = await SearchService.search_assets(
            db=db,
            query=search_params.keyword,
            organization_id=organization_id,
            limit=search_params.page_size,
            offset=offset,
            use_fulltext=search_params.use_fulltext
        )
        
        # 应用额外的筛选条件
        if search_params.status or search_params.stage or search_params.category or \
           search_params.data_classification or search_params.sensitivity_level or \
           search_params.created_by or search_params.date_from or search_params.date_to:
            
            # 构建筛选查询
            asset_ids = [asset.id for asset in assets]
            if not asset_ids:
                return [], 0
            
            stmt = select(DataAsset).where(
                and_(
                    DataAsset.id.in_(asset_ids),
                    DataAsset.deleted_at.is_(None)
                )
            )
            
            # 状态筛选
            if search_params.status:
                stmt = stmt.where(DataAsset.status.in_(search_params.status))
            
            # 阶段筛选
            if search_params.stage:
                stmt = stmt.where(DataAsset.current_stage.in_(search_params.stage))
            
            # 分类筛选
            if search_params.category:
                stmt = stmt.where(DataAsset.category.in_(search_params.category))
            
            # 数据分类筛选
            if search_params.data_classification:
                stmt = stmt.where(DataAsset.data_classification.in_(search_params.data_classification))
            
            # 敏感级别筛选
            if search_params.sensitivity_level:
                stmt = stmt.where(DataAsset.sensitivity_level.in_(search_params.sensitivity_level))
            
            # 创建人筛选
            if search_params.created_by:
                stmt = stmt.where(DataAsset.created_by == search_params.created_by)
            
            # 日期范围筛选
            if search_params.date_from:
                stmt = stmt.where(DataAsset.created_at >= search_params.date_from)
            if search_params.date_to:
                stmt = stmt.where(DataAsset.created_at <= search_params.date_to)
            
            # 重新计数
            count_stmt = select(func.count()).select_from(stmt.subquery())
            count_result = await db.execute(count_stmt)
            total = count_result.scalar() or 0
            
            # 执行筛选查询
            result = await db.execute(stmt)
            assets = list(result.scalars().all())
        
        logger.info(
            f"Advanced search by user {current_user.id}: "
            f"keyword='{search_params.keyword}', total={total}"
        )
        
        return assets, total
