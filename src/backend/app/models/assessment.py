"""
Assessment Record model
评估记录模型

Tables:
- assessment_records: 评估记录表
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Numeric, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User, Organization
    from app.models.asset import DataAsset, Material


class AssessmentRecord(Base):
    """
    Assessment Record model - 评估记录表
    
    记录数据资产的各类评估信息，包括合规评估、价值评估等
    """
    
    __tablename__ = "assessment_records"
    __table_args__ = (
        # 索引
        Index('idx_assessment_records_asset', 'asset_id'),
        Index('idx_assessment_records_type', 'assessment_type'),
        Index('idx_assessment_records_evaluator', 'evaluator_id'),
        Index('idx_assessment_records_evaluator_org', 'evaluator_org_id'),
        Index('idx_assessment_records_status', 'status'),
        Index('idx_assessment_records_started_at', 'started_at'),
        # 复合索引
        Index('idx_assessment_records_asset_type', 'asset_id', 'assessment_type'),
        Index('idx_assessment_records_asset_status', 'asset_id', 'status'),
        # 检查约束
        CheckConstraint(
            "assessment_type IN ('compliance', 'value', 'quality', 'security', 'comprehensive')",
            name='ck_assessment_records_type'
        ),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'cancelled', 'failed')",
            name='ck_assessment_records_status'
        ),
        CheckConstraint(
            "method IS NULL OR method IN ('cost', 'market', 'income', 'expert', 'hybrid')",
            name='ck_assessment_records_method'
        ),
        CheckConstraint(
            "risk_level IS NULL OR risk_level IN ('low', 'medium', 'high', 'critical')",
            name='ck_assessment_records_risk'
        ),
        CheckConstraint(
            "score IS NULL OR (score >= 0 AND score <= 100)",
            name='ck_assessment_records_score'
        ),
        {'comment': '评估记录表'}
    )
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="主键ID")
    
    # 关联资产
    asset_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("data_assets.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联资产ID"
    )
    
    # 评估类型和方法
    assessment_type: Mapped[str] = mapped_column(
        String(30), 
        nullable=False,
        comment="评估类型：compliance/value/quality/security/comprehensive"
    )
    method: Mapped[Optional[str]] = mapped_column(
        String(30), 
        nullable=True,
        comment="评估方法：cost/market/income/expert/hybrid"
    )
    
    # 评估人信息
    evaluator_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="评估人ID"
    )
    evaluator_org_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        comment="评估机构ID"
    )
    
    # 评估结果
    score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), 
        nullable=True,
        comment="评估得分（0-100）"
    )
    risk_level: Mapped[Optional[str]] = mapped_column(
        String(10), 
        nullable=True,
        comment="风险等级：low/medium/high/critical"
    )
    result_summary: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="评估结果摘要"
    )
    
    # 评估报告
    report_material_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("materials.id", ondelete="SET NULL"),
        nullable=True,
        comment="评估报告材料ID"
    )
    
    # 状态
    status: Mapped[str] = mapped_column(
        String(20), 
        default="pending", 
        server_default="pending",
        comment="状态：pending/in_progress/completed/cancelled/failed"
    )
    
    # 时间信息
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        comment="开始时间"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="完成时间"
    )
    
    # ==================== Relationships ====================
    
    # 关联资产
    asset: Mapped["DataAsset"] = relationship(
        "DataAsset",
        back_populates="assessment_records",
        foreign_keys=[asset_id]
    )
    
    # 评估人
    evaluator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="assessment_records",
        foreign_keys=[evaluator_id]
    )
    
    # 评估机构
    evaluator_org: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        back_populates="assessment_records",
        foreign_keys=[evaluator_org_id]
    )
    
    # 评估报告材料
    report_material: Mapped[Optional["Material"]] = relationship(
        "Material",
        back_populates="assessment_records",
        foreign_keys=[report_material_id]
    )
    
    # ==================== Properties ====================
    
    @property
    def is_completed(self) -> bool:
        """Check if assessment is completed"""
        return self.status == 'completed'
    
    @property
    def is_passed(self) -> bool:
        """Check if assessment is passed (score >= 60)"""
        if self.score is None:
            return False
        return self.score >= 60
    
    @property
    def duration_hours(self) -> Optional[float]:
        """Calculate assessment duration in hours"""
        if self.completed_at is None:
            return None
        delta = self.completed_at - self.started_at
        return delta.total_seconds() / 3600
