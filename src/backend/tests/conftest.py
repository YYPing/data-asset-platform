"""
测试配置文件
"""
import os
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.core.security import create_access_token

# 使用内存SQLite数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token() -> str:
    """生成管理员Token"""
    return create_access_token(
        data={"sub": "admin", "role": "admin"}
    )


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """管理员请求头"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def manager_token() -> str:
    """生成资产管理员Token"""
    return create_access_token(
        data={"sub": "manager", "role": "asset_manager"}
    )


@pytest.fixture
def manager_headers(manager_token: str) -> dict:
    """资产管理员请求头"""
    return {"Authorization": f"Bearer {manager_token}"}


@pytest.fixture
def viewer_token() -> str:
    """生成普通用户Token"""
    return create_access_token(
        data={"sub": "viewer", "role": "viewer"}
    )


@pytest.fixture
def viewer_headers(viewer_token: str) -> dict:
    """普通用户请求头"""
    return {"Authorization": f"Bearer {viewer_token}"}
