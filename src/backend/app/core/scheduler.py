"""
定时任务调度器
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 创建调度器实例
scheduler = AsyncIOScheduler()

__all__ = ["scheduler"]