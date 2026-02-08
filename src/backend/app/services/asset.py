"""
数据资产业务逻辑服务
"""
import logging
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.asset import DataAsset
from app.models.user import User
from app.schemas.asset import AssetCreate, AssetUpdate, SearchParams

logger = logging.getLogger(__name__)


class AssetService:
    """资产服务类"""

    # 可编辑状态
    EDITABLE_STATUSES = ["draft", "correction"]
    # 可删除状态
    DELETABLE_STATUSES = ["draft"]
    # 可提交状态
    SUBMITTABLE_STATUSES = ["draft"]

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
