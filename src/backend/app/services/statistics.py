"""
统计分析服务
"""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import DataAsset, Material, RegistrationCertificate
from app.models.workflow import WorkflowInstance, ApprovalRecord
from app.models.assessment import AssessmentRecord
from app.models.user import User, Organization
from app.schemas.statistics import (
    OverviewStats,
    TrendStats,
    TrendDataPoint,
    OrganizationStats,
    CategoryStats,
    AssessmentStats,
    WorkflowStats,
)


class StatisticsService:
    """统计分析服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overview(self, organization_id: Optional[int] = None) -> OverviewStats:
        """
        获取总览统计
        
        Args:
            organization_id: 组织ID（holder角色传入，限制查询范围）
        """
        # 基础查询条件
        base_filter = []
        if organization_id:
            base_filter.append(DataAsset.organization_id == organization_id)

        # 资产总数
        total_query = select(func.count(DataAsset.id)).where(*base_filter)
        total_result = await self.db.execute(total_query)
        total_assets = total_result.scalar() or 0

        # 各状态数量
        status_query = select(
            DataAsset.status,
            func.count(DataAsset.id)
        ).where(*base_filter).group_by(DataAsset.status)
        status_result = await self.db.execute(status_query)
        status_counts = {row[0]: row[1] for row in status_result.all()}

        # 各阶段数量
        stage_query = select(
            DataAsset.stage,
            func.count(DataAsset.id)
        ).where(*base_filter).group_by(DataAsset.stage)
        stage_result = await self.db.execute(stage_query)
        stage_counts = {row[0]: row[1] for row in stage_result.all()}

        # 本月新增
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)
        monthly_filter = base_filter + [DataAsset.created_at >= month_start]
        monthly_query = select(func.count(DataAsset.id)).where(*monthly_filter)
        monthly_result = await self.db.execute(monthly_query)
        monthly_new = monthly_result.scalar() or 0

        # 待审批数（状态为pending的工作流）
        pending_filter = [WorkflowInstance.status == 'pending']
        if organization_id:
            pending_filter.append(
                WorkflowInstance.asset_id.in_(
                    select(DataAsset.id).where(DataAsset.organization_id == organization_id)
                )
            )
        pending_query = select(func.count(WorkflowInstance.id)).where(*pending_filter)
        pending_result = await self.db.execute(pending_query)
        pending_approval = pending_result.scalar() or 0

        return OverviewStats(
            total_assets=total_assets,
            status_counts=status_counts,
            stage_counts=stage_counts,
            monthly_new=monthly_new,
            pending_approval=pending_approval,
        )

    async def get_trend(self, organization_id: Optional[int] = None) -> TrendStats:
        """
        获取趋势统计（最近12个月）
        
        Args:
            organization_id: 组织ID（holder角色传入）
        """
        # 计算12个月前的日期
        now = datetime.now()
        twelve_months_ago = now - timedelta(days=365)

        # 基础查询条件
        base_filter = [DataAsset.created_at >= twelve_months_ago]
        if organization_id:
            base_filter.append(DataAsset.organization_id == organization_id)

        # 按月统计
        query = select(
            extract('year', DataAsset.created_at).label('year'),
            extract('month', DataAsset.created_at).label('month'),
            func.count(DataAsset.id).label('count')
        ).where(*base_filter).group_by('year', 'month').order_by('year', 'month')

        result = await self.db.execute(query)
        rows = result.all()

        # 构建完整的12个月数据（填充空缺月份）
        data_points = []
        current = twelve_months_ago.replace(day=1)
        month_data = {f"{int(row.year)}-{int(row.month):02d}": row.count for row in rows}

        for _ in range(12):
            month_key = current.strftime("%Y-%m")
            count = month_data.get(month_key, 0)
            data_points.append(TrendDataPoint(month=month_key, count=count))
            # 移动到下个月
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        return TrendStats(data=data_points)

    async def get_by_organization(self, organization_id: Optional[int] = None) -> List[OrganizationStats]:
        """
        按组织统计
        
        Args:
            organization_id: 组织ID（holder角色传入，只返回该组织）
        """
        # 基础查询
        query = select(
            Organization.id,
            Organization.name,
            func.count(DataAsset.id).label('asset_count'),
            func.sum(
                func.cast(DataAsset.status == 'confirmed', func.Integer())
            ).label('confirmed_count'),
            func.coalesce(func.sum(DataAsset.valuation), 0).label('total_valuation')
        ).join(
            DataAsset, DataAsset.organization_id == Organization.id, isouter=True
        )

        # 如果是holder角色，只查询自己的组织
        if organization_id:
            query = query.where(Organization.id == organization_id)

        query = query.group_by(Organization.id, Organization.name)

        result = await self.db.execute(query)
        rows = result.all()

        return [
            OrganizationStats(
                organization_id=row.id,
                organization_name=row.name,
                asset_count=row.asset_count or 0,
                confirmed_count=row.confirmed_count or 0,
                total_valuation=float(row.total_valuation or 0),
            )
            for row in rows
        ]

    async def get_by_category(self, organization_id: Optional[int] = None) -> List[CategoryStats]:
        """
        按分类统计
        
        Args:
            organization_id: 组织ID（holder角色传入）
        """
        # 基础查询条件
        base_filter = []
        if organization_id:
            base_filter.append(DataAsset.organization_id == organization_id)

        # 总数
        total_query = select(func.count(DataAsset.id)).where(*base_filter)
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0

        # 按分类统计
        query = select(
            DataAsset.category,
            func.count(DataAsset.id).label('count')
        ).where(*base_filter).group_by(DataAsset.category)

        result = await self.db.execute(query)
        rows = result.all()

        return [
            CategoryStats(
                category=row.category or 'unknown',
                count=row.count,
                percentage=round((row.count / total * 100) if total > 0 else 0, 2),
            )
            for row in rows
        ]

    async def get_assessment_stats(self, organization_id: Optional[int] = None) -> AssessmentStats:
        """
        评估统计
        
        Args:
            organization_id: 组织ID（holder角色传入）
        """
        # 基础查询条件
        base_filter = []
        if organization_id:
            base_filter.append(
                AssessmentRecord.asset_id.in_(
                    select(DataAsset.id).where(DataAsset.organization_id == organization_id)
                )
            )

        # 总评估数
        total_query = select(func.count(AssessmentRecord.id)).where(*base_filter)
        total_result = await self.db.execute(total_query)
        total_assessments = total_result.scalar() or 0

        # 合规通过率
        pass_filter = base_filter + [AssessmentRecord.compliance_status == 'pass']
        pass_query = select(func.count(AssessmentRecord.id)).where(*pass_filter)
        pass_result = await self.db.execute(pass_query)
        pass_count = pass_result.scalar() or 0
        compliance_pass_rate = round((pass_count / total_assessments * 100) if total_assessments > 0 else 0, 2)

        # 平均评分
        avg_query = select(func.avg(AssessmentRecord.score)).where(*base_filter)
        avg_result = await self.db.execute(avg_query)
        average_score = round(float(avg_result.scalar() or 0), 2)

        # 风险分布
        risk_query = select(
            AssessmentRecord.risk_level,
            func.count(AssessmentRecord.id)
        ).where(*base_filter).group_by(AssessmentRecord.risk_level)
        risk_result = await self.db.execute(risk_query)
        risk_distribution = {row[0] or 'unknown': row[1] for row in risk_result.all()}

        return AssessmentStats(
            total_assessments=total_assessments,
            compliance_pass_rate=compliance_pass_rate,
            average_score=average_score,
            risk_distribution=risk_distribution,
        )

    async def get_workflow_stats(self, organization_id: Optional[int] = None) -> WorkflowStats:
        """
        审批统计
        
        Args:
            organization_id: 组织ID（holder角色传入）
        """
        # 基础查询条件
        base_filter = []
        if organization_id:
            base_filter.append(
                WorkflowInstance.asset_id.in_(
                    select(DataAsset.id).where(DataAsset.organization_id == organization_id)
                )
            )

        # 总审批数
        total_query = select(func.count(WorkflowInstance.id)).where(*base_filter)
        total_result = await self.db.execute(total_query)
        total_workflows = total_result.scalar() or 0

        # 平均审批时长（已完成的）
        completed_filter = base_filter + [
            WorkflowInstance.status.in_(['approved', 'rejected']),
            WorkflowInstance.completed_at.isnot(None)
        ]
        duration_query = select(
            func.avg(
                func.extract('epoch', WorkflowInstance.completed_at - WorkflowInstance.created_at) / 3600
            )
        ).where(*completed_filter)
        duration_result = await self.db.execute(duration_query)
        average_duration_hours = round(float(duration_result.scalar() or 0), 2)

        # 通过率
        approved_filter = base_filter + [WorkflowInstance.status == 'approved']
        approved_query = select(func.count(WorkflowInstance.id)).where(*approved_filter)
        approved_result = await self.db.execute(approved_query)
        approved_count = approved_result.scalar() or 0
        approval_rate = round((approved_count / total_workflows * 100) if total_workflows > 0 else 0, 2)

        # 驳回率
        rejected_filter = base_filter + [WorkflowInstance.status == 'rejected']
        rejected_query = select(func.count(WorkflowInstance.id)).where(*rejected_filter)
        rejected_result = await self.db.execute(rejected_query)
        rejected_count = rejected_result.scalar() or 0
        rejection_rate = round((rejected_count / total_workflows * 100) if total_workflows > 0 else 0, 2)

        # 超时率（假设超时标记在is_timeout字段）
        timeout_filter = base_filter + [WorkflowInstance.is_timeout == True]
        timeout_query = select(func.count(WorkflowInstance.id)).where(*timeout_filter)
        timeout_result = await self.db.execute(timeout_query)
        timeout_count = timeout_result.scalar() or 0
        timeout_rate = round((timeout_count / total_workflows * 100) if total_workflows > 0 else 0, 2)

        return WorkflowStats(
            total_workflows=total_workflows,
            average_duration_hours=average_duration_hours,
            approval_rate=approval_rate,
            rejection_rate=rejection_rate,
            timeout_rate=timeout_rate,
        )
