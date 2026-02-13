from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User, Role
from app.models.audit import AuditLog

router = APIRouter(prefix="/api/v1/audit", tags=["审计日志"])


class AuditLogOut(BaseModel):
    id: int
    user_id: int
    username: str
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    detail: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("", response_model=List[AuditLogOut])
def list_audit_logs(
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    user_id: Optional[int] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (Role.ADMIN, Role.REGISTRY_CENTER, Role.REGULATOR):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="无权查看审计日志")

    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
