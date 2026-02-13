from functools import wraps
from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def log_audit(db: Session, user_id: int, username: str, action: str, resource_type: str, resource_id: int = None, detail: str = "", ip_address: str = ""):
    """记录审计日志（只INSERT，不可修改删除）"""
    log = AuditLog(
        user_id=user_id,
        username=username,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        detail=detail,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()
