"""
评估模块业务逻辑服务
"""
import json
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.assessment import AssessmentRecord
from app.models.asset import DataAsset, Material
from app.models.user import User
from app.models.organization import Organization
from app.schemas.assessment import (
    AssessmentType,
    AssessmentStatus,
    RiskLevel,
    ValuationMethod,
    ComplianceAssessmentCreate,
    ValuationAssessmentCreate,
    AssessmentUpdate,
    AssessmentRecordResponse,
    AssessmentDetailResponse,
)


class AssessmentService:
    """评估服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_asset_or_404(self, asset_id: int) -> DataAsset:
        """获取资产，不存在则抛出404"""
        result = await self.db.execute(
            select(DataAsset).where(DataAsset.id == asset_id)
        )
        asset = result.scalar_one_or_none()
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"资产ID {asset_id} 不存在"
            )
        return asset

    async def _get_assessment_or_404(self, assessment_id: int) -> AssessmentRecord:
        """获取评估记录，不存在则抛出404"""
        result = await self.db.execute(
            select(AssessmentRecord)
            .options(
                selectinload(AssessmentRecord.asset),
                selectinload(AssessmentRecord.evaluator),
                selectinload(AssessmentRecord.evaluator_org),
                selectinload(AssessmentRecord.report_material),
            )
            .where(AssessmentRecord.id == assessment_id)
        )
        assessment = result.scalar_one_or_none()
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"评估记录ID {assessment_id} 不存在"
            )
        return assessment

    async def _check_material_exists(self, material_id: Optional[int]) -> None:
        """检查附件是否存在"""
        if material_id:
            result = await self.db.execute(
                select(Material).where(Material.id == material_id)
            )
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"附件ID {material_id} 不存在"
                )

    async def create_compliance_assessment(
        self,
        asset_id: int,
        data: ComplianceAssessmentCreate,
        current_user: User,
    ) -> AssessmentRecord:
        """
        创建合规评估
        
        权限要求：center_user 或 center_admin
        """
        # 验证资产存在
        asset = await self._get_asset_or_404(asset_id)

        # 验证附件存在
        await self._check_material_exists(data.report_material_id)

        # 创建评估记录
        assessment = AssessmentRecord(
            asset_id=asset_id,
            assessment_type=AssessmentType.COMPLIANCE.value,
            evaluator_id=current_user.id,
            evaluator_org_id=current_user.org_id,
            score=data.score,
            risk_level=data.risk_level.value,
            result_summary=data.result_summary,
            report_material_id=data.report_material_id,
            status=AssessmentStatus.IN_PROGRESS.value,
            started_at=datetime.utcnow(),
            # 存储扩展信息到JSON字段（假设模型有extra_data字段）
            extra_data=json.dumps({
                "check_items": [item.model_dump() for item in data.check_items],
                "improvement_suggestions": data.improvement_suggestions,
            }, ensure_ascii=False),
        )

        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)

        # 记录审计日志
        await self._log_audit(
            user_id=current_user.id,
            action="CREATE_COMPLIANCE_ASSESSMENT",
            resource_type="assessment",
            resource_id=assessment.id,
            details=f"为资产 {asset.name} 创建合规评估，风险等级：{data.risk_level.value}",
        )

        return assessment

    async def create_valuation_assessment(
        self,
        asset_id: int,
        data: ValuationAssessmentCreate,
        current_user: User,
    ) -> AssessmentRecord:
        """
        创建价值评估
        
        权限要求：evaluator（第三方评估机构）
        业务规则：重大资产(>100万)必须第三方评估
        """
        # 验证资产存在
        asset = await self._get_asset_or_404(asset_id)

        # 验证附件存在
        await self._check_material_exists(data.report_material_id)

        # 检查重大资产规则
        if data.score > Decimal("100"):
            # 验证评估人是第三方评估机构
            if current_user.role != "evaluator":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="重大资产(>100万)必须由第三方评估机构评估"
                )

        # 创建评估记录
        assessment = AssessmentRecord(
            asset_id=asset_id,
            assessment_type=AssessmentType.VALUATION.value,
            method=data.method.value,
            evaluator_id=current_user.id,
            evaluator_org_id=current_user.org_id,
            score=data.score,
            result_summary=data.result_summary,
            report_material_id=data.report_material_id,
            status=AssessmentStatus.IN_PROGRESS.value,
            started_at=datetime.utcnow(),
            extra_data=json.dumps({
                "method_description": data.method_description,
                "calculation_basis": data.calculation_basis,
            }, ensure_ascii=False),
        )

        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)

        # 记录审计日志
        await self._log_audit(
            user_id=current_user.id,
            action="CREATE_VALUATION_ASSESSMENT",
            resource_type="assessment",
            resource_id=assessment.id,
            details=f"为资产 {asset.name} 创建价值评估，评估值：{data.score}万元，方法：{data.method.value}",
        )

        return assessment

    async def get_asset_assessments(
        self,
        asset_id: int,
        assessment_type: Optional[AssessmentType] = None,
    ) -> List[AssessmentRecord]:
        """获取资产的所有评估记录"""
        await self._get_asset_or_404(asset_id)

        query = select(AssessmentRecord).options(
            selectinload(AssessmentRecord.evaluator),
            selectinload(AssessmentRecord.evaluator_org),
            selectinload(AssessmentRecord.report_material),
        ).where(AssessmentRecord.asset_id == asset_id)

        if assessment_type:
            query = query.where(AssessmentRecord.assessment_type == assessment_type.value)

        query = query.order_by(AssessmentRecord.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_assessment_detail(self, assessment_id: int) -> Dict[str, Any]:
        """获取评估详情（包含扩展信息）"""
        assessment = await self._get_assessment_or_404(assessment_id)

        # 基础信息
        detail = {
            "id": assessment.id,
            "asset_id": assessment.asset_id,
            "asset_name": assessment.asset.name if assessment.asset else None,
            "assessment_type": assessment.assessment_type,
            "method": assessment.method,
            "evaluator_id": assessment.evaluator_id,
            "evaluator_name": assessment.evaluator.username if assessment.evaluator else None,
            "evaluator_org_id": assessment.evaluator_org_id,
            "evaluator_org_name": assessment.evaluator_org.name if assessment.evaluator_org else None,
            "score": assessment.score,
            "risk_level": assessment.risk_level,
            "result_summary": assessment.result_summary,
            "report_material_id": assessment.report_material_id,
            "report_material_name": assessment.report_material.file_name if assessment.report_material else None,
            "status": assessment.status,
            "started_at": assessment.started_at,
            "completed_at": assessment.completed_at,
            "created_at": assessment.created_at,
            "updated_at": assessment.updated_at,
        }

        # 解析扩展信息
        if assessment.extra_data:
            try:
                extra = json.loads(assessment.extra_data)
                detail.update(extra)
            except json.JSONDecodeError:
                pass

        return detail

    async def update_assessment(
        self,
        assessment_id: int,
        data: AssessmentUpdate,
        current_user: User,
    ) -> AssessmentRecord:
        """
        更新评估（仅pending/in_progress状态可更新）
        
        权限要求：评估创建人
        """
        assessment = await self._get_assessment_or_404(assessment_id)

        # 验证权限：只有创建人可以更新
        if assessment.evaluator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有评估创建人可以更新评估"
            )

        # 验证状态：只有pending/in_progress可更新
        if assessment.status not in [AssessmentStatus.PENDING.value, AssessmentStatus.IN_PROGRESS.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"评估状态为 {assessment.status}，无法更新"
            )

        # 验证附件存在
        if data.report_material_id:
            await self._check_material_exists(data.report_material_id)

        # 更新字段
        update_fields = []
        if data.score is not None:
            assessment.score = data.score
            update_fields.append("score")
        if data.risk_level is not None:
            assessment.risk_level = data.risk_level.value
            update_fields.append("risk_level")
        if data.result_summary is not None:
            assessment.result_summary = data.result_summary
            update_fields.append("result_summary")
        if data.report_material_id is not None:
            assessment.report_material_id = data.report_material_id
            update_fields.append("report_material_id")
        if data.status is not None:
            assessment.status = data.status.value
            update_fields.append("status")

        assessment.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(assessment)

        # 记录审计日志
        await self._log_audit(
            user_id=current_user.id,
            action="UPDATE_ASSESSMENT",
            resource_type="assessment",
            resource_id=assessment.id,
            details=f"更新评估字段：{', '.join(update_fields)}",
        )

        return assessment

    async def complete_assessment(
        self,
        assessment_id: int,
        final_summary: Optional[str],
        current_user: User,
    ) -> AssessmentRecord:
        """
        完成评估
        
        权限要求：评估创建人
        """
        assessment = await self._get_assessment_or_404(assessment_id)

        # 验证权限
        if assessment.evaluator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有评估创建人可以完成评估"
            )

        # 验证状态
        if assessment.status == AssessmentStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="评估已完成"
            )

        # 更新状态
        assessment.status = AssessmentStatus.COMPLETED.value
        assessment.completed_at = datetime.utcnow()
        if final_summary:
            assessment.result_summary = final_summary
        assessment.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(assessment)

        # 记录审计日志
        await self._log_audit(
            user_id=current_user.id,
            action="COMPLETE_ASSESSMENT",
            resource_type="assessment",
            resource_id=assessment.id,
            details=f"完成评估，类型：{assessment.assessment_type}",
        )

        return assessment

    async def get_pending_assessments(
        self,
        current_user: User,
        assessment_type: Optional[AssessmentType] = None,
    ) -> List[AssessmentRecord]:
        """获取当前用户的待评估列表"""
        query = select(AssessmentRecord).options(
            selectinload(AssessmentRecord.asset),
            selectinload(AssessmentRecord.evaluator_org),
        ).where(
            and_(
                AssessmentRecord.evaluator_id == current_user.id,
                or_(
                    AssessmentRecord.status == AssessmentStatus.PENDING.value,
                    AssessmentRecord.status == AssessmentStatus.IN_PROGRESS.value,
                )
            )
        )

        if assessment_type:
            query = query.where(AssessmentRecord.assessment_type == assessment_type.value)

        query = query.order_by(AssessmentRecord.started_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _log_audit(
        self,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: int,
        details: str,
    ) -> None:
        """
        记录审计日志
        
        注意：这里假设存在 AuditLog 模型，实际项目中需要根据实际情况调整
        """
        try:
            from app.models.audit import AuditLog
            
            log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                ip_address=None,  # 可以从请求中获取
                created_at=datetime.utcnow(),
            )
            self.db.add(log)
            await self.db.flush()
        except ImportError:
            # 如果审计日志模型不存在，静默失败
            pass
        except Exception as e:
            # 审计日志失败不应影响主业务
            print(f"审计日志记录失败: {e}")
