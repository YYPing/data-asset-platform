from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.stage import StageRecord
from app.models.material import StageMaterial
from app.services.material_service import save_material

router = APIRouter(prefix="/api/v1/materials", tags=["材料管理"])


class MaterialOut(BaseModel):
    id: int
    stage_record_id: int
    file_name: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    hash_sha256: str
    version: int
    uploaded_by: Optional[int] = None

    class Config:
        from_attributes = True


@router.post("/upload/{stage_record_id}", response_model=MaterialOut)
async def upload(
    stage_record_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = db.query(StageRecord).filter(StageRecord.id == stage_record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="阶段记录不存在")

    file_bytes = await file.read()
    file_type = file.content_type or ""
    material = save_material(db, stage_record_id, file.filename, file_bytes, file_type, user.id)
    return material


@router.get("/{stage_record_id}", response_model=List[MaterialOut])
def list_materials(stage_record_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    materials = db.query(StageMaterial).filter(
        StageMaterial.stage_record_id == stage_record_id
    ).order_by(StageMaterial.created_at.desc()).all()
    return materials
