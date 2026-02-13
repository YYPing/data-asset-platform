import hashlib
from io import BytesIO
from fastapi.testclient import TestClient
from tests.conftest import TestingSessionLocal
from app.main import app

client = TestClient(app)


def _setup_and_submit():
    db = TestingSessionLocal()
    from app.models.organization import Organization
    from app.models.user import User
    from app.core.security import get_password_hash

    org = Organization(name="材料测试公司", org_type="enterprise")
    db.add(org)
    db.commit()
    db.refresh(org)

    user = User(username="mat_holder", hashed_password=get_password_hash("pass"), role="data_holder", org_id=org.id)
    db.add(user)
    db.commit()
    db.close()

    token = client.post("/api/v1/auth/login", data={"username": "mat_holder", "password": "pass"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    asset = client.post("/api/v1/assets", json={"name": "材料测试资产"}, headers=headers).json()
    submit = client.post(f"/api/v1/stages/{asset['id']}/submit", headers=headers).json()
    return token, submit["id"]


def test_upload_material():
    token, record_id = _setup_and_submit()
    headers = {"Authorization": f"Bearer {token}"}
    content = b"test file content"
    resp = client.post(
        f"/api/v1/materials/upload/{record_id}",
        files={"file": ("test.pdf", BytesIO(content), "application/pdf")},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["file_name"] == "test.pdf"
    assert data["hash_sha256"] == hashlib.sha256(content).hexdigest()
    assert data["version"] == 1


def test_upload_version_control():
    token, record_id = _setup_and_submit()
    headers = {"Authorization": f"Bearer {token}"}

    client.post(f"/api/v1/materials/upload/{record_id}",
                files={"file": ("report.pdf", BytesIO(b"v1"), "application/pdf")}, headers=headers)
    resp = client.post(f"/api/v1/materials/upload/{record_id}",
                       files={"file": ("report.pdf", BytesIO(b"v2"), "application/pdf")}, headers=headers)
    assert resp.json()["version"] == 2


def test_list_materials():
    token, record_id = _setup_and_submit()
    headers = {"Authorization": f"Bearer {token}"}

    client.post(f"/api/v1/materials/upload/{record_id}",
                files={"file": ("a.pdf", BytesIO(b"aaa"), "application/pdf")}, headers=headers)
    client.post(f"/api/v1/materials/upload/{record_id}",
                files={"file": ("b.pdf", BytesIO(b"bbb"), "application/pdf")}, headers=headers)

    resp = client.get(f"/api/v1/materials/{record_id}", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2
