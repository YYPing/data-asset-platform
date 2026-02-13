from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User, Role
from app.models.asset import DataAsset, AssetStage
from app.models.stage import StageRecord, StageStatus
from app.engine.lifecycle import submit_stage, approve_stage, reject_stage, LifecycleError

router = APIRouter(prefix="/api/v1/stages", tags=["生命周期"])


class StageRecordOut(BaseModel):
    id: int
    asset_id: int
    stage: AssetStage
    status: StageStatus
    submitted_by: Optional[int] = None
    approved_by: Optional[int] = None
    reject_reason: Optional[str] = None

    class Config:
        from_attributes = True


class RejectInput(BaseModel):
    reason: str = ""


@router.post("/{asset_id}/submit", response_model=StageRecordOut)
def submit(asset_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    asset = db.query(DataAsset).filter(DataAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    try:
        record = submit_stage(db, asset, user.id)
        return record
    except LifecycleError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/records/{record_id}/approve", response_model=StageRecordOut)
def approve(record_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role not in (Role.REGISTRY_CENTER, Role.ADMIN):
        raise HTTPException(status_code=403, detail="只有登记中心或管理员可以审批")
    record = db.query(StageRecord).filter(StageRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="阶段记录不存在")
    try:
        return approve_stage(db, record, user.id)
    except LifecycleError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/records/{record_id}/reject", response_model=StageRecordOut)
def reject(record_id: int, data: RejectInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role not in (Role.REGISTRY_CENTER, Role.ADMIN):
        raise HTTPException(status_code=403, detail="只有登记中心或管理员可以退回")
    record = db.query(StageRecord).filter(StageRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="阶段记录不存在")
    try:
        return reject_stage(db, record, user.id, data.reason)
    except LifecycleError as e:
        raise HTTPException(status_code=400, detail=str(e))
