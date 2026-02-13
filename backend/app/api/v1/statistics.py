from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User, Role
from app.models.asset import DataAsset, AssetStage
from app.models.organization import Organization

router = APIRouter(prefix="/api/v1/statistics", tags=["统计分析"])


class StageDistribution(BaseModel):
    stage: str
    count: int


class CityStats(BaseModel):
    total_assets: int
    stage_distribution: List[StageDistribution]
    org_count: int


class HolderStats(BaseModel):
    total_assets: int
    stage_distribution: List[StageDistribution]
    valued_count: int
    total_valuation: float


@router.get("/city", response_model=CityStats)
def city_statistics(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    total = db.query(func.count(DataAsset.id)).scalar()
    org_count = db.query(func.count(Organization.id)).scalar()

    stage_dist = db.query(
        DataAsset.current_stage, func.count(DataAsset.id)
    ).group_by(DataAsset.current_stage).all()

    return CityStats(
        total_assets=total,
        stage_distribution=[StageDistribution(stage=s.value if hasattr(s, 'value') else str(s), count=c) for s, c in stage_dist],
        org_count=org_count,
    )


@router.get("/holder", response_model=HolderStats)
def holder_statistics(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(DataAsset)
    if user.role == Role.DATA_HOLDER and user.org_id:
        query = query.filter(DataAsset.org_id == user.org_id)

    total = query.count()
    stage_dist = query.with_entities(
        DataAsset.current_stage, func.count(DataAsset.id)
    ).group_by(DataAsset.current_stage).all()

    valued = query.filter(DataAsset.valuation_amount.isnot(None)).count()
    total_val = query.with_entities(func.coalesce(func.sum(DataAsset.valuation_amount), 0)).scalar()

    return HolderStats(
        total_assets=total,
        stage_distribution=[StageDistribution(stage=s.value if hasattr(s, 'value') else str(s), count=c) for s, c in stage_dist],
        valued_count=valued,
        total_valuation=float(total_val),
    )
