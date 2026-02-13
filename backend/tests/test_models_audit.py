from app.models.audit import AuditLog
from app.models.approval import ApprovalRecord


def test_audit_log_model():
    log = AuditLog(user_id=1, username="admin", action="create", resource_type="asset", resource_id=1)
    assert log.action == "create"
    assert log.resource_type == "asset"


def test_approval_record_model():
    record = ApprovalRecord(stage_record_id=1, action="approve", operator_id=1)
    assert record.action == "approve"
