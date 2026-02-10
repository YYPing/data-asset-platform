"""
评估模块 API 路由
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.core.permissions import require_roles
from app.models.user import User
from app.services.assessment import AssessmentService
from app.schemas.assessment import (
    AssessmentType,
    ComplianceAssessmentCreate,
    ValuationAssessmentCreate,
    AssessmentUpdate,
    AssessmentComplete,
    AssessmentRecordResponse,
    AssessmentDetailResponse,
    AssessmentListResponse,
    ApiResponse,
)


router = APIRouter(prefix="", tags=["评估管理"])


def _to_response(assessment) -> dict:
    """转换评估记录为响应格式"""
    return {
        "id": assessment.id,
        "asset_id": assessment.asset_id,
        "asset_name": assessment.asset.name if assessment.asset else None,
        "assessment_type": assessment.assessment_type,
        "method": assessment.method,
        "evaluator_id": assessment.evaluator_id,
        "evaluator_name": assessment.evaluator.username if assessment.evaluator else None,
        "evaluator_org_id": assessment.evaluator_org_id,
        "evaluator_org_name": assessment.evaluator_org.name if assessment.evaluator_org else None,
        "score": float(assessment.score),
        "risk_level": assessment.risk_level,
        "result_summary": assessment.result_summary,
        "report_material_id": assessment.report_material_id,
        "report_material_name": assessment.report_material.file_name if assessment.report_material else None,
        "status": assessment.status,
        "started_at": assessment.started_at.isoformat() if assessment.started_at else None,
        "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
        "created_at": assessment.created_at.isoformat() if assessment.created_at else None,
        "updated_at": assessment.updated_at.isoformat() if assessment.updated_at else None,
    }


@router.post(
    "/compliance/{asset_id}",
    response_model=ApiResponse,
    summary="提交合规评估",
    description="创建合规评估记录，需要 center_user 或 center_admin 角色"
)
async def create_compliance_assessment(
    asset_id: int,
    data: ComplianceAssessmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["center_user", "center_admin"])),
):
    """
    提交合规评估
    
    **权限要求**: center_user 或 center_admin
    
    **业务规则**:
    - 法规检查清单：数据安全法、个人信息保护法、网络安全法
    - 风险等级：high/medium/low（基于检查项打分）
    - 评估结果包含：总分(0-100)、风险等级、整改建议
    
    **请求参数**:
    - score: 总分(0-100)
    - risk_level: 风险等级(high/medium/low)
    - result_summary: 评估结果摘要
    - check_items: 检查项列表
    - improvement_suggestions: 整改建议列表
    - report_material_id: 评估报告附件ID（可选）
    """
    service = AssessmentService(db)
    assessment = await service.create_compliance_assessment(
        asset_id=asset_id,
        data=data,
        current_user=current_user,
    )
    
    return ApiResponse(
        code=200,
        message="合规评估创建成功",
        data=_to_response(assessment),
    )


@router.post(
    "/valuation/{asset_id}",
    response_model=ApiResponse,
    summary="提交价值评估",
    description="创建价值评估记录，需要 evaluator 角色"
)
async def create_valuation_assessment(
    asset_id: int,
    data: ValuationAssessmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["evaluator"])),
):
    """
    提交价值评估
    
    **权限要求**: evaluator（第三方评估机构）
    
    **业务规则**:
    - 评估方法：cost(成本法)/market(市场法)/income(收益法)/comprehensive(综合法)
    - 重大资产(>100万)必须第三方评估
    - 评估结果包含：评估值、评估方法、评估报告
    
    **请求参数**:
    - method: 评估方法
    - score: 评估值（单位：万元）
    - result_summary: 评估结果摘要
    - method_description: 评估方法说明
    - calculation_basis: 计算依据（可选）
    - report_material_id: 评估报告附件ID（可选）
    """
    service = AssessmentService(db)
    assessment = await service.create_valuation_assessment(
        asset_id=asset_id,
        data=data,
        current_user=current_user,
    )
    
    return ApiResponse(
        code=200,
        message="价值评估创建成功",
        data=_to_response(assessment),
    )


@router.get(
    "/{asset_id}",
    response_model=ApiResponse,
    summary="获取资产的所有评估记录",
    description="获取指定资产的所有评估记录列表"
)
async def get_asset_assessments(
    asset_id: int,
    assessment_type: Optional[AssessmentType] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取资产的所有评估记录
    
    **查询参数**:
    - assessment_type: 评估类型过滤（可选，compliance/valuation）
    
    **返回**: 评估记录列表，按创建时间倒序
    """
    service = AssessmentService(db)
    assessments = await service.get_asset_assessments(
        asset_id=asset_id,
        assessment_type=assessment_type,
    )
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "total": len(assessments),
            "items": [_to_response(a) for a in assessments],
        },
    )


@router.get(
    "/{id}/detail",
    response_model=ApiResponse,
    summary="获取评估详情",
    description="获取评估记录的详细信息，包含扩展字段"
)
async def get_assessment_detail(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取评估详情
    
    **返回**: 评估记录详细信息，包含：
    - 合规评估：check_items（检查项）、improvement_suggestions（整改建议）
    - 价值评估：method_description（方法说明）、calculation_basis（计算依据）
    """
    service = AssessmentService(db)
    detail = await service.get_assessment_detail(assessment_id=id)
    
    return ApiResponse(
        code=200,
        message="success",
        data=detail,
    )


@router.put(
    "/{id}",
    response_model=ApiResponse,
    summary="更新评估",
    description="更新评估记录，仅 pending/in_progress 状态可更新"
)
async def update_assessment(
    id: int,
    data: AssessmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新评估
    
    **权限要求**: 评估创建人
    
    **业务规则**:
    - 仅 pending/in_progress 状态可更新
    - 只有评估创建人可以更新
    
    **请求参数**（所有字段可选）:
    - score: 分数/评估值
    - risk_level: 风险等级（仅合规评估）
    - result_summary: 评估结果摘要
    - report_material_id: 评估报告附件ID
    - status: 状态
    """
    service = AssessmentService(db)
    assessment = await service.update_assessment(
        assessment_id=id,
        data=data,
        current_user=current_user,
    )
    
    return ApiResponse(
        code=200,
        message="评估更新成功",
        data=_to_response(assessment),
    )


@router.post(
    "/{id}/complete",
    response_model=ApiResponse,
    summary="完成评估",
    description="将评估状态标记为已完成"
)
async def complete_assessment(
    id: int,
    data: AssessmentComplete,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    完成评估
    
    **权限要求**: 评估创建人
    
    **业务规则**:
    - 只有评估创建人可以完成评估
    - 完成后状态变更为 completed，记录完成时间
    
    **请求参数**:
    - final_summary: 最终总结（可选，会覆盖原有 result_summary）
    """
    service = AssessmentService(db)
    assessment = await service.complete_assessment(
        assessment_id=id,
        final_summary=data.final_summary,
        current_user=current_user,
    )
    
    return ApiResponse(
        code=200,
        message="评估已完成",
        data=_to_response(assessment),
    )


@router.get(
    "/pending",
    response_model=ApiResponse,
    summary="我的待评估列表",
    description="获取当前用户的待评估任务列表"
)
async def get_pending_assessments(
    assessment_type: Optional[AssessmentType] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    我的待评估列表
    
    **查询参数**:
    - assessment_type: 评估类型过滤（可选，compliance/valuation）
    
    **返回**: 当前用户的待评估任务列表（pending/in_progress 状态）
    """
    service = AssessmentService(db)
    assessments = await service.get_pending_assessments(
        current_user=current_user,
        assessment_type=assessment_type,
    )
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "total": len(assessments),
            "items": [_to_response(a) for a in assessments],
        },
    )
