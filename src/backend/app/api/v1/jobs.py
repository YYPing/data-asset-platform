"""
异步任务管理路由
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.system import AsyncJob

router = APIRouter(prefix="", tags=["jobs"])


class JobResponse(BaseModel):
    """任务响应模型"""
    id: int
    job_name: str
    job_type: str
    status: str
    params: Optional[dict] = None
    result: Optional[dict] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int
    max_retries: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """任务列表响应"""
    code: int = 200
    message: str = "success"
    data: dict


class JobDetailResponse(BaseModel):
    """任务详情响应"""
    code: int = 200
    message: str = "success"
    data: JobResponse


class JobRetryResponse(BaseModel):
    """任务重试响应"""
    code: int = 200
    message: str = "success"
    data: dict


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选: pending/running/completed/failed"),
    job_type: Optional[str] = Query(None, description="任务类型筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取异步任务列表
    
    支持分页和筛选
    """
    # 构建查询条件
    filters = []
    
    # 非管理员只能查看自己创建的任务
    if current_user.role not in ['center_admin', 'center_user']:
        filters.append(AsyncJob.created_by == current_user.id)
    
    if status:
        filters.append(AsyncJob.status == status)
    
    if job_type:
        filters.append(AsyncJob.job_type == job_type)
    
    # 查询总数
    count_query = select(AsyncJob).where(*filters)
    count_result = await db.execute(select(AsyncJob.id).where(*filters))
    total = len(count_result.all())
    
    # 分页查询
    offset = (page - 1) * page_size
    query = (
        select(AsyncJob)
        .where(*filters)
        .order_by(AsyncJob.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return JobListResponse(
        code=200,
        message="success",
        data={
            "items": [JobResponse.model_validate(job).model_dump() for job in jobs],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    )


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取任务详情
    """
    query = select(AsyncJob).where(AsyncJob.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 权限检查：非管理员只能查看自己的任务
    if current_user.role not in ['center_admin', 'center_user']:
        if job.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="无权限查看此任务")
    
    return JobDetailResponse(
        code=200,
        message="success",
        data=JobResponse.model_validate(job).model_dump()
    )


@router.post("/{job_id}/retry", response_model=JobRetryResponse)
async def retry_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    重试失败的任务
    
    只能重试状态为failed的任务
    """
    query = select(AsyncJob).where(AsyncJob.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 权限检查：非管理员只能重试自己的任务
    if current_user.role not in ['center_admin', 'center_user']:
        if job.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="无权限操作此任务")
    
    # 状态检查
    if job.status != 'failed':
        raise HTTPException(status_code=400, detail="只能重试失败的任务")
    
    # 检查重试次数
    if job.retry_count >= job.max_retries:
        raise HTTPException(
            status_code=400,
            detail=f"已达到最大重试次数 ({job.max_retries})"
        )
    
    # 重置任务状态
    job.status = 'pending'
    job.retry_count += 1
    job.error_message = None
    job.started_at = None
    job.completed_at = None
    job.updated_at = datetime.now()
    
    await db.commit()
    await db.refresh(job)
    
    # TODO: 触发任务执行
    # await task_executor.execute(job)
    
    return JobRetryResponse(
        code=200,
        message="任务已重新提交",
        data={
            "job_id": job.id,
            "status": job.status,
            "retry_count": job.retry_count,
            "max_retries": job.max_retries,
        }
    )


@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除任务记录
    
    只能删除已完成或失败的任务
    """
    query = select(AsyncJob).where(AsyncJob.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 权限检查：非管理员只能删除自己的任务
    if current_user.role not in ['center_admin', 'center_user']:
        if job.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="无权限操作此任务")
    
    # 状态检查
    if job.status in ['pending', 'running']:
        raise HTTPException(status_code=400, detail="不能删除进行中的任务")
    
    await db.delete(job)
    await db.commit()
    
    return {
        "code": 200,
        "message": "任务已删除",
        "data": {"job_id": job_id}
    }


@router.get("/statistics/summary")
async def get_job_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取任务统计摘要
    """
    from sqlalchemy import func
    
    # 构建基础过滤条件
    filters = []
    if current_user.role not in ['center_admin', 'center_user']:
        filters.append(AsyncJob.created_by == current_user.id)
    
    # 按状态统计
    status_query = (
        select(
            AsyncJob.status,
            func.count(AsyncJob.id).label('count')
        )
        .where(*filters)
        .group_by(AsyncJob.status)
    )
    status_result = await db.execute(status_query)
    status_stats = {row.status: row.count for row in status_result.all()}
    
    # 按类型统计
    type_query = (
        select(
            AsyncJob.job_type,
            func.count(AsyncJob.id).label('count')
        )
        .where(*filters)
        .group_by(AsyncJob.job_type)
    )
    type_result = await db.execute(type_query)
    type_stats = {row.job_type: row.count for row in type_result.all()}
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "by_status": status_stats,
            "by_type": type_stats,
            "total": sum(status_stats.values()),
        }
    }
