from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.asset import DataAsset, AssetStage
from app.models.user import User, Role


def create_asset(db: Session, name: str, description: str, user: User, asset_type: str = None, data_classification: str = None) -> DataAsset:
    asset = DataAsset(
        name=name,
        description=description,
        org_id=user.org_id,
        current_stage=AssetStage.RESOURCE_INVENTORY,
        asset_type=asset_type,
        data_classification=data_classification,
        created_by=user.id,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def list_assets(db: Session, user: User, stage: Optional[str] = None) -> List[DataAsset]:
    query = db.query(DataAsset)
    # RBAC: 持有方只能看自己组织的资产
    if user.role == Role.DATA_HOLDER:
        query = query.filter(DataAsset.org_id == user.org_id)
    if stage:
        query = query.filter(DataAsset.current_stage == stage)
    return query.order_by(DataAsset.created_at.desc()).all()


def get_asset(db: Session, asset_id: int, user: User) -> Optional[DataAsset]:
    asset = db.query(DataAsset).filter(DataAsset.id == asset_id).first()
    if not asset:
        return None
    # RBAC: 持有方只能看自己组织的资产
    if user.role == Role.DATA_HOLDER and asset.org_id != user.org_id:
        return None
    return asset
