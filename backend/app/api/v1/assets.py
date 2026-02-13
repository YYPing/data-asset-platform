from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User, Role
from app.models.asset import AssetStage
from app.services.asset_service import create_asset, list_assets, get_asset

router = APIRouter(prefix="/api/v1/assets", tags=["资产管理"])


class AssetCreate(BaseModel):
    name: str
    description: str = ""
    asset_type: Optional[str] = None
    data_classification: Optional[str] = None


class AssetOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    org_id: int
    current_stage: AssetStage
    asset_type: Optional[str] = None
    data_classification: Optional[str] = None
    valuation_amount: Optional[float] = None
    accounting_type: Optional[str] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


@router.post("", response_model=AssetOut)
def create(data: AssetCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role not in (Role.DATA_HOLDER, Role.ADMIN):
        raise HTTPException(status_code=403, detail="只有数据持有方或管理员可以创建资产")
    if not user.org_id:
        raise HTTPException(status_code=400, detail="用户未关联组织")
    asset = create_asset(db, data.name, data.description, user, data.asset_type, data.data_classification)
    return asset


@router.get("", response_model=List[AssetOut])
def list_all(stage: Optional[str] = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_assets(db, user, stage)


@router.get("/{asset_id}", response_model=AssetOut)
def detail(asset_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    asset = get_asset(db, asset_id, user)
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在或无权访问")
    return asset
