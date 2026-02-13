from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register():
    resp = client.post("/api/v1/auth/register", json={
        "username": "holder1",
        "password": "test123",
        "real_name": "张三",
        "role": "data_holder",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "holder1"
    assert data["role"] == "data_holder"


def test_register_duplicate():
    client.post("/api/v1/auth/register", json={
        "username": "dup_user", "password": "test123", "role": "admin",
    })
    resp = client.post("/api/v1/auth/register", json={
        "username": "dup_user", "password": "test123", "role": "admin",
    })
    assert resp.status_code == 400


def test_login():
    client.post("/api/v1/auth/register", json={
        "username": "login_user", "password": "mypass", "role": "registry_center",
    })
    resp = client.post("/api/v1/auth/login", data={
        "username": "login_user", "password": "mypass",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["role"] == "registry_center"


def test_login_wrong_password():
    client.post("/api/v1/auth/register", json={
        "username": "wrong_pw", "password": "correct", "role": "admin",
    })
    resp = client.post("/api/v1/auth/login", data={
        "username": "wrong_pw", "password": "incorrect",
    })
    assert resp.status_code == 401


def test_get_me():
    client.post("/api/v1/auth/register", json={
        "username": "me_user", "password": "pass123", "role": "assessor",
    })
    login_resp = client.post("/api/v1/auth/login", data={
        "username": "me_user", "password": "pass123",
    })
    token = login_resp.json()["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "me_user"


def test_get_me_no_token():
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
