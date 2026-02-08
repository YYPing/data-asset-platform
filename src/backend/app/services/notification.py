"""
通知服务
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListQuery,
    NotificationListResponse,
    NotificationType,
)


class NotificationService:
    """通知服务"""

    @staticmethod
    async def send(
        db: AsyncSession,
        user_id: int,
        title: str,
        content: str,
        notification_type: NotificationType = NotificationType.SYSTEM,
        related_type: Optional[str] = None,
        related_id: Optional[str] = None,
    ) -> Notification:
        """发送通知给指定用户"""
        notification = Notification(
            user_id=user_id,
            title=title,
            content=content,
            notification_type=notification_type.value,
            related_type=related_type,
            related_id=related_id,
            is_read=False,
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification

    @staticmethod
    async def send_to_role(
        db: AsyncSession,
        role: str,
        title: str,
        content: str,
        notification_type: NotificationType = NotificationType.SYSTEM,
        related_type: Optional[str] = None,
        related_id: Optional[str] = None,
    ) -> int:
        """发送通知给指定角色的所有用户"""
        # 查询该角色的所有用户
        query = select(User).where(User.role == role, User.is_active == True)
        result = await db.execute(query)
        users = result.scalars().all()
        
        # 批量创建通知
        notifications = []
        for user in users:
            notification = Notification(
                user_id=user.id,
                title=title,
                content=content,
                notification_type=notification_type.value,
                related_type=related_type,
                related_id=related_id,
                is_read=False,
            )
            notifications.append(notification)
        
        if notifications:
            db.add_all(notifications)
            await db.commit()
        
        return len(notifications)

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        user_id: int,
        query_params: NotificationListQuery,
    ) -> NotificationListResponse:
        """获取用户通知列表（分页+筛选）"""
        # 构建查询
        query = select(Notification).where(Notification.user_id == user_id)
        
        # 筛选条件
        conditions = []
        if query_params.notification_type:
            conditions.append(Notification.notification_type == query_params.notification_type.value)
        if query_params.is_read is not None:
            conditions.append(Notification.is_read == query_params.is_read)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 计算总数
        count_query = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id
        )
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        query = query.order_by(Notification.created_at.desc())
        query = query.offset((query_params.page - 1) * query_params.page_size)
        query = query.limit(query_params.page_size)
        
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        # 构建响应
        items = [
            NotificationResponse(
                id=n.id,
                user_id=n.user_id,
                title=n.title,
                content=n.content,
                notification_type=NotificationType(n.notification_type),
                related_type=n.related_type,
                related_id=n.related_id,
                is_read=n.is_read,
                created_at=n.created_at,
                read_at=n.read_at,
            )
            for n in notifications
        ]
        
        return NotificationListResponse(
            total=total,
            page=query_params.page,
            page_size=query_params.page_size,
            items=items,
        )

    @staticmethod
    async def get_unread_count(
        db: AsyncSession,
        user_id: int,
    ) -> int:
        """获取用户未读通知数量"""
        query = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        result = await db.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        notification_id: int,
        user_id: int,
    ) -> bool:
        """标记通知为已读"""
        query = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        result = await db.execute(query)
        notification = result.scalar_one_or_none()
        
        if not notification:
            return False
        
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now()
            await db.commit()
        
        return True

    @staticmethod
    async def mark_all_as_read(
        db: AsyncSession,
        user_id: int,
    ) -> int:
        """标记用户所有通知为已读"""
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
            .values(is_read=True, read_at=datetime.now())
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

    @staticmethod
    async def delete_notification(
        db: AsyncSession,
        notification_id: int,
        user_id: int,
    ) -> bool:
        """删除通知"""
        query = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        result = await db.execute(query)
        notification = result.scalar_one_or_none()
        
        if not notification:
            return False
        
        await db.delete(notification)
        await db.commit()
        return True

    @staticmethod
    async def get_notification_by_id(
        db: AsyncSession,
        notification_id: int,
        user_id: int,
    ) -> Optional[NotificationResponse]:
        """获取通知详情"""
        query = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        result = await db.execute(query)
        notification = result.scalar_one_or_none()
        
        if not notification:
            return None
        
        return NotificationResponse(
            id=notification.id,
            user_id=notification.user_id,
            title=notification.title,
            content=notification.content,
            notification_type=NotificationType(notification.notification_type),
            related_type=notification.related_type,
            related_id=notification.related_id,
            is_read=notification.is_read,
            created_at=notification.created_at,
            read_at=notification.read_at,
        )
