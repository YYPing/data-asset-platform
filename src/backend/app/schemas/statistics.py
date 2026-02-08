"""
统计分析 Pydantic 模型
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class OverviewStats(BaseModel):
    """总览统计"""
    total_assets: int = Field(description="资产总数")
    status_counts: dict[str, int] = Field(description="各状态数量")
    stage_counts: dict[str, int] = Field(description="各阶段数量")
    monthly_new: int = Field(description="本月新增")
    pending_approval: int = Field(description="待审批数")


class TrendDataPoint(BaseModel):
    """趋势数据点"""
    month: str = Field(description="月份 YYYY-MM")
    count: int = Field(description="数量")


class TrendStats(BaseModel):
    """趋势统计"""
    data: List[TrendDataPoint] = Field(description="最近12个月数据")


class OrganizationStats(BaseModel):
    """组织统计"""
    organization_id: int
    organization_name: str
    asset_count: int = Field(description="资产数量")
    confirmed_count: int = Field(description="已确权数量")
    total_valuation: float = Field(description="总估值")


class OrganizationStatsResponse(BaseModel):
    """组织统计响应"""
    data: List[OrganizationStats]


class CategoryStats(BaseModel):
    """分类统计"""
    category: str
    count: int
    percentage: float = Field(description="占比")


class CategoryStatsResponse(BaseModel):
    """分类统计响应"""
    data: List[CategoryStats]


class AssessmentStats(BaseModel):
    """评估统计"""
    total_assessments: int = Field(description="总评估数")
    compliance_pass_rate: float = Field(description="合规通过率")
    average_score: float = Field(description="平均评分")
    risk_distribution: dict[str, int] = Field(description="风险分布 {low/medium/high: count}")


class WorkflowStats(BaseModel):
    """审批统计"""
    total_workflows: int = Field(description="总审批数")
    average_duration_hours: float = Field(description="平均审批时长(小时)")
    approval_rate: float = Field(description="通过率")
    rejection_rate: float = Field(description="驳回率")
    timeout_rate: float = Field(description="超时率")


class StatisticsResponse(BaseModel):
    """统计响应基类"""
    code: int = 200
    message: str = "success"
    data: dict | list | OverviewStats | TrendStats | OrganizationStatsResponse | CategoryStatsResponse | AssessmentStats | WorkflowStats
