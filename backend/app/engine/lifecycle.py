from typing import Optional
from sqlalchemy.orm import Session

from app.models.asset import DataAsset, AssetStage, STAGE_ORDER
from app.models.stage import StageRecord, StageStatus


class LifecycleError(Exception):
    pass


def get_next_stage(current: AssetStage) -> Optional[AssetStage]:
    idx = STAGE_ORDER.index(current)
    if idx + 1 < len(STAGE_ORDER):
        return STAGE_ORDER[idx + 1]
    return None  # 已在运营阶段


def get_prev_stage(current: AssetStage) -> Optional[AssetStage]:
    idx = STAGE_ORDER.index(current)
    if idx > 0:
        return STAGE_ORDER[idx - 1]
    return None


def submit_stage(db: Session, asset: DataAsset, user_id: int) -> StageRecord:
    """提交当前阶段审批"""
    existing = db.query(StageRecord).filter(
        StageRecord.asset_id == asset.id,
        StageRecord.stage == asset.current_stage,
        StageRecord.status == StageStatus.SUBMITTED,
    ).first()
    if existing:
        raise LifecycleError("当前阶段已提交审批，请等待审批结果")

    record = StageRecord(
        asset_id=asset.id,
        stage=asset.current_stage,
        status=StageStatus.SUBMITTED,
        submitted_by=user_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def approve_stage(db: Session, record: StageRecord, approver_id: int) -> StageRecord:
    """审批通过，自动推进到下一阶段"""
    if record.status != StageStatus.SUBMITTED:
        raise LifecycleError("只能审批已提交的阶段记录")

    record.status = StageStatus.APPROVED
    record.approved_by = approver_id

    asset = db.query(DataAsset).filter(DataAsset.id == record.asset_id).first()
    next_stage = get_next_stage(asset.current_stage)
    if next_stage:
        asset.current_stage = next_stage

    db.commit()
    db.refresh(record)
    return record


def reject_stage(db: Session, record: StageRecord, approver_id: int, reason: str = "") -> StageRecord:
    """退回阶段"""
    if record.status != StageStatus.SUBMITTED:
        raise LifecycleError("只能退回已提交的阶段记录")

    record.status = StageStatus.REJECTED
    record.approved_by = approver_id
    record.reject_reason = reason
    db.commit()
    db.refresh(record)
    return record
