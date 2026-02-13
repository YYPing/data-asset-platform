from fastapi.testclient import TestClient
from tests.conftest import TestingSessionLocal
from app.main import app

client = TestClient(app)


def _create_org_and_user(role="data_holder"):
    db = TestingSessionLocal()
    from app.models.organization import Organization
    from app.models.user import User
    from app.core.security import get_password_hash

    org = Organization(name="测试公司", org_type="enterprise")
    db.add(org)
    db.commit()
    db.refresh(org)

    user = User(
        username=f"user_{role}",
        hashed_password=get_password_hash("pass123"),
        role=role,
        org_id=org.id,
    )
    db.add(user)
    db.commit()
    db.close()

    resp = client.post("/api/v1/auth/login", data={"username": f"user_{role}", "password": "pass123"})
    return resp.json()["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_asset():
    token = _create_org_and_user("data_holder")
    resp = client.post("/api/v1/assets", json={"name": "客户数据集", "description": "CRM数据"}, headers=_auth_header(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "客户数据集"
    assert data["current_stage"] == "resource_inventory"


def test_create_asset_forbidden_for_assessor():
    token = _create_org_and_user("assessor")
    resp = client.post("/api/v1/assets", json={"name": "test"}, headers=_auth_header(token))
    assert resp.status_code == 403


def test_list_assets():
    token = _create_org_and_user("data_holder")
    client.post("/api/v1/assets", json={"name": "资产A"}, headers=_auth_header(token))
    client.post("/api/v1/assets", json={"name": "资产B"}, headers=_auth_header(token))
    resp = client.get("/api/v1/assets", headers=_auth_header(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_asset_detail():
    token = _create_org_and_user("data_holder")
    create_resp = client.post("/api/v1/assets", json={"name": "详情测试"}, headers=_auth_header(token))
    asset_id = create_resp.json()["id"]
    resp = client.get(f"/api/v1/assets/{asset_id}", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["name"] == "详情测试"


def test_get_asset_not_found():
    token = _create_org_and_user("data_holder")
    resp = client.get("/api/v1/assets/9999", headers=_auth_header(token))
    assert resp.status_code == 404
