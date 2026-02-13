import hashlib
import os
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.material import StageMaterial
from app.models.stage import StageRecord


def compute_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def save_material(
    db: Session,
    stage_record_id: int,
    file_name: str,
    file_bytes: bytes,
    file_type: str,
    uploaded_by: int,
) -> StageMaterial:
    hash_value = compute_sha256(file_bytes)

    # Version control: check existing file with same name
    existing = db.query(StageMaterial).filter(
        StageMaterial.stage_record_id == stage_record_id,
        StageMaterial.file_name == file_name,
    ).order_by(StageMaterial.version.desc()).first()
    version = (existing.version + 1) if existing else 1

    # Save file to disk
    upload_dir = os.path.join(settings.UPLOAD_DIR, str(stage_record_id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"v{version}_{file_name}")
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    material = StageMaterial(
        stage_record_id=stage_record_id,
        file_name=file_name,
        file_path=file_path,
        file_size=len(file_bytes),
        file_type=file_type,
        hash_sha256=hash_value,
        version=version,
        uploaded_by=uploaded_by,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material
