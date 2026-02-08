"""
审计日志服务
"""
from datetime import datetime, timedelta
from typing import Optional, AsyncIterator
from sqlalchemy import select, func, and_, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import csv
import io

from app.models.system import AuditLog
from app.models.user import User
from app.schemas.audit import (
    AuditLogCreate,
    AuditLogResponse,
    AuditLogListQuery,
    AuditLogListResponse,
    AuditStatsResponse,
    AuditStatsActionItem,
    AuditStatsTrendItem,
)


class AuditService:
    """审计日志服务"""

    @staticmethod
    async def create_log(
        db: AsyncSession,
        log_data: AuditLogCreate
    ) -> AuditLog:
        """创建审计日志"""
        log = AuditLog(
            user_id=log_data.user_id,
            action=log_data.action,
            resource_type=log_data.resource_type,
            resource_id=log_data.resource_id,
            detail=log_data.detail,
            ip_address=log_data.ip_address,
            user_agent=log_data.user_agent,
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def get_log_by_id(
        db: AsyncSession,
        log_id: int,
        user_id: Optional[int] = None
    ) -> Optional[AuditLogResponse]:
        """获取审计日志详情"""
        query = select(AuditLog, User).join(
            User, AuditLog.user_id == User.id, isouter=True
        ).where(AuditLog.id == log_id)
        
        # 如果指定了user_id，只能查看自己的日志
        if user_id is not None:
            query = query.where(AuditLog.user_id == user_id)
        
        result = await db.execute(query)
        row = result.first()
        
        if not row:
            return None
        
        audit_log, user = row
        return AuditLogResponse(
            id=audit_log.id,
            user_id=audit_log.user_id,
            action=audit_log.action,
            resource_type=audit_log.resource_type,
            resource_id=audit_log.resource_id,
            detail=audit_log.detail,
            ip_address=audit_log.ip_address,
            user_agent=audit_log.user_agent,
            created_at=audit_log.created_at,
            username=user.username if user else None,
            user_email=user.email if user else None,
        )

    @staticmethod
    async def get_logs(
        db: AsyncSession,
        query_params: AuditLogListQuery,
        current_user_id: Optional[int] = None
    ) -> AuditLogListResponse:
        """获取审计日志列表（分页+筛选）"""
        # 构建基础查询
        query = select(AuditLog, User).join(
            User, AuditLog.user_id == User.id, isouter=True
        )
        
        # 权限过滤：如果指定了current_user_id，只能查看自己的
        if current_user_id is not None:
            query = query.where(AuditLog.user_id == current_user_id)
        
        # 筛选条件
        conditions = []
        if query_params.user_id:
            conditions.append(AuditLog.user_id == query_params.user_id)
        if query_params.action:
            conditions.append(AuditLog.action == query_params.action)
        if query_params.resource_type:
            conditions.append(AuditLog.resource_type == query_params.resource_type)
        if query_params.date_from:
            conditions.append(AuditLog.created_at >= query_params.date_from)
        if query_params.date_to:
            conditions.append(AuditLog.created_at <= query_params.date_to)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 计算总数
        count_query = select(func.count()).select_from(AuditLog)
        if current_user_id is not None:
            count_query = count_query.where(AuditLog.user_id == current_user_id)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        query = query.order_by(AuditLog.created_at.desc())
        query = query.offset((query_params.page - 1) * query_params.page_size)
        query = query.limit(query_params.page_size)
        
        result = await db.execute(query)
        rows = result.all()
        
        # 构建响应
        items = []
        for audit_log, user in rows:
            items.append(AuditLogResponse(
                id=audit_log.id,
                user_id=audit_log.user_id,
                action=audit_log.action,
                resource_type=audit_log.resource_type,
                resource_id=audit_log.resource_id,
                detail=audit_log.detail,
                ip_address=audit_log.ip_address,
                user_agent=audit_log.user_agent,
                created_at=audit_log.created_at,
                username=user.username if user else None,
                user_email=user.email if user else None,
            ))
        
        return AuditLogListResponse(
            total=total,
            page=query_params.page,
            page_size=query_params.page_size,
            items=items,
        )

    @staticmethod
    async def get_stats(
        db: AsyncSession,
        current_user_id: Optional[int] = None
    ) -> AuditStatsResponse:
        """获取审计统计"""
        # 基础条件
        base_condition = []
        if current_user_id is not None:
            base_condition.append(AuditLog.user_id == current_user_id)
        
        # 总数统计
        count_query = select(func.count()).select_from(AuditLog)
        if base_condition:
            count_query = count_query.where(and_(*base_condition))
        total_result = await db.execute(count_query)
        total_count = total_result.scalar() or 0
        
        # 按操作类型统计
        action_query = select(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.action).order_by(func.count(AuditLog.id).desc())
        
        if base_condition:
            action_query = action_query.where(and_(*base_condition))
        
        action_result = await db.execute(action_query)
        action_stats = [
            AuditStatsActionItem(action=row.action, count=row.count)
            for row in action_result.all()
        ]
        
        # 按天统计趋势（最近30天）
        thirty_days_ago = datetime.now() - timedelta(days=30)
        trend_query = select(
            cast(AuditLog.created_at, Date).label('date'),
            func.count(AuditLog.id).label('count')
        ).where(AuditLog.created_at >= thirty_days_ago)
        
        if base_condition:
            trend_query = trend_query.where(and_(*base_condition))
        
        trend_query = trend_query.group_by(cast(AuditLog.created_at, Date))
        trend_query = trend_query.order_by(cast(AuditLog.created_at, Date))
        
        trend_result = await db.execute(trend_query)
        trend_stats = [
            AuditStatsTrendItem(
                date=row.date.strftime('%Y-%m-%d'),
                count=row.count
            )
            for row in trend_result.all()
        ]
        
        return AuditStatsResponse(
            total_count=total_count,
            action_stats=action_stats,
            trend_stats=trend_stats,
        )

    @staticmethod
    async def export_logs_csv(
        db: AsyncSession,
        query_params: AuditLogListQuery,
        current_user_id: Optional[int] = None
    ) -> AsyncIterator[str]:
        """导出审计日志为CSV（流式）"""
        # 构建查询（不分页，导出所有符合条件的）
        query = select(AuditLog, User).join(
            User, AuditLog.user_id == User.id, isouter=True
        )
        
        # 权限过滤
        if current_user_id is not None:
            query = query.where(AuditLog.user_id == current_user_id)
        
        # 筛选条件
        conditions = []
        if query_params.user_id:
            conditions.append(AuditLog.user_id == query_params.user_id)
        if query_params.action:
            conditions.append(AuditLog.action == query_params.action)
        if query_params.resource_type:
            conditions.append(AuditLog.resource_type == query_params.resource_type)
        if query_params.date_from:
            conditions.append(AuditLog.created_at >= query_params.date_from)
        if query_params.date_to:
            conditions.append(AuditLog.created_at <= query_params.date_to)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(AuditLog.created_at.desc())
        
        # CSV头部
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'ID', '用户ID', '用户名', '邮箱', '操作', '资源类型', 
            '资源ID', '详情', 'IP地址', '用户代理', '创建时间'
        ])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)
        
        # 流式查询并写入
        result = await db.stream(query)
        async for audit_log, user in result:
            writer.writerow([
                audit_log.id,
                audit_log.user_id,
                user.username if user else '',
                user.email if user else '',
                audit_log.action,
                audit_log.resource_type or '',
                audit_log.resource_id or '',
                audit_log.detail or '',
                audit_log.ip_address or '',
                audit_log.user_agent or '',
                audit_log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
