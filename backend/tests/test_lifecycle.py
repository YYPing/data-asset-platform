import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_lifecycle.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    from app.models.organization import Organization  # noqa
    from app.models.user import User  # noqa
    from app.models.asset import DataAsset  # noqa
    from app.models.stage import StageRecord  # noqa
    from app.models.material import StageMaterial  # noqa
    from app.models.audit import AuditLog  # noqa
    from app.models.approval import ApprovalRecord  # noqa
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def _setup_users():
    """Create org + holder + registry users, return their tokens."""
    db = TestingSessionLocal()
    from app.models.organization import Organization
    from app.models.user import User
    from app.core.security import get_password_hash

    org = Organization(name="测试公司", org_type="enterprise")
    db.add(org)
    db.commit()
    db.refresh(org)

    holder = User(username="holder", hashed_password=get_password_hash("pass"), role="data_holder", org_id=org.id)
    registry = User(username="registry", hashed_password=get_password_hash("pass"), role="registry_center", org_id=org.id)
    db.add_all([holder, registry])
    db.commit()
    db.close()

    h_token = client.post("/api/v1/auth/login", data={"username": "holder", "password": "pass"}).json()["access_token"]
    r_token = client.post("/api/v1/auth/login", data={"username": "registry", "password": "pass"}).json()["access_token"]
    return h_token, r_token


def _h(token):
    return {"Authorization": f"Bearer {token}"}


def test_submit_stage():
    h_token, _ = _setup_users()
    asset = client.post("/api/v1/assets", json={"name": "测试资产"}, headers=_h(h_token)).json()
    resp = client.post(f"/api/v1/stages/{asset['id']}/submit", headers=_h(h_token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "submitted"
    assert resp.json()["stage"] == "resource_inventory"


def test_approve_advances_stage():
    h_token, r_token = _setup_users()
    asset = client.post("/api/v1/assets", json={"name": "推进测试"}, headers=_h(h_token)).json()
    submit_resp = client.post(f"/api/v1/stages/{asset['id']}/submit", headers=_h(h_token))
    record_id = submit_resp.json()["id"]

    resp = client.post(f"/api/v1/stages/records/{record_id}/approve", headers=_h(r_token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"

    # Check asset advanced to next stage
    asset_resp = client.get(f"/api/v1/assets/{asset['id']}", headers=_h(h_token))
    assert asset_resp.json()["current_stage"] == "asset_inventory"


def test_reject_stage():
    h_token, r_token = _setup_users()
    asset = client.post("/api/v1/assets", json={"name": "退回测试"}, headers=_h(h_token)).json()
    submit_resp = client.post(f"/api/v1/stages/{asset['id']}/submit", headers=_h(h_token))
    record_id = submit_resp.json()["id"]

    resp = client.post(f"/api/v1/stages/records/{record_id}/reject", json={"reason": "材料不完整"}, headers=_h(r_token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "rejected"
    assert resp.json()["reject_reason"] == "材料不完整"

    # Asset stays at same stage
    asset_resp = client.get(f"/api/v1/assets/{asset['id']}", headers=_h(h_token))
    assert asset_resp.json()["current_stage"] == "resource_inventory"


def test_holder_cannot_approve():
    h_token, _ = _setup_users()
    asset = client.post("/api/v1/assets", json={"name": "权限测试"}, headers=_h(h_token)).json()
    submit_resp = client.post(f"/api/v1/stages/{asset['id']}/submit", headers=_h(h_token))
    record_id = submit_resp.json()["id"]

    resp = client.post(f"/api/v1/stages/records/{record_id}/approve", headers=_h(h_token))
    assert resp.status_code == 403


def test_full_lifecycle_3_stages():
    """Test advancing through first 3 stages."""
    h_token, r_token = _setup_users()
    asset = client.post("/api/v1/assets", json={"name": "全流程测试"}, headers=_h(h_token)).json()

    expected_stages = ["asset_inventory", "usage_scenario", "compliance_assessment"]
    for next_stage in expected_stages:
        submit_resp = client.post(f"/api/v1/stages/{asset['id']}/submit", headers=_h(h_token))
        record_id = submit_resp.json()["id"]
        client.post(f"/api/v1/stages/records/{record_id}/approve", headers=_h(r_token))
        asset_resp = client.get(f"/api/v1/assets/{asset['id']}", headers=_h(h_token))
        assert asset_resp.json()["current_stage"] == next_stage
