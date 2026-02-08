"""
评估模块 Pydantic 模型
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class AssessmentType(str, Enum):
    """评估类型"""
    COMPLIANCE = "compliance"  # 合规评估
    VALUATION = "valuation"    # 价值评估


class ValuationMethod(str, Enum):
    """价值评估方法"""
    COST = "cost"                    # 成本法
    MARKET = "market"                # 市场法
    INCOME = "income"                # 收益法
    COMPREHENSIVE = "comprehensive"  # 综合法


class RiskLevel(str, Enum):
    """风险等级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AssessmentStatus(str, Enum):
    """评估状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


# ==================== 合规评估相关 ====================

class ComplianceCheckItem(BaseModel):
    """合规检查项"""
    regulation: str = Field(..., description="法规名称：数据安全法/个人信息保护法/网络安全法")
    check_points: List[str] = Field(..., description="检查要点列表")
    score: int = Field(..., ge=0, le=100, description="该项得分")
    issues: Optional[List[str]] = Field(default=None, description="发现的问题")


class ComplianceAssessmentCreate(BaseModel):
    """创建合规评估请求"""
    score: Decimal = Field(..., ge=0, le=100, description="总分(0-100)")
    risk_level: RiskLevel = Field(..., description="风险等级")
    result_summary: str = Field(..., min_length=10, description="评估结果摘要")
    check_items: List[ComplianceCheckItem] = Field(..., min_items=1, description="检查项列表")
    improvement_suggestions: List[str] = Field(..., min_items=1, description="整改建议")
    report_material_id: Optional[int] = Field(default=None, description="评估报告附件ID")

    @field_validator('score')
    @classmethod
    def validate_score(cls, v: Decimal) -> Decimal:
        """验证分数精度"""
        if v.as_tuple().exponent < -2:
            raise ValueError("分数最多保留2位小数")
        return v


# ==================== 价值评估相关 ====================

class ValuationAssessmentCreate(BaseModel):
    """创建价值评估请求"""
    method: ValuationMethod = Field(..., description="评估方法")
    score: Decimal = Field(..., ge=0, description="评估值（单位：万元）")
    result_summary: str = Field(..., min_length=10, description="评估结果摘要")
    method_description: str = Field(..., description="评估方法说明")
    calculation_basis: Optional[str] = Field(default=None, description="计算依据")
    report_material_id: Optional[int] = Field(default=None, description="评估报告附件ID")

    @field_validator('score')
    @classmethod
    def validate_score(cls, v: Decimal) -> Decimal:
        """验证评估值精度"""
        if v.as_tuple().exponent < -2:
            raise ValueError("评估值最多保留2位小数")
        return v


# ==================== 评估更新 ====================

class AssessmentUpdate(BaseModel):
    """更新评估（仅pending/in_progress状态可更新）"""
    score: Optional[Decimal] = Field(default=None, ge=0, description="分数/评估值")
    risk_level: Optional[RiskLevel] = Field(default=None, description="风险等级（仅合规评估）")
    result_summary: Optional[str] = Field(default=None, min_length=10, description="评估结果摘要")
    report_material_id: Optional[int] = Field(default=None, description="评估报告附件ID")
    status: Optional[AssessmentStatus] = Field(default=None, description="状态")

    @field_validator('score')
    @classmethod
    def validate_score(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v.as_tuple().exponent < -2:
            raise ValueError("分数最多保留2位小数")
        return v


class AssessmentComplete(BaseModel):
    """完成评估"""
    final_summary: Optional[str] = Field(default=None, description="最终总结")


# ==================== 评估响应 ====================

class AssessmentRecordResponse(BaseModel):
    """评估记录响应"""
    id: int
    asset_id: int
    asset_name: Optional[str] = None
    assessment_type: AssessmentType
    method: Optional[ValuationMethod] = None
    evaluator_id: int
    evaluator_name: Optional[str] = None
    evaluator_org_id: Optional[int] = None
    evaluator_org_name: Optional[str] = None
    score: Decimal
    risk_level: Optional[RiskLevel] = None
    result_summary: str
    report_material_id: Optional[int] = None
    report_material_name: Optional[str] = None
    status: AssessmentStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssessmentDetailResponse(AssessmentRecordResponse):
    """评估详情响应（包含完整信息）"""
    # 合规评估专属字段
    check_items: Optional[List[ComplianceCheckItem]] = None
    improvement_suggestions: Optional[List[str]] = None
    
    # 价值评估专属字段
    method_description: Optional[str] = None
    calculation_basis: Optional[str] = None


class AssessmentListResponse(BaseModel):
    """评估列表响应"""
    total: int
    items: List[AssessmentRecordResponse]


# ==================== 统一响应格式 ====================

class ApiResponse(BaseModel):
    """统一API响应格式"""
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[dict | list | AssessmentRecordResponse | AssessmentDetailResponse | AssessmentListResponse] = None
