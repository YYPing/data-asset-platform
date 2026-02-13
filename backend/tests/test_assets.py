import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_assets.db"
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


def _create_org_and_user(role="data_holder"):
    """Helper: create org, register user with org_id, login, return token."""
    db = TestingSessionLocal()
    from app.models.organization import Organization
    org = Organization(name="测试公司", org_type="enterprise")
    db.add(org)
    db.commit()
    db.refresh(org)

    from app.models.user import User, Role
    from app.core.security import get_password_hash
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
