"""
定时任务调度服务
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.asset import DataAsset, RegistrationCertificate
from app.models.workflow import WorkflowInstance, ApprovalRecord
from app.models.system import AsyncJob
from app.core.config import settings

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务调度服务"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        self._setup_jobs()

    def _setup_jobs(self):
        """配置定时任务"""
        # 1. 证书过期检查（每天凌晨2点）
        self.scheduler.add_job(
            self.check_certificate_expiry,
            CronTrigger(hour=2, minute=0),
            id="check_certificate_expiry",
            name="证书过期检查",
            replace_existing=True,
        )

        # 2. 审批超时检查（每小时）
        self.scheduler.add_job(
            self.check_approval_timeout,
            CronTrigger(minute=0),
            id="check_approval_timeout",
            name="审批超时检查",
            replace_existing=True,
        )

        # 3. 统计数据刷新（每天凌晨3点）
        self.scheduler.add_job(
            self.refresh_statistics_cache,
            CronTrigger(hour=3, minute=0),
            id="refresh_statistics_cache",
            name="统计数据刷新",
            replace_existing=True,
        )

        # 4. 异步任务清理（每周日凌晨4点）
        self.scheduler.add_job(
            self.cleanup_async_jobs,
            CronTrigger(day_of_week='sun', hour=4, minute=0),
            id="cleanup_async_jobs",
            name="异步任务清理",
            replace_existing=True,
        )

    async def check_certificate_expiry(self):
        """
        证书过期检查
        
        检查30天内到期的证书，发送通知
        """
        logger.info("开始执行证书过期检查任务")
        
        try:
            async for db in get_db():
                # 计算30天后的日期
                thirty_days_later = datetime.now() + timedelta(days=30)
                
                # 查询30天内到期的证书
                query = select(RegistrationCertificate).where(
                    and_(
                        RegistrationCertificate.expiry_date.isnot(None),
                        RegistrationCertificate.expiry_date <= thirty_days_later,
                        RegistrationCertificate.expiry_date >= datetime.now(),
                        RegistrationCertificate.status == 'active'
                    )
                )
                
                result = await db.execute(query)
                expiring_certs = result.scalars().all()
                
                logger.info(f"发现 {len(expiring_certs)} 个即将过期的证书")
                
                # 发送通知（这里简化处理，实际应调用通知服务）
                for cert in expiring_certs:
                    days_left = (cert.expiry_date - datetime.now()).days
                    logger.warning(
                        f"证书即将过期: ID={cert.id}, "
                        f"资产ID={cert.asset_id}, "
                        f"剩余天数={days_left}"
                    )
                    
                    # TODO: 调用通知服务发送邮件/站内信
                    # await notification_service.send(
                    #     user_id=cert.asset.owner_id,
                    #     title="证书即将过期提醒",
                    #     content=f"您的资产证书将在{days_left}天后过期，请及时续期"
                    # )
                
                await db.commit()
                logger.info("证书过期检查任务完成")
                
        except Exception as e:
            logger.error(f"证书过期检查任务失败: {str(e)}", exc_info=True)

    async def check_approval_timeout(self):
        """
        审批超时检查
        
        检查超时的审批节点，发送提醒通知
        """
        logger.info("开始执行审批超时检查任务")
        
        try:
            async for db in get_db():
                # 查询pending状态且超时的工作流（假设超时时间为72小时）
                timeout_threshold = datetime.now() - timedelta(hours=72)
                
                query = select(WorkflowInstance).where(
                    and_(
                        WorkflowInstance.status == 'pending',
                        WorkflowInstance.created_at < timeout_threshold,
                        or_(
                            WorkflowInstance.is_timeout.is_(None),
                            WorkflowInstance.is_timeout == False
                        )
                    )
                )
                
                result = await db.execute(query)
                timeout_workflows = result.scalars().all()
                
                logger.info(f"发现 {len(timeout_workflows)} 个超时审批")
                
                # 标记为超时并发送通知
                for workflow in timeout_workflows:
                    workflow.is_timeout = True
                    
                    hours_elapsed = (datetime.now() - workflow.created_at).total_seconds() / 3600
                    logger.warning(
                        f"审批超时: ID={workflow.id}, "
                        f"资产ID={workflow.asset_id}, "
                        f"已耗时={hours_elapsed:.1f}小时"
                    )
                    
                    # TODO: 发送通知给当前审批人
                    # current_approver = await get_current_approver(workflow)
                    # await notification_service.send(
                    #     user_id=current_approver.id,
                    #     title="审批超时提醒",
                    #     content=f"工作流{workflow.id}已超时，请尽快处理"
                    # )
                
                await db.commit()
                logger.info("审批超时检查任务完成")
                
        except Exception as e:
            logger.error(f"审批超时检查任务失败: {str(e)}", exc_info=True)

    async def refresh_statistics_cache(self):
        """
        统计数据刷新
        
        预计算统计数据并缓存（可使用Redis等缓存系统）
        """
        logger.info("开始执行统计数据刷新任务")
        
        try:
            async for db in get_db():
                from app.services.statistics import StatisticsService
                
                service = StatisticsService(db)
                
                # 预计算全局统计数据
                overview = await service.get_overview()
                trend = await service.get_trend()
                by_org = await service.get_by_organization()
                by_category = await service.get_by_category()
                assessment = await service.get_assessment_stats()
                workflow = await service.get_workflow_stats()
                
                logger.info("统计数据计算完成:")
                logger.info(f"  - 资产总数: {overview.total_assets}")
                logger.info(f"  - 组织数: {len(by_org)}")
                logger.info(f"  - 分类数: {len(by_category)}")
                
                # TODO: 将统计结果缓存到Redis
                # await redis_client.setex(
                #     "stats:overview",
                #     3600 * 24,  # 缓存24小时
                #     overview.model_dump_json()
                # )
                
                logger.info("统计数据刷新任务完成")
                
        except Exception as e:
            logger.error(f"统计数据刷新任务失败: {str(e)}", exc_info=True)

    async def cleanup_async_jobs(self):
        """
        异步任务清理
        
        清理30天前已完成的异步任务记录
        """
        logger.info("开始执行异步任务清理任务")
        
        try:
            async for db in get_db():
                # 计算30天前的日期
                thirty_days_ago = datetime.now() - timedelta(days=30)
                
                # 查询需要清理的任务
                query = select(AsyncJob).where(
                    and_(
                        AsyncJob.status.in_(['completed', 'failed']),
                        AsyncJob.completed_at.isnot(None),
                        AsyncJob.completed_at < thirty_days_ago
                    )
                )
                
                result = await db.execute(query)
                old_jobs = result.scalars().all()
                
                logger.info(f"发现 {len(old_jobs)} 个待清理的任务")
                
                # 删除旧任务
                for job in old_jobs:
                    await db.delete(job)
                
                await db.commit()
                logger.info(f"异步任务清理完成，已删除 {len(old_jobs)} 条记录")
                
        except Exception as e:
            logger.error(f"异步任务清理任务失败: {str(e)}", exc_info=True)

    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("定时任务调度器已启动")
            logger.info(f"已注册 {len(self.scheduler.get_jobs())} 个定时任务:")
            for job in self.scheduler.get_jobs():
                logger.info(f"  - {job.name} (ID: {job.id})")

    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("定时任务调度器已关闭")


# 全局调度器实例
scheduler_service = SchedulerService()


def get_scheduler() -> SchedulerService:
    """获取调度器实例"""
    return scheduler_service
