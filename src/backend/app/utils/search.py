"""
搜索工具模块 - 支持PostgreSQL zhparser中文分词
"""
from typing import List, Optional
from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import DataAsset


class SearchService:
    """搜索服务类 - 支持中文分词全文搜索"""
    
    @staticmethod
    async def init_zhparser(db: AsyncSession) -> bool:
        """
        初始化zhparser中文分词扩展
        
        需要在PostgreSQL中预先安装zhparser扩展：
        CREATE EXTENSION IF NOT EXISTS zhparser;
        CREATE TEXT SEARCH CONFIGURATION chinese_zh (PARSER = zhparser);
        ALTER TEXT SEARCH CONFIGURATION chinese_zh ADD MAPPING FOR n,v,a,i,e,l WITH simple;
        
        Returns:
            bool: 是否成功初始化
        """
        try:
            # 检查zhparser扩展是否存在
            result = await db.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'zhparser'")
            )
            if not result.scalar():
                return False
            
            # 检查中文分词配置是否存在
            result = await db.execute(
                text("SELECT 1 FROM pg_ts_config WHERE cfgname = 'chinese_zh'")
            )
            if not result.scalar():
                return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    async def update_search_vector(
        db: AsyncSession,
        asset_id: int
    ) -> None:
        """
        更新资产的搜索向量
        
        将资产的名称、描述、数据来源等字段转换为tsvector
        使用中文分词配置
        
        Args:
            db: 数据库会话
            asset_id: 资产ID
        """
        # 使用SQL更新搜索向量
        # 合并多个字段，使用不同的权重：
        # A权重（最高）：资产名称、资产编码
        # B权重：描述
        # C权重：数据来源
        # D权重（最低）：其他字段
        
        sql = text("""
            UPDATE data_assets
            SET search_vector = 
                setweight(to_tsvector('chinese_zh', COALESCE(asset_code, '')), 'A') ||
                setweight(to_tsvector('chinese_zh', COALESCE(asset_name, '')), 'A') ||
                setweight(to_tsvector('chinese_zh', COALESCE(description, '')), 'B') ||
                setweight(to_tsvector('chinese_zh', COALESCE(data_source, '')), 'C') ||
                setweight(to_tsvector('chinese_zh', COALESCE(category, '')), 'D') ||
                setweight(to_tsvector('chinese_zh', COALESCE(asset_type, '')), 'D')
            WHERE id = :asset_id
        """)
        
        await db.execute(sql, {"asset_id": asset_id})
    
    @staticmethod
    async def search_assets_fulltext(
        db: AsyncSession,
        query: str,
        organization_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[DataAsset], int]:
        """
        使用中文分词进行全文搜索
        
        Args:
            db: 数据库会话
            query: 搜索关键词
            organization_id: 组织ID过滤（可选）
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            tuple: (资产列表, 总数)
        """
        # 构建搜索查询
        # 使用ts_rank进行相关性排序
        search_query = text("""
            SELECT 
                id,
                asset_code,
                asset_name,
                organization_id,
                category,
                data_classification,
                sensitivity_level,
                description,
                data_source,
                data_volume,
                data_format,
                update_frequency,
                current_stage,
                status,
                asset_type,
                estimated_value,
                created_by,
                assigned_to,
                version,
                previous_version_id,
                created_at,
                updated_at,
                deleted_at,
                ts_rank(search_vector, query) as rank
            FROM data_assets, to_tsquery('chinese_zh', :query) query
            WHERE search_vector @@ query
                AND deleted_at IS NULL
                AND (:org_id IS NULL OR organization_id = :org_id)
            ORDER BY rank DESC, created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        
        # 构建计数查询
        count_query = text("""
            SELECT COUNT(*)
            FROM data_assets, to_tsquery('chinese_zh', :query) query
            WHERE search_vector @@ query
                AND deleted_at IS NULL
                AND (:org_id IS NULL OR organization_id = :org_id)
        """)
        
        # 处理查询字符串：将空格替换为&（AND操作）
        processed_query = query.strip().replace(' ', '&')
        
        # 执行搜索
        result = await db.execute(
            search_query,
            {
                "query": processed_query,
                "org_id": organization_id,
                "limit": limit,
                "offset": offset
            }
        )
        rows = result.fetchall()
        
        # 执行计数
        count_result = await db.execute(
            count_query,
            {
                "query": processed_query,
                "org_id": organization_id
            }
        )
        total = count_result.scalar() or 0
        
        # 将结果转换为DataAsset对象
        assets = []
        for row in rows:
            asset = DataAsset(
                id=row.id,
                asset_code=row.asset_code,
                asset_name=row.asset_name,
                organization_id=row.organization_id,
                category=row.category,
                data_classification=row.data_classification,
                sensitivity_level=row.sensitivity_level,
                description=row.description,
                data_source=row.data_source,
                data_volume=row.data_volume,
                data_format=row.data_format,
                update_frequency=row.update_frequency,
                current_stage=row.current_stage,
                status=row.status,
                asset_type=row.asset_type,
                estimated_value=row.estimated_value,
                created_by=row.created_by,
                assigned_to=row.assigned_to,
                version=row.version,
                previous_version_id=row.previous_version_id,
                created_at=row.created_at,
                updated_at=row.updated_at,
                deleted_at=row.deleted_at
            )
            assets.append(asset)
        
        return assets, total
    
    @staticmethod
    async def search_assets_simple(
        db: AsyncSession,
        query: str,
        organization_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[DataAsset], int]:
        """
        简单搜索（不使用中文分词，使用LIKE）
        
        当zhparser不可用时的备选方案
        
        Args:
            db: 数据库会话
            query: 搜索关键词
            organization_id: 组织ID过滤（可选）
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            tuple: (资产列表, 总数)
        """
        from sqlalchemy import or_, and_
        
        # 构建基础查询
        stmt = select(DataAsset).where(
            and_(
                DataAsset.deleted_at.is_(None),
                or_(
                    DataAsset.asset_code.ilike(f"%{query}%"),
                    DataAsset.asset_name.ilike(f"%{query}%"),
                    DataAsset.description.ilike(f"%{query}%"),
                    DataAsset.data_source.ilike(f"%{query}%"),
                    DataAsset.category.ilike(f"%{query}%"),
                    DataAsset.asset_type.ilike(f"%{query}%")
                )
            )
        )
        
        # 组织过滤
        if organization_id:
            stmt = stmt.where(DataAsset.organization_id == organization_id)
        
        # 计数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # 分页和排序
        stmt = stmt.order_by(DataAsset.created_at.desc()).offset(offset).limit(limit)
        
        # 执行查询
        result = await db.execute(stmt)
        assets = list(result.scalars().all())
        
        return assets, total
    
    @staticmethod
    async def search_assets(
        db: AsyncSession,
        query: str,
        organization_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
        use_fulltext: bool = True
    ) -> tuple[List[DataAsset], int]:
        """
        智能搜索 - 自动选择全文搜索或简单搜索
        
        Args:
            db: 数据库会话
            query: 搜索关键词
            organization_id: 组织ID过滤（可选）
            limit: 返回数量限制
            offset: 偏移量
            use_fulltext: 是否尝试使用全文搜索
            
        Returns:
            tuple: (资产列表, 总数)
        """
        if use_fulltext:
            # 尝试使用全文搜索
            try:
                return await SearchService.search_assets_fulltext(
                    db, query, organization_id, limit, offset
                )
            except Exception:
                # 全文搜索失败，降级到简单搜索
                pass
        
        # 使用简单搜索
        return await SearchService.search_assets_simple(
            db, query, organization_id, limit, offset
        )
